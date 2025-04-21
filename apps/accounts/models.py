# python imports
import datetime
import random
import base64

# Django

from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.timezone import now, timezone
from django.db.models import Avg, Q
from django.core.cache import cache
from django.core.exceptions import ValidationError

# third parties
from .utils import _validate_photo
from cloudinary.models import CloudinaryField
import cloudinary

# local
from accounts.manager import CustomUserManager
from apps.services.models import Service
from apps.category.models import Skill
from commons.mixins import ModelMixin
from .enums import EVENTTYPES, UserRoles, GENDERS
# Create your models here.



class CustomUser(AbstractBaseUser, PermissionsMixin, ModelMixin):
    """
    Custom user model that extends Django's AbstractBaseUser and PermissionsMixin.

    This model replaces Django's default User model and supports:
    - Email-based authentication
    - Role-based user management (Normal User, Skilled User, Staff, Admin)
    - Account approval system for skilled users
    - Cloudinary profile picture storage
    - Foreign key relationships to Country and State

    Attributes:
        email (EmailField): Unique email address used for authentication.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        date_joined (DateTimeField): Timestamp when the user registered.
        is_active (BooleanField): Indicates whether the account is active. Activated via email.
        is_staff (BooleanField): Grants access to staff-level admin functionalities.
        is_superuser (BooleanField): Grants full admin privileges.
        profile_picture (CloudinaryField): Stores the user's profile image on Cloudinary.
        role (CharField): Defines the user's role (Normal, Skilled, Staff, Admin).
        is_approved (BooleanField): Approval flag for skilled users (set by an admin). Only applicable for skilled users.
        country (ForeignKey): Links the user to a country.
        state (ForeignKey): Links the user to a state.

    Methods:
        __str__: Returns the user's email address as a string representation.
    """
     
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    # profile_picture = CloudinaryField('image', null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRoles.choices, default=UserRoles.CLIENT_USER)
    is_approved = models.BooleanField(default=False)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDERS.choices)

    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
    


