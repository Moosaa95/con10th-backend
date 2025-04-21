from django.conf import settings
from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver

# get the user model
from django.contrib.auth import get_user_model

# from accounts.enums import UserRoles

from .models import OTPVerification, ExpertUserProfile

from clients.models import ClientProfile

from .tasks import send_otp_email_task

User = get_user_model()

ROLE_PROFILE_MAPPING = {
    'expert': ExpertUserProfile,
    'client': ClientProfile,
    # 'is_staff': AdminProfile,
}


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create/update user profiles based on role
    """
    try:
        if created:
            # Create profile if user has matching role
            profile_class = ROLE_PROFILE_MAPPING.get(instance.role)
            if profile_class:
                profile_class.create_profile(user=instance)
                print(f"Created {instance.role} profile for {instance.email}")
        else:
            # Update existing profiles
            if hasattr(instance, 'profile'):
                ClientProfile.update_profile(user=instance)
            if hasattr(instance, 'expert_profile'):
                ExpertUserProfile.update_profile(user=instance)
                
    except IntegrityError as e:
        print(f"Profile error for {instance.email}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         User.objects.create(user=instance)
#     instance.user.save()
#     print("User profile created or updated successfully!")



@receiver(post_save, sender=User)
def create_otp_for_new_user(sender, instance, created, **kwargs):
    """
    Generate OTP for new users and send OTP via email.
    """
    # print("SIGNAL")
    if created and not hasattr(instance, "otp_verification") or not instance.otp_verification.is_verified:
        # print("INNER OTP=====", instance, dir(instance))
        # if instance.role == UserRoles.NORMAL_USER:
        otp = OTPVerification.generate_otp(instance)
        print("OTP", otp)
        send_otp_email_task.delay(instance.email, instance.first_name, otp)


# @receiver(post_save, sender=User)
# def handle_skilled_user_approval(sender, instance, **kwargs):
#     """
#     Send OTP to skilled users only after admin approval.
#     """
#     if instance.role == "skilled_user" and instance.is_approved and not instance.is_verified:
#         otp = OTPVerification.generate_otp(instance)  # ✅ Generate OTP
#         send_otp_email_task.delay(instance.email, instance.first_name, otp)  # ✅ Send OTP after approval