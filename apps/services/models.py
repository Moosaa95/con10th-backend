# from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models, transaction
from django.db.models import Count, F, Q, Sum
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.category.models import Category
from commons.mixins import ModelMixin
from services.enums import DisputeStatusChoices, DisputeTypeChoices, PaymentStatusChoices, StatusChoices


# User = get_user_model()


    
# TODO: let the expert be the one setting up the price

# so with this service, service request and client profile how do i go about getting total number of services, active services and amount spent by the client


class Service(ModelMixin):
    """
    Represents an expert’s specific service offering.
    """
    expert = models.ForeignKey("accounts.ExpertUserProfile", on_delete=models.CASCADE, related_name="services", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="service_category")  # ✅ Service must belong to a skill
    title = models.CharField(max_length=255)
    description = models.TextField()
    # skills = models.ForeignKey(Skill, related_name='service_skill', blank=True, on_delete=models.CASCADE, null=True)
    # estimated_time = models.DurationField(null=True, blank=True, help_text="Estimated time to complete the service")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.title}  by {self.expert.expert}"
    


    @classmethod
    def create_service(cls, category_id, title, description, price=None):
        """
        Creates a new service for an expert.
        """
        return cls.objects.create(
            # expert_id=expert_id,
            category__id=category_id,
            title=title,
            description=description,
            price=price
        )

    @classmethod
    def update_service(cls, service_id, **kwargs):
        """
        Updates an existing service.
        """
        updated = cls.objects.filter(id=service_id).update(**kwargs)
        return updated > 0  # Returns True if update was successful
    


    @classmethod
    def get_service(cls, service_id):
        """
        Retrieves a specific service by ID.
        """
        try:
            return cls.objects.select_related("expert", "skill").get(id=service_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def fetch_services(cls, filters=Q()):
        """
        Retrieves all services with optional filtering.
        """

        return cls.objects.filter(filters).select_related("expert", "skill").order_by("-created_at")

    @classmethod
    def delete_service(cls, service_id):
        """
        Deletes a service by ID.
        """
        deleted, _ = cls.objects.filter(id=service_id).delete()
        return deleted > 0  # Returns True if deletion was successful

    @classmethod
    def toggle_service_status(cls, service_id):
        """
        Toggles the is_active status of a service.
        """
        service = cls.objects.filter(id=service_id).first()
        if service:
            service.is_active = not service.is_active
            service.save(update_fields=["is_active"])
            return service.is_active  # Returns the new status
        return None

class ServiceRequest(ModelMixin):
    """
    Represents a service request from a client to an expert.
    """
    
    client = models.ForeignKey("clients.ClientProfile", on_delete=models.CASCADE, related_name="service_requests")
    expert = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="engagements")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="requests")
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    end_date = models.DateField(help_text="Expected completion date provided by the client.")
    start_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=StatusChoices, default=StatusChoices.PENDING)
    expert_response_reason = models.TextField(blank=True, null=True)

    # Tracking service completion
    expert_completed = models.BooleanField(default=False)
    expert_completion_date = models.DateTimeField(blank=True, null=True)

    # Tracking client confirmation
    client_confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(blank=True, null=True)
    has_dispute = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['expert']),
            models.Index(fields=['status', 'client']),
            models.Index(fields=['status', 'expert']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Ensure agreed price is set before saving"""
        if not self.agreed_price:
            self.agreed_price = self.service.price  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client.client.first_name} -> {self.expert.first_name} | {self.status}"

    @classmethod
    def create_request(cls, client, expert, service, agreed_price, end_date):
        """
        Creates a new service request, ensuring no duplicate active requests exist.
        """
        if cls.objects.filter(client=client, expert=expert, service=service, status=StatusChoices.PENDING).exists():
            return None  # Prevent duplicate pending requests
        
        try:
            with transaction.atomic():
                new_request = cls.objects.create(
                    client=client,
                    expert=expert,
                    service=service,
                    agreed_price=agreed_price,
                    end_date=end_date,
                )

                # Send email to expert
                subject = "New Service Request"
                message = f"Hi {expert.first_name},\n\nYou have received a new service request. Log in to check details."
                cls.send_request_message(subject, message, expert.email)  
            
                return new_request
        except Exception as e:
            print(f"Error creating service request: {e}")
            return None
    
    @classmethod
    def confirm_service(cls, service_request):
        """
        Client confirms service, updating status and releasing payment.
        
        Args:
            service_request (ServiceRequest): The service request instance to confirm.

        Returns:
            bool: True if the service was successfully confirmed, False otherwise.
        """
        if not service_request:
            return False

        if service_request.status != cls.StatusChoices.AWAITING_CONFIRMATION:
            return False 

        try:
            with transaction.atomic():
                # Update the service request
                service_request.client_confirmed = True
                service_request.confirmation_date = timezone.now()
                service_request.status = cls.StatusChoices.COMPLETED
                service_request.save(update_fields=["client_confirmed", "confirmation_date", "status"])

                # Trigger payment release if funds are in escrow
                payment = service_request.payments.filter(status="in_escrow").first()
                if payment:
                    payment.release_funds()

            return True

        except Exception as e:
            return False

    @classmethod
    def get_service_requests(cls, **filters):
        """
        Retrieves service requests and allows flexible filtering using keyword arguments.

        Example Usage:
            - ServiceRequest.get_service_requests(id=5)
            - ServiceRequest.get_service_requests(status="pending")
            - ServiceRequest.get_service_requests(client=user)
            - ServiceRequest.get_service_requests(expert=user, status="accepted")

        Args:
            **filters: Dictionary of field-based filters.

        Returns:
            QuerySet: Filtered and optimized queryset of service requests.
        """
        try:
            queryset = cls.objects.select_related("client__profile", "expert__profile")
            
            if filters:
                queryset = queryset.filter(**filters)

            return queryset
        except Exception as e:
            # Optional: Log the error if needed
            print(f"Error fetching service requests: {e}")
            return None

    @classmethod
    def update_profiles(cls, service_request):
        if not service_request.client_confirmed or service_request.status != cls.StatusChoices.COMPLETED:
            return False

        try:
            with transaction.atomic():
                # Update expert profile
                service_request.expert.profile.update(
                    completed_services=F('completed_services') + 1,
                    total_earnings=F('total_earnings') + service_request.agreed_price
                )

                # Update client profile
                service_request.client.profile.update(
                    services_purchased=F('services_purchased') + 1,
                    total_spent=F('total_spent') + service_request.agreed_price
                )

            return True  # Success

        except Exception as e:
            return False
    
    @classmethod
    def update_service_status(cls, service_id, status, reason=''):
        try:
            with transaction.atomic():
                service_request = cls.objects.select_related("expert", "client").filter(id=service_id).first()
                
                if not service_request:
                    return None

                # Update status
                service_request.status = status
                service_request.expert_response_reason = reason
                service_request.save(update_fields=["status", "expert_response_reason"])

                subject = "Service Request Update"
                expert_message = f"Hi {service_request.expert.first_name},\n\nThe status of a service request has been updated to {status}. Log in to check details."
                client_message = f"Hi {service_request.client.first_name},\n\nYour service request status has been updated to {status}. Log in to check details."

                cls.send_request_message(subject, expert_message, service_request.expert.email)
                cls.send_request_message(subject, client_message, service_request.client.email)

                return service_request  

        except Exception as e:
            return None
    
    @classmethod
    def get_auto_complete_candidates(cls):
        """
        Get requests that should be auto-completed (expert marked as completed
        more than 24 hours ago but client hasn't confirmed).
        """
        auto_complete_threshold = timezone.now() - timezone.timedelta(hours=24)
        
        return cls.objects.filter(
            status="awaiting_confirmation",
            client_confirmed=False,
            expert_completed=True,
            expert_completion_date__lte=auto_complete_threshold

        )
    
    @classmethod
    def send_request_message(cls, subject, message, email):
        from services.tasks import send_email_task
        send_email_task.delay(subject, message, email)
    
    @classmethod
    def mark_expert_completed(cls, service_id):
        """
        Expert marks a service as completed.
        """
        try:
            with transaction.atomic():
                service_request = cls.objects.get(id=service_id, status=StatusChoices.IN_PROGRESS)
                service_request.expert_completed = True
                service_request.expert_completion_date = timezone.now()
                service_request.status = StatusChoices.AWAITING_CONFIRMATION
                service_request.save(update_fields=["expert_completed", "expert_completion_date", "status"])

                # Notify client
                subject = "Service Completed - Confirm Now"
                message = f"Hi {service_request.client.first_name},\n\nThe service has been completed. Log in to confirm."
                cls.send_request_message(subject, message, service_request.client.email)
                
                return True
        except cls.DoesNotExist:
            return False
        except Exception as e:
            print(f"Error marking service as completed: {e}")
            return False
    
    @classmethod
    def auto_confirm_services(cls):
        """
        Automatically confirms completed services if the client doesn't take action within 24 hours.
        """
        auto_complete_threshold = timezone.now() - timezone.timedelta(hours=24)

        try:
            with transaction.atomic():
                services = cls.objects.filter(
                    status=StatusChoices.AWAITING_CONFIRMATION,
                    client_confirmed=False,
                    expert_completed=True,
                    expert_completion_date__lte=auto_complete_threshold
                )

                for service in services:
                    service.client_confirmed = True
                    service.confirmation_date = timezone.now()
                    service.status = StatusChoices.COMPLETED
                    service.save(update_fields=["client_confirmed", "confirmation_date", "status"])
                    
                    # Release payment
                    # payment = service.payments.filter(status="in_escrow").first()
                    # if payment:
                    #     payment.release_funds()

        except Exception as e:
            print(f"Error in auto-confirming services: {e}")
    
    @classmethod
    def get_client_stats(cls, filters=None, recent_limit=3):
        queryset = cls.objects.filter(**filters) if filters else cls.objects.all()

        summary = cls._get_summary_aggregates(queryset)
        recent = cls._get_recent_requests(queryset, recent_limit)

        return {
            "summary": summary,
            "recent_requests": recent,
        }

    @classmethod
    def _get_summary_aggregates(cls, queryset):
        return queryset.aggregate(
            total_requests=Count("id"),
            active_requests=Count("id", filter=Q(status__in=[StatusChoices.PENDING, StatusChoices.IN_PROGRESS]), distinct=True),
            completed_requests=Count("id", filter=Q(status=StatusChoices.COMPLETED)),
            total_spent=Sum("agreed_price", filter=Q(status=StatusChoices.COMPLETED)),
        )

    @classmethod
    def _get_recent_requests(cls, queryset, limit):
        return list(
            queryset.order_by("-created_at")[:limit].values("id", "status", "agreed_price", "created_at")
        )



# class Dispute(models.Model):
#     """
#     Captures disputes raised by a client or expert for a given service request.
#     """
#     service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="disputes")
#     raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="disputes_raised")
#     dispute_type = models.CharField(
#         max_length=20, 
#         choices=DisputeTypeChoices.choices,
#         help_text="Type of dispute being raised"
#     )
#     client_statement = models.TextField(blank=True, null=True, help_text="Client's statement regarding the dispute.")
#     expert_statement = models.TextField(blank=True, null=True, help_text="Expert's statement regarding the dispute.")
#     description = models.TextField(help_text="Description of the issue.")
#     status = models.CharField(max_length=20, choices=DisputeStatusChoices, default=DisputeStatusChoices.OPEN)
#     resolution = models.TextField(blank=True, null=True, help_text="Admin resolution details.")
#     admin_notes = models.TextField(
#         blank=True, 
#         null=True, 
#         help_text="Internal notes for administrators."
#     )
#     resolved_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         related_name="disputes_resolved"
#     )
#     resolved_at = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


#     class Meta:
#         indexes = [
#             models.Index(fields=['status']),
#             models.Index(fields=['service_request']),
#             models.Index(fields=['raised_by']),
#             models.Index(fields=['created_at']),
#         ]
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Dispute for {self.service_request} - {self.status}"

#     def save(self, *args, **kwargs):
#         """
#         Override save to run validation and update service request status.
#         """
#         self.clean()
        
#         # If this is a new dispute, update the service request
#         if not self.pk:
#             self.service_request.has_dispute = True
#             self.service_request.save(update_fields=['has_dispute'])
        
#         super().save(*args, **kwargs)
        
#         # Send notification after saving
#         if not self.pk:
#             self.send_dispute_notification()

#     @classmethod
#     def create_dispute(cls, service_request, raised_by, dispute_type, description, evidence_files=None):
#         """
#         Create a new dispute for a service request.
        
#         Args:
#             service_request: The ServiceRequest object
#             raised_by: The User object raising the dispute
#             dispute_type: Type of dispute from DisputeTypeChoices
#             description: Detailed description of the issue
#             evidence_files: Optional list of file objects to attach as evidence
            
#         Returns:
#             The created Dispute object or None if validation fails
#         """
#         try:
#             # Validate that the user is part of the service request
#             if raised_by != service_request.client and raised_by != service_request.expert:
#                 return None
            
#             # Check if there's already an open dispute
#             if Dispute.objects.filter(
#                 service_request=service_request,
#                 status__in=[DisputeStatusChoices.OPEN, DisputeStatusChoices.UNDER_REVIEW]
#             ).exists():
#                 return None
            
#             # Create the dispute
#             dispute = cls(
#                 service_request=service_request,
#                 raised_by=raised_by,
#                 dispute_type=dispute_type,
#                 description=description
#             )
            
#             # Set the appropriate statement field based on who raised the dispute
#             # if raised_by == service_request.client:
#             #     dispute.client_statement = description
#             # else:
#             #     dispute.expert_statement = description
            
#             # dispute.save()
            
#             # # Add evidence files if provided
#             # if evidence_files:
#             #     for file in evidence_files:
#             #         evidence = DisputeEvidence.objects.create(
#             #             uploaded_by=raised_by,
#             #             file=file
#             #         )
#             #         dispute.evidence_files.add(evidence)
            
#             # # Update service request status
#             # service_request.has_dispute = True
#             # service_request.save(update_fields=['has_dispute'])
            
#             # # Send notifications
#             # dispute.send_dispute_notification()
            
#             return dispute
            
#         except ValidationError:
#             return None


# class Payment(models.Model):
    
#     service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="payments")
#     client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_made")
#     expert = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments_received")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'credit_card', 'paypal'
#     transaction_id = models.CharField(max_length=100, blank=True, null=True)
#     status = models.CharField(max_length=20, choices=PaymentStatusChoices, default=PaymentStatusChoices.PENDING)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Payment of {self.amount} for {self.service_request}"

#     @classmethod
#     def create_payment(cls, service_request, client, expert, amount, payment_method, transaction_id=None, status="pending"):
#         """
#         Creates a new payment record.
#         """
#         try:
#             with transaction.atomic():
#                 return cls.objects.create(
#                     service_request=service_request,
#                     client=client,
#                     expert=expert,
#                     amount=amount,
#                     payment_method=payment_method,
#                     transaction_id=transaction_id,
#                     status=status
#                 )
#         except Exception as e:
#             print(f"Error creating payment for ServiceRequest {service_request.id}: {e}")
#             return None  # Ensure transaction rollback on failure

#     @classmethod
#     def release_funds(cls, payment_id):
#         """
#         Releases funds from escrow when the client confirms service completion.
#         """
#         try:
#             with transaction.atomic():
#                 # Retrieve payment in escrow
#                 payment = cls.objects.filter(id=payment_id, status="in_escrow").select_related("client__client_profile", "expert__expert_profile").first()
#                 if not payment:
#                     print(f"Payment ID {payment_id} not found or not in escrow.")
#                     return False

#                 # Update payment status
#                 payment.status = PaymentStatusChoices.RELEASED
#                 payment.save(update_fields=["status"])

#                 # Update expert's and client's financial records
#                 payment.expert.expert_profile.total_earnings = models.F('total_earnings') + payment.amount
#                 payment.client.client_profile.total_spent = models.F('total_spent') + payment.amount

#                 payment.expert.expert_profile.save(update_fields=["total_earnings"])
#                 payment.client.client_profile.save(update_fields=["total_spent"])

#                 return True
#         except Exception as e:
#             print(f"Error releasing funds for Payment ID {payment_id}: {e}")
#             return False
#     # @classmethod
#     # def mark_as_accepted(cls):
#     #     """
#     #     Expert accepts the request.
#     #     """
#     #     cls.status = "accepted"
#     #     cls.save(update_fields=['status'])
#     #     cls.send_status_update_notification(accepted=True)

#     # @classmethod
#     # def mark_as_rejected(cls, reason=None):
#     #     """
#     #     Expert rejects the request.
#     #     """
#     #     cls.status = "rejected"
#     #     cls.expert_response_reason = reason
#     #     cls.save(update_fields=['status', 'expert_response_reason'])
#     #     cls.send_status_update_notification(accepted=False)

#     # @classmethod
#     # def mark_as_expert_completed(cls):
#     #     """
#     #     Expert notifies that work is completed.
#     #     """
#     #     cls.expert_completed = True
#     #     cls.expert_completion_date = timezone.now()
#     #     cls.status = "awaiting_confirmation"
#     #     cls.save(update_fields=['expert_completed', 'expert_completion_date', 'status'])

#     #     subject = "Service Completed - Confirm Now"
#     #     message = f"Hi {cls.client.username},\n\n{cls.expert.username} has completed the service. Log in to review and confirm."
#     #     send_email_task.delay(subject, message, cls.client.email)

    
#     # @classmethod
#     # def send_request_notification(cls):
#     #     """
#     #     Notify expert when a new service request is received.
#     #     """
#     #     subject = "New Service Request"
#     #     message = f"Hi {cls.expert.username},\n\nYou have received a new service request. Log in to check details."
#     #     send_email_task.delay(subject, message, cls.expert.email)  

#     # @classmethod
#     # def send_status_update_notification(cls, accepted=True):
#     #     """
#     #     Notify the client when the expert accepts/rejects the request.
#     #     """
#     #     action = "accepted" if accepted else "rejected"
#     #     subject = f"Service Request {action.capitalize()}"
#     #     message = f"Hi {cls.client.username},\n\nYour service request has been {action} by {cls.expert.username}. Log in to check details."
#     #     send_email_task.delay(subject, message, cls.client.email)