class OTPVerification(ModelMixin):
    """
    Model to store OTP for user verification.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="otp_verification")
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    last_sent_at = models.DateTimeField(null=True, blank=True)


    @classmethod
    def get_user_otp(cls, email):
        """
        Get the OTP for a given user.
        """
        try:
            user = OTPVerification.objects.select_related("user").get(user__email=email)
            return user
        
        except cls.DoesNotExist:
            return None
        
    @classmethod
    def generate_otp(cls, user):
        """
        Generate a new OTP for a given user. If an OTP already exists, update it.
        """
        otp_instance, created = cls.objects.get_or_create(user=user)
        otp_instance.otp = str(random.randint(100000, 999999))
        otp_instance.created_at = now()  # Update timestamp when OTP is refreshed
        otp_instance.last_sent_at = now()
        print("OTP", otp_instance, otp_instance.otp)
        otp_instance.save(update_fields=['otp', 'created_at', 'last_sent_at'])
        OTPLog.objects.create(user=user, event_type='sent')
        return otp_instance.otp  # Return the OTP for further processing (e.g., email sending)

    @classmethod
    def is_expired(cls, user, expiry_minutes=10):
        """
        Check if the OTP for a user has expired.
        Default expiration time is 10 minutes.
        """
        try:
            otp_instance = cls.objects.get(user=user)
            expiry_time = otp_instance.created_at + datetime.timedelta(minutes=expiry_minutes)
            return now() > expiry_time
        except cls.DoesNotExist:
            return True  # If no OTP exists, consider it expired

    @classmethod
    def verify_otp(cls, user, otp):
        """
        Verify the OTP for a user and mark them as verified.
        """
        otp_log = OTPLog.create_otp_log(user=user)
        try:
            otp_instance = cls.objects.get(user=user)

            if cls.is_expired(user):
                return False, "OTP has expired."

            if otp_instance.otp != otp:
                
                return False, "Invalid OTP."

            otp_instance.is_verified = True
            otp_instance.otp = None  # Clear OTP after successful verification
            otp_instance.save(update_fields=['is_verified', 'otp'])

            user.is_active = True  # Update user verification status
            user.save(update_fields=['is_active'])
            
            OTPLog.update_otp_log(otp_log.id, EVENTTYPES.VERIFIED)

            return True, "OTP verified successfully."

        except cls.DoesNotExist:
            return False, "OTP not found. Please request a new OTP."

    @classmethod
    def can_resend_otp(cls, user, cooldown_minutes=2):
        """
        Check if the user can request a new OTP.
        """
        otp_log = OTPLog.create_otp_log(user, 'failed')
        try:
            otp_instance = cls.objects.get(user=user)
            if otp_instance.last_sent_at and (now() - otp_instance.last_sent_at).seconds < cooldown_minutes * 60:
                return False  # OTP was sent too recently

            OTPLog.update_otp_log(otp_log.id, 'success')
            return True
        except cls.DoesNotExist:
            return True
        
    def __str__(self):
        return f"OTP for {self.user.email} - Verified: {self.is_verified}"




class ExpertUserProfile(ModelMixin):
    """
    Profile for skilled users (freelancers).
    """
    expert = models.OneToOneField("CustomUser", on_delete=models.CASCADE, related_name="expert_profile", null=True, blank=True) #TODO: remove the null later after clearing the db
    skills = models.ManyToManyField(Skill, related_name="experts")
    bio = models.TextField(blank=True, null=True)
    rating = models.FloatField(default=0.0)  # 
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    completed_services = models.PositiveIntegerField(default=0)
    portfolio = models.JSONField(default=list, blank=True, null=True)  
    is_profile_complete = models.BooleanField(default=False)  # 
    has_agreed_to_terms = models.BooleanField(default=False)  # 
    title = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField(default=0)
    availability = models.BooleanField(default=True)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    profile_picture = CloudinaryField('image', null=True, blank=True)
    completion_percentage = models.IntegerField(default=0)  


    # def __str__(self):
    #     return f"{self.expert.email} - {self.rating}⭐"
    
    @classmethod
    def get_fields(cls):
        """
        Returns a list of all field names in the model.
        """
        return [
            "expert__first_name",
            "expert__last_name",
            "expert__email",
            "expert__gender",
            "expert__country",
            "profile_picture",
            "skills",
            "bio",
            "rating",
            "phone_number",
            "completed_services",
            # "price",
            "portfolio",
            "is_profile_complete",
            "has_agreed_to_terms",
            "title",
            "years_of_experience",
            "availability",
            "total_earnings",
            "reviews_count"

        ]
        # return [field.name for field in cls._meta.fields]
    
    @classmethod
    def create_profile(cls, user, **kwargs):
        """
        Create and return a new expert profile for the given user.
        """
        return cls.objects.create(expert=user, **kwargs)

    # @classmethod
    # def update_profile(cls, user, **kwargs):
    #     """
    #     Update the existing expert profile for the user with given kwargs.
    #     """
    #     profile = cls.objects.filter(user=user).update(**kwargs)
    #     return profile
    @classmethod
    def update_profile(cls, user_id, **kwargs):
        """
        Updates an expert profile for the given user ID, including skills, services, and portfolio.
        Also updates profile completion percentage.
        """
        with transaction.atomic():
            # Fetch profile and ensure user exists
            profile = cls.objects.select_related("expert").filter(expert_id=user_id).first()
            if not profile or not profile.expert:
                return None  

            # Extract related fields for CustomUser
            user_fields = ["first_name", "last_name", "gender", "email", "country"]
            user_data = {field: kwargs.pop(field) for field in user_fields if field in kwargs}

            # Extract related fields for ExpertUserProfile
            skills = kwargs.pop("skills", None)
            services = kwargs.pop("services", None)
            portfolio = kwargs.pop("portfolio", None)

            print("PORTFOLIO========", portfolio)

            # Update CustomUser fields
            if user_data:
                CustomUser.objects.filter(id=profile.expert.id).update(**user_data)

            # Update profile fields
            if kwargs:
                cls.objects.filter(id=profile.id).update(**kwargs)

            # Update ManyToManyField (skills)
            
            if skills:
                skill_ids = Skill.objects.filter(id__in=[s for s in skills])
                profile.skills.set(skill_ids)

            # Bulk update/create services
            if services:
                service_objs = [
                    Service(
                        expert_id=profile.id,
                        skill_id=s["skillId"],
                        title=s["title"],
                        description=s["description"],
                        price=s["price"],
                        is_active=s.get("isActive", True),
                    )
                    for s in services
                ]
                Service.objects.bulk_create(service_objs)

            # Handle portfolio (validate and update JSONField)
            if portfolio:
                try:
                    validated_portfolio = [
                        {"title": item["title"], "image": item["image"]}
                        for item in portfolio if "title" in item and "image" in item and item["image"]
                    ]
                    profile.portfolio = validated_portfolio
                    profile.save(update_fields=["portfolio"])
                except Exception as e:
                    print("E", e)
                    pass  # Avoid breaking the update if portfolio processing fails
            
            # Update profile completion percentage
            completion_percentage = cls.update_completion(profile)

            return profile  # Return updated profile object
    

    @classmethod
    def update_photo(cls, user_id, photo=None):
        """
        Update profile photo.
        If photo is None, removes the current photo.
        """
        if not user_id:
            return None 
        try:
            profile = cls.objects.get(expert_id=user_id)
            
            # Validate photo if provided
            if photo:
                _validate_photo(photo)
                profile.profile_picture = photo
            else:
                # Remove existing photo if any
                if profile.profile_picture:
                    public_id = profile.profile_picture.public_id
                    if public_id:
                        cloudinary.uploader.destroy(public_id)
                    profile.profile_picture = None
            
            cls.update_completion(profile)
            profile.save()
            
            return profile
            
        except cls.DoesNotExist:
            return None



    @classmethod
    def get_expert_profile(cls, **kwargs):
        """
        Retrieve the ClientProfile for the given user.
        """
        obj = kwargs.pop("obj", None)
        try:
            if obj:
                profile = cls.objects.get(**kwargs)
            else:
                profile = cls.objects.filter(**kwargs).values(*cls.get_fields())[0]
        except cls.DoesNotExist:
            profile = None
        return profile


    @classmethod
    def update_completion(cls, profile):
        """Update expert profile completion percentage and status."""
        if not profile:
            return 0
        
        # Fields required for a complete expert profile
        required_fields = ["profile_picture", "bio", "title", "years_of_experience", "skills", "portfolio"]

        # Count completed fields in ExpertUserProfile
        completed = sum(
            1 for field in required_fields if getattr(profile, field, None) not in [None, "", []]
        )

        # Check required fields in CustomUser (linked via OneToOneField)
        user_fields = ["first_name", "last_name", "gender", "country"]
        completed += sum(1 for field in user_fields if getattr(profile.expert, field, None) not in [None, ""])

        # Total fields count
        total_fields = len(required_fields) + len(user_fields)

        # Calculate percentage
        completion_percentage = int((completed / total_fields) * 100) if total_fields > 0 else 0

        # Update and save profile completion status
        cls.objects.filter(id=profile.id).update(
            completion_percentage=completion_percentage,
            is_profile_complete=completion_percentage >= 80
        )

        return completion_percentage

    @classmethod
    def top_experts(cls, limit=10, order_by_field="rating"):
        """
        Returns the top experts, optimized with caching.
        """
        cache_key = f"top_experts_{order_by_field}_{limit}"
        top_experts = cache.get(cache_key)

        if not top_experts:
            top_experts = (
                cls.objects
                .select_related('expert')
                .prefetch_related('skills')
                .annotate(avg_rating=Avg('rating'))
                .order_by(f"-{order_by_field}")[:limit]
                .values('expert__first_name', 'rating', 'completed_services', 'total_earnings', 'reviews_count', 'skills__name', 'profile_picture')
            )
            cache.set(cache_key, list(top_experts), timeout=3600)  # Cache for 1 hour

        return top_experts
    

    @classmethod
    def fetch_experts(cls, conditions=None, count=500):
        queryset = cls.objects.filter(conditions).select_related(
            "expert", "expert__country"
        ).prefetch_related("skills").order_by("-pk")[:count]
        return queryset
    
    

    # def save(self, *args, **kwargs):
    #     """
    #     Override save method to update profile completion status automatically.
    #     """
    #     self.update_profile_completion_status()
    #     super().save(*args, **kwargs)
    

# TODO: to be moved to general.modelss
class Country(ModelMixin):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    

class State(ModelMixin):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class OTPLog(ModelMixin):
    """
    Log OTP events (sent, verified, failed, etc.).
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='otp_logs'
    )
    event_type = models.CharField(max_length=50, choices=EVENTTYPES, default=EVENTTYPES.FAILED)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.event_type} at {self.timestamp}"
    

    @classmethod
    def create_otp_log(cls, user, event_type=EVENTTYPES.FAILED):
        """
        Create a new OTP log entry for the user.
        """
        print("CREATE ", user)
        return cls.objects.create(user=user, event_type=event_type)
    
    @classmethod
    def get_otp_logs(cls, user):
        """
        Get all OTP logs for a user.
        """
        return cls.objects.filter(user=user)
    
    @classmethod
    def update_otp_log(cls, otp_log_id, event_type):
        """
        Update the OTP log for a user.
        """
        try:
            otp_log = cls.objects.filter(id=otp_log_id).update(event_type=event_type)
            return otp_log
    
        except cls.DoesNotExist:
            return None
        



    