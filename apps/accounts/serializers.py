import uuid
from django.contrib.auth import get_user_model
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from cloudinary.utils import cloudinary_url

from rest_framework import serializers

from accounts.models import (
    CustomUser,
    OTPVerification
)

from accounts.tasks import send_approved_email_task, send_otp_email_task
from apps.accounts.enums import UserRoles
# from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
# from .models import UserProfile

User = get_user_model() #dynamically fetches the user model (whether default or custom)


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User's email address")
    password = serializers.CharField(help_text="User's password", write_only=True)
    first_name = serializers.CharField(help_text="User's first name")
    last_name = serializers.CharField(help_text="User's last name")
    role = serializers.ChoiceField(choices=UserRoles, help_text="User's role")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('email', 'role')


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer to resend OTP to the user's email.
    """
    email = serializers.EmailField()

    def validate(self, data):
        """
        Validate email and resend a new OTP.
        """
        email = data.get("email")

        try:
            otp_instance = OTPVerification.objects.select_related("user").get(user__email=email)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("User not found or OTP not generated.")

        
        if otp_instance.is_verified:
            raise serializers.ValidationError("User is already verified.")
        
        if not OTPVerification.can_resend_otp(otp_instance.user):
            raise serializers.ValidationError("You can request a new OTP in 2 minutes.")


        new_otp = OTPVerification.generate_otp(otp_instance.user)

        send_otp_email_task(email=otp_instance.user, first_name=otp_instance.user.first_name,  otp=new_otp)

        return {"message": "A new OTP has been sent to your email."}
    

class VerifyOTPSerializer(serializers.Serializer):
    """
    Serializer to verify OTP and activate user account.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        """
        Validate OTP and activate the user if correct.
        """
        email = data.get("email")
        otp = data.get("otp")

        try:
            user_otp = OTPVerification.get_user_otp(email=email)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("User not found or OTP not generated.")

        success, message = OTPVerification.verify_otp(user_otp.user, otp)

        if not success:
            raise serializers.ValidationError(message)

        return {"message": message}
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that ensures tokens are only issued if the user is verified.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        profile = getattr(user, "client_profile", None) or getattr(self.user, "expert_profile", None)
        role = getattr(user, "role")
        user_id = getattr(user, "id")
        data["profile_complete"] = getattr(profile, "is_profile_complete", False)
        data["has_agreed_to_terms"] = getattr(profile, "has_agreed_to_terms", False)
        data["role"] = role
        data["user_id"] =  user_id

        print("DATA", data)

        # Fetch user verification status from OTPVerification model
        if not hasattr(self.user, "otp_verification") or not self.user.otp_verification.is_verified:
            raise serializers.ValidationError("User is not verified. Please verify your account using the OTP sent to your email.")
        
        return data


class ApproveExpertUserSerializer(serializers.Serializer):
    """
    Serializer for approving skilled users.
    """
    id = serializers
    class Meta:
        model = User
        fields = ["id", "is_approved"]

    def update(self, instance, validated_data):
        if instance.role.lower() != "expert_user":
            raise serializers.ValidationError("Only skilled users can be approved.")

        if instance.is_approved:
            raise serializers.ValidationError("User is already approved.")

        instance.is_approved = True
        instance.save(update_fields=["is_approved"])

        # otp = OTPVerification.generate_otp(instance)
        # send_approved_email_task.delay(instance.email, instance.first_name, otp)

        return instance



class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting an OTP-based password reset.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Check if user exists and send OTP.
        """
        user = User.objects.get(email=value)
        if not user:
            raise serializers.ValidationError("No user found with this email.")

        #  Generate OTP for password reset
        otp = OTPVerification.generate_otp(user)
        print("OTP", otp)
        send_otp_email_task.delay(user.email, user.first_name, otp)
        return value


class PasswordResetVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying OTP and setting a new password.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate OTP and reset password.
        """
        user = User.objects.filter(email=data["email"]).first()
        if not user:
            raise serializers.ValidationError("User not found.")

        otp_instance = OTPVerification.get_user_otp(email=user.email)

        if not otp_instance or otp_instance.otp != data["otp"]:
            raise serializers.ValidationError("Invalid or expired OTP.")

        #  Reset password
        user.password = make_password(data["new_password"])
        user.save(update_fields=["password"])

        #  Clear OTP after successful reset
        otp_instance.otp = None
        otp_instance.is_verified = True
        otp_instance.save(update_fields=["otp", "is_verified"])

        return data


# class ClientProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClientProfile
#         fields = [
#             'id', 'profile_picture', 'address', 'date_of_birth', 
#             'bio', 'phone_number', 'total_spent', 
#             'is_profile_complete', 'completion_percentage'
#         ]
#         read_only_fields = ['total_spent', 'is_profile_complete', 'completion_percentage']

# class ClientProfileUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClientProfile
#         fields = [
#             'profile_picture', 'address', 'date_of_birth', 
#             'bio', 'phone_number'
#         ]
    
#     def update(self, instance, validated_data):
#         # Update the profile with validated data
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
        
#         # Calculate completion after update
#         instance.calculate_completion()
        
#         return instance


