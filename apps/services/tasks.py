from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from apps.services.models import ServiceRequest

@shared_task
def send_email_task(subject, message, recipient):
    
    try: 
        send_mail(
        subject,
        message,
        'noreply@yourplatform.com',  # Replace with your actual sender email
        [recipient],
        fail_silently=True
    )
    except  Exception as e: 
        print("Failed to send service")


@shared_task
def auto_confirm_services():
    """
    Automatically confirms service completion if the client doesn't take action within 24 hours.
    """
    try:
        with transaction.atomic():
            # Get all service requests eligible for auto-confirmation
            service_requests = ServiceRequest.get_auto_complete_candidates()

            if not service_requests:
                print("No service requests eligible for auto-confirmation.")
                return False

            for service_request in service_requests:
                success = ServiceRequest.confirm_service(service_request)
                if success:
                    print(f"ServiceRequest ID {service_request.id} auto-confirmed successfully.")
                else:
                    print(f"Failed to auto-confirm ServiceRequest ID {service_request.id}.")

    except Exception as e:
        print(f"Error occurred while auto-confirming services: {e}")
    