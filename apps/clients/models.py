from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from accounts.models import ModelMixin
from accounts.models import CustomUser
from accounts.utils import _validate_photo
from django.utils.timezone import now
from django.db.models import Count, Q, Sum
from apps.services.models import ServiceRequest
from apps.services.enums import StatusChoices
# get user model
from django.contrib.auth import get_user_model
import cloudinary


User = get_user_model()

class ClientProfile(ModelMixin):
    """
    UserProfile model extends the CustomUser with additional personal details.

    Attributes:
        user (OneToOneField): Link to the CustomUser.
        phone_number (CharField): Contact number.
        address (TextField): Residential address.
        date_of_birth (DateField): Date of birth.
        bio (TextField, optional): Brief description or portfolio summary.
    """
    client = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    profile_picture = CloudinaryField('image', null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    has_agreed_to_terms = models.BooleanField(default=False)  # 
    is_profile_complete = models.BooleanField(default=False)  
    services_purchased = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    completion_percentage = models.IntegerField(default=0)  



    def __str__(self):
        return self.client.email
    

    @classmethod
    def get_fields(cls):
        fields  = [
            "client__first_name",
            "client__last_name",
            "client__email",
            "client__gender",
            "client__role",
            "bio",
            "address",
            "profile_picture",
        ]
        return fields

    @classmethod
    def create_profile(cls, user, **kwargs):
        """
        Create and return a new ClientProfile for the given user.
        """
        return cls.objects.create(client=user, **kwargs)

    @classmethod
    def update_profile(cls, user, **kwargs):
        """
        Update the existing ClientProfile for the user with given kwargs.
        """
        profile = cls.objects.filter(client=user).update(**kwargs)
        return profile
    
    @classmethod
    def update_client_profile(cls, user_id, **data):
        print("UPDATE CLIENT PROFILE", user_id, data)
        try:
            # Fetch the profile with related user
            profile = cls.objects.select_related('client').get(client_id=user_id)
            user = profile.client
            data.pop("country", None)
            if not user:
                return None

            # Separate user and profile fields
            user_fields = {'first_name', 'last_name', 'email', 'gender'}
            user_data = {k: v for k, v in data.items() if k in user_fields}
            profile_data = {k: v for k, v in data.items() if k not in user_fields}

            # Update user fields using update
            if user_data:
                CustomUser.objects.filter(id=user.id).update(**user_data)

            # Update profile fields using update
            if profile_data:
                cls.objects.filter(client_id=user_id).update(**profile_data)

            # Re-fetch profile after updates
            profile = cls.objects.select_related('client').get(client_id=user_id)

            # Update completion percentage
            cls.update_completion(profile)

            # Return fresh profile
            profile.refresh_from_db()
            return profile

        except cls.DoesNotExist:
            return None


    @classmethod
    def update_photo(cls, user_id, photo=None):
        """
        Update profile photo.
        If photo is None, removes the current photo.
        """
        try:
            profile = cls.objects.get(client_id=user_id)
            
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
    def get_client_profile(cls, **kwargs):
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
        """Update profile completion percentage and status."""
        if not profile:
            return 0
        
        completion_fields = ['profile_picture', 'bio']
        
        # Count completed fields in ClientProfile
        completed = sum(
            1 for field in completion_fields if getattr(profile, field, None) not in [None, ""]
        )

        
        if getattr(profile.client, "gender", None) not in [None, ""]:
            completed += 1  

        total_fields = len(completion_fields) + 1  # Include gender in total fields count

        # Calculate percentage
        completion_percentage = int((completed / total_fields) * 100) if total_fields > 0 else 0
        print("Completion Percentage:", completion_percentage)
        # Update and save profile changes
        up = cls.objects.filter(id=profile.id).update(
            completion_percentage=completion_percentage,
            is_profile_complete=completion_percentage >= 80
        )

        print("Profile Completion Updated:", up)
        

        return completion_percentage

    @classmethod
    def get_client_stats(cls, filters=None, recent_limit=3):
        total_service_requests = Q()
        total_service_requests_count = Count("id", filter=total_service_requests)
        
        active_service_requests_conditions = Q(
            service_request__status__in=[StatusChoices.PENDING,
                StatusChoices.IN_PROGRESS,
            ]
        )
        actove_service_requests_count = Count(
            "id", filter=active_service_requests_conditions
        )


        completed_service_requests_conditions = Q(
            service_request_status=StatusChoices.COMPLETED
        )
        completed_service_requests_count = Count(
            "id", filter=completed_service_requests_conditions
        )

        total_spent = Sum("total_cost", filter=completed_service_requests_conditions)

        service_request_summary = cls.objects.filter(filters).aaggregate(
            total_service_requests=total_service_requests_count,
            active_service_requests=actove_service_requests_count,
            completed_service_requests=completed_service_requests_count,
            total_spent=total_spent,
        )

        return service_request_summary
    


        