class ExpertFilterRequestSerializer(serializers.Serializer):
    # expert_id = serializers.UUIDField()
    skills = serializers.ListField(child=serializers.IntegerField(), required=False) 
    bio = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.FloatField(required=False)
    phone_number = serializers.CharField(allow_blank=True, required=False)
    completed_services = serializers.IntegerField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    portfolio = serializers.JSONField(required=False)
    is_profile_complete = serializers.BooleanField(required=False)
    has_agreed_to_terms = serializers.BooleanField(required=False)
    title = serializers.CharField(allow_blank=True, required=False)
    years_of_experience = serializers.IntegerField(required=False)
    availability = serializers.BooleanField(required=False)
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reviews_count = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(required=False)
    

class ExpertDetailRequestSerializer(serializers.Serializer):
    expert_id = serializers.UUIDField()


class ExpertProfileSetupResponseSerializer(serializers.Serializer):
    expert_id = serializers.UUIDField()
    first_name = serializers.CharField(source="expert.first_name")
    last_name = serializers.CharField(source="expert.last_name")
    email = serializers.EmailField(source="expert.email")
    role = serializers.EmailField(source="expert.role")
    skills = serializers.ListField(child=serializers.IntegerField(), required=False, source="skills.name") 
    bio = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.FloatField(required=False)
    phone_number = serializers.CharField(allow_blank=True, required=False)
    completed_services = serializers.IntegerField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    portfolio = serializers.JSONField(required=False)
    is_profile_complete = serializers.BooleanField(required=False)
    has_agreed_to_terms = serializers.BooleanField(required=False)
    title = serializers.CharField(allow_blank=True, required=False)
    years_of_experience = serializers.IntegerField(required=False)
    availability = serializers.BooleanField(required=False)
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reviews_count = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(required=False)
    profile_picture = serializers.ImageField()



class ExpertUserProfileSerializer(serializers.Serializer):
    # id = serializers.UUIDField(read_only=True)
    expert_id = serializers.UUIDField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    # country = serializers.CharField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    rating = serializers.FloatField(required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    completed_services = serializers.IntegerField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    portfolio = serializers.ListField(child=serializers.DictField(), required=False)  
    is_profile_complete = serializers.BooleanField(required=False)
    has_agreed_to_terms = serializers.BooleanField(required=False)
    title = serializers.CharField(required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False)
    availability = serializers.BooleanField(required=False)
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reviews_count = serializers.IntegerField(required=False)

    # ManyToMany and ForeignKey fields
    skills = serializers.ListField(child=serializers.DictField(),required=False)
    services = serializers.ListField(child=serializers.DictField(), required=False)
    is_profile_complete = serializers.BooleanField(read_only=True)
    completion_percentage = serializers.IntegerField(read_only=True)

    def validate_skills(self, value):
        print("VALUE", value)
        try:
            return [uuid.UUID(skill["id"]) for skill in value]
        except (KeyError, ValueError):
            raise serializers.ValidationError("Invalid skills format. Expected list of objects with 'id' as UUID.")

    def get_profile_picture(self, obj):
        return obj.profile_picture.url if obj.profile_picture else None

class UploadExpertProfilePhotoSerializer(serializers.Serializer):
    expert_id = serializers.UUIDField(required=True)
    profile_picture = serializers.ImageField(required=True)


class ExpertFilterSerializer(serializers.Serializer):
    # Basic filters
    title = serializers.CharField(required=False)
    availability = serializers.CharField(required=False)
    years_of_experience = serializers.IntegerField(required=False)
    total_earnings = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)
    is_profile_complete = serializers.BooleanField(required=False)
    has_agreed_to_terms = serializers.BooleanField(required=False)

    # Related expert filters
    expert__gender = serializers.CharField(required=False)
    expert__country = serializers.IntegerField(required=False)
    expert__first_name = serializers.CharField(required=False)
    expert__last_name = serializers.CharField(required=False)
    expert__email = serializers.EmailField(required=False)

    # List-based filter
    skills = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of skill names or IDs to filter by."
    )

    # General
    count = serializers.IntegerField(required=False, default=500)


class ExpertResultSerializer(serializers.Serializer):
    expert_id = serializers.UUIDField(required=True)
    first_name = serializers.CharField(source="expert.first_name")
    last_name = serializers.CharField(source="expert.last_name")
    email = serializers.EmailField(source="expert.email")
    gender = serializers.CharField(source="expert.gender")
    country = serializers.IntegerField(source="expert.country_id")

    profile_picture = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    bio = serializers.CharField(allow_blank=True, required=False)
    rating = serializers.FloatField(required=False)
    phone_number = serializers.CharField(required=False)
    completed_services = serializers.IntegerField(required=False)
    portfolio = serializers.JSONField(required=False)
    is_profile_complete = serializers.BooleanField()
    has_agreed_to_terms = serializers.BooleanField()
    title = serializers.CharField(required=False)
    years_of_experience = serializers.IntegerField(required=False)
    availability = serializers.CharField(required=False)
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reviews_count = serializers.IntegerField(required=False)

    def get_skills(self, obj):
        return [{"id": skill.id, "name": skill.name, "category": skill.category.id} for skill in obj.skills.all()]

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            url, _ = cloudinary_url(obj.profile_picture.public_id, secure=True)
            return url
        return None