from django.core.mail import send_mail
from django.conf import settings
# import logging

# logger = logging.getLogger(__name__)

def send_otp_email(user, otp):
    """
    Sends an OTP email to the user.
    """
    subject = "Your OTP for Account Verification"
    message = f"Hello {user.first_name},\n\nYour OTP for verifying your account is: {otp}\n\nUse this OTP to activate your account."
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        print(f"OTP email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send OTP email to {user.email}: {str(e)}")
