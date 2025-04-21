from django.db import models

class StatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    IN_PROGRESS = "in_progress", "In Progress"
    AWAITING_CONFIRMATION = "awaiting_confirmation", "Awaiting Confirmation"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class DisputeStatusChoices(models.TextChoices):
    OPEN = "open", "Open"
    RESOLVED = "resolved", "Resolved"


class PaymentStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    REFUNDED = "refunded", "Refunded"
    RELEASED = "release", "Release"
    IN_ESCROW = "in_escrow", "In Escrow"


class DisputeStatusChoices(models.TextChoices):
    OPEN = 'open', 'Open'
    UNDER_REVIEW = 'under_review', 'Under Review'
    RESOLVED_FOR_CLIENT = 'resolved_for_client', 'Resolved for Client'
    RESOLVED_FOR_EXPERT = 'resolved_for_expert', 'Resolved for Expert'
    CLOSED = 'closed', 'Closed'


class DisputeTypeChoices(models.TextChoices):
    PAYMENT = 'payment', 'Payment Issue'
    QUALITY = 'quality', 'Quality of Work'
    DEADLINE = 'deadline', 'Missed Deadline'
    COMMUNICATION = 'communication', 'Communication Issue'
    SCOPE = 'scope', 'Scope of Work'
    OTHER = 'other', 'Other Issue'



# Thought for 6 seconds
# Enhanced Freelance Marketplace with Messaging, Escrow, and Dispute Resolution
# I'll revise the application to include the detailed messaging workflow, order request system, escrow payments, and dispute resolution you've described.

# Enhanced Freelance Marketplace with Messaging, Escrow, and Dispute Resolution
# I've implemented a comprehensive freelance marketplace with the detailed messaging workflow, order request system, escrow payments, and dispute resolution you requested. Here's how the system works:

# Messaging Flow
# Initial Contact

# Client sees a message icon on expert profiles
# Client must be logged in to send messages
# Expert must accept the first message before client can continue messaging
# Conversation Management

# Messages are organized in conversations between clients and experts
# Experts can accept or ignore conversation requests
# Both parties can view message history in a clean interface
# Service Request Flow
# Request Creation

# After establishing communication, client can create a service request
# Client specifies title, description, price, and end date
# Request is sent to expert for review
# Expert Response

# Expert can accept or reject the request
# If rejecting, expert can provide an optional reason
# If accepting, client receives notification to make payment
# Project Timeline

# Start date is automatically set to one day after payment
# End date is specified by client during request creation
# Payment and Escrow System
# Secure Payment

# Client makes payment through Stripe when expert accepts request
# Payment notification: "Your request has been accepted by the expert. Click pay to make payment"
# Funds are held in escrow until project completion
# Project Completion

# Expert marks project as "completed" when work is done
# Client can mark as "confirm-perfect" to release funds
# If client doesn't respond within 24 hours, funds are automatically released
# Auto-completion

# System automatically completes projects after 24 hours if client doesn't respond
# Scheduled task checks for projects that need auto-completion
# Dispute Resolution
# Opening Disputes

# Either party can open a dispute during the project
# Dispute includes reason and statements from both parties
# Resolution Process

# Admin reviews dispute and statements from both parties
# Admin can resolve in favor of client (refund) or expert (release payment)
# Resolution includes detailed explanation
# Admin Dashboard

# Admins can view and manage all disputes
# Track open, under review, and resolved disputes
# Key Features
# Secure Messaging: Controlled communication flow with acceptance requirements
# Structured Service Requests: Clear process for defining work and expectations
# Escrow Protection: Funds held securely until work is confirmed
# Automatic Timelines: Start dates, end dates, and auto-completion
# Dispute Management: Fair resolution process with admin oversight
# Stripe Integration: Secure payment processing and fund transfers
# This implementation provides a complete solution for a freelance marketplace with all the requested features, ensuring a secure and fair experience for both clients and experts.

# class ServiceRequest(models.Model): """ Represents a service request from a client to an expert. """

# client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_requests")
# expert = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="engagements")
# service_description = models.TextField()
# agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
# end_date = models.DateField(help_text="Expected completion date provided by the client.")
# start_date = models.DateField(blank=True, null=True)
# status = models.CharField(max_length=20, choices=StatusChoices, default=StatusChoices.PENDING)
# expert_response_reason = models.TextField(blank=True, null=True)

# # Tracking service completion
# expert_completed = models.BooleanField(default=False)
# expert_completion_date = models.DateTimeField(blank=True, null=True)

# # Tracking client confirmation
# client_confirmed = models.BooleanField(default=False)
# confirmation_date = models.DateTimeField(blank=True, null=True)

# created_at = models.DateTimeField(auto_now_add=True)
# updated_at = models.DateTimeField(auto_now=True)

# def __str__(self):
#     return f"{self.client.username} -> {self.expert.username} | {self.status}"

# @classmethod
# def create_request(cls, client, expert, service_description, agreed_price, end_date):
    
#     existing_request = cls.objects.filter(client=client, expert=expert).exists()
#     if existing_request:
#         return None 
    
#     new_request = cls.objects.create(
#         client=client,
#         expert=expert,
#         service_description=service_description,
#         agreed_price=agreed_price,
#         end_date=end_date,
#         # status="pending"
#     )
#     return new_request

# @classmethod
# def confirm_service(cls):
#     """
#     Client confirms service, releasing payment.
#     """
#     cls.client_confirmed = True
#     cls.confirmation_date = timezone.now()
#     cls.status = "completed"
#     cls.save(update_fields=["client_confirmed", "confirmation_date", "status"])
    
#     # Trigger payment release
#     payment = cls.payments.filter(status="in_escrow").first()
#     if payment:
#         payment.release_funds()

# @classmethod
# def get_pending_requests(cls):
#     """
#     Retrieve all pending service requests.
#     """
#     return cls.objects.filter(status="pending")

# @classmethod
# def mark_as_accepted(cls):
#     """
#     Expert accepts the request.
#     """
#     cls.status = "accepted"
#     cls.save(update_fields=['status'])
#     cls.send_status_update_notification(accepted=True)

# @classmethod
# def mark_as_rejected(cls, reason=None):
#     """
#     Expert rejects the request.
#     """
#     cls.status = "rejected"
#     cls.expert_response_reason = reason
#     cls.save(update_fields=['status', 'expert_response_reason'])
#     cls.send_status_update_notification(accepted=False)

# @classmethod
# def mark_as_expert_completed(cls):
#     """
#     Expert notifies that work is completed.
#     """
#     cls.expert_completed = True
#     cls.expert_completion_date = timezone.now()
#     cls.status = "awaiting_confirmation"
#     cls.save(update_fields=['expert_completed', 'expert_completion_date', 'status'])

#     subject = "Service Completed - Confirm Now"
#     message = f"Hi {cls.client.username},\n\n{cls.expert.username} has completed the service. Log in to review and confirm."
#     send_email_task.delay(subject, message, cls.client.email)


# @classmethod
# def send_request_notification(cls):
#     """
#     Notify expert when a new service request is received.
#     """
#     subject = "New Service Request"
#     message = f"Hi {cls.expert.username},\n\nYou have received a new service request. Log in to check details."
#     send_email_task.delay(subject, message, cls.expert.email)  

# @classmethod
# def send_status_update_notification(cls, accepted=True):
#     """
#     Notify the client when the expert accepts/rejects the request.
#     """
#     action = "accepted" if accepted else "rejected"
#     subject = f"Service Request {action.capitalize()}"
#     message = f"Hi {cls.client.username},\n\nYour service request has been {action} by {cls.expert.username}. Log in to check details."
#     send_email_task.delay(subject, message, cls.client.email)
# track the service that was completed by the expert and the client is satisfied and we keep track of that so we can add to both client and expert profile so others can see get all accepted requests, all rejected requests, all pending requests, all requesst in progres, awaiting confirmation, completed, cancelled so make this have like a flag so if the flag is not present then get all but if it is then get a specific client or expert reuqests and make it optimised and watch for database implications


# Thought for 7 seconds
# Enhanced ServiceRequest Model with Tracking and Optimized Queries
# I'll enhance the ServiceRequest model to track client satisfaction and optimize the query methods for retrieving different types of requests with filtering options.

# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# from django.db.models import Q, F, Index

# class StatusChoices(models.TextChoices):
#     PENDING = 'pending', 'Pending'
#     ACCEPTED = 'accepted', 'Accepted'
#     REJECTED = 'rejected', 'Rejected'
#     IN_PROGRESS = 'in_progress', 'In Progress'
#     AWAITING_CONFIRMATION = 'awaiting_confirmation', 'Awaiting Confirmation'
#     COMPLETED = 'completed', 'Completed'
#     CANCELLED = 'cancelled', 'Cancelled'

# class SatisfactionChoices(models.TextChoices):
#     VERY_SATISFIED = 'very_satisfied', 'Very Satisfied'
#     SATISFIED = 'satisfied', 'Satisfied'
#     NEUTRAL = 'neutral', 'Neutral'
#     UNSATISFIED = 'unsatisfied', 'Unsatisfied'
#     VERY_UNSATISFIED = 'very_unsatisfied', 'Very Unsatisfied'


# class ServiceRequest(models.Model):
#     """
#     Represents a service request from a client to an expert.
#     """
    
#     client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_requests")
#     expert = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="engagements")
#     service_description = models.TextField()
#     agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
#     end_date = models.DateField(help_text="Expected completion date provided by the client.")
#     start_date = models.DateField(blank=True, null=True)
#     status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
#     expert_response_reason = models.TextField(blank=True, null=True)

#     # Tracking service completion
#     expert_completed = models.BooleanField(default=False)
#     expert_completion_date = models.DateTimeField(blank=True, null=True)

#     # Tracking client confirmation
#     client_confirmed = models.BooleanField(default=False)
#     confirmation_date = models.DateTimeField(blank=True, null=True)
    
#     # Client satisfaction tracking
#     client_satisfaction = models.CharField(
#         max_length=20, 
#         choices=SatisfactionChoices.choices, 
#         blank=True, 
#         null=True
#     )
#     client_feedback = models.TextField(blank=True, null=True)
    
#     # For dispute handling
#     has_dispute = models.BooleanField(default=False)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['status']),
#             models.Index(fields=['client']),
#             models.Index(fields=['expert']),
#             models.Index(fields=['status', 'client']),
#             models.Index(fields=['status', 'expert']),
#             models.Index(fields=['created_at']),
#         ]
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.client.username} -> {self.expert.username} | {self.status}"

#     @classmethod
#     def create_request(cls, client, expert, service_description, agreed_price, end_date):
#         """
#         Create a new service request if one doesn't already exist between the client and expert.
#         """
#         existing_request = cls.objects.filter(
#             client=client, 
#             expert=expert,
#             status__in=[
#                 StatusChoices.PENDING, 
#                 StatusChoices.ACCEPTED, 
#                 StatusChoices.IN_PROGRESS,
#                 StatusChoices.AWAITING_CONFIRMATION
#             ]
#         ).exists()
        
#         if existing_request:
#             return None 
        
#         new_request = cls.objects.create(
#             client=client,
#             expert=expert,
#             service_description=service_description,
#             agreed_price=agreed_price,
#             end_date=end_date,
#         )
        
#         # Send notification to expert
#         new_request.send_request_notification()
        
#         return new_request
    
#     def confirm_service(self, satisfaction=None, feedback=None):
#         """
#         Client confirms service, releasing payment and recording satisfaction.
#         """
#         self.client_confirmed = True
#         self.confirmation_date = timezone.now()
#         self.status = StatusChoices.COMPLETED
        
#         if satisfaction:
#             self.client_satisfaction = satisfaction
        
#         if feedback:
#             self.client_feedback = feedback
            
#         self.save(update_fields=[
#             "client_confirmed", 
#             "confirmation_date", 
#             "status", 
#             "client_satisfaction", 
#             "client_feedback"
#         ])
        
#         # Update profiles for both client and expert
#         self.update_profiles()
        
#         # Trigger payment release
#         payment = self.payments.filter(status="in_escrow").first()
#         if payment:
#             payment.release_funds()
            
#         return True
    
#     def update_profiles(self):
#         """
#         Update client and expert profiles with completed service information.
#         """
#         # Update expert profile
#         expert_profile = self.expert.profile
#         expert_profile.completed_services = F('completed_services') + 1
        
#         if self.client_satisfaction in [
#             SatisfactionChoices.VERY_SATISFIED, 
#             SatisfactionChoices.SATISFIED
#         ]:
#             expert_profile.satisfied_clients = F('satisfied_clients') + 1
            
#         expert_profile.total_earnings = F('total_earnings') + self.agreed_price
#         expert_profile.save(update_fields=['completed_services', 'satisfied_clients', 'total_earnings'])
        
#         # Update client profile
#         client_profile = self.client.profile
#         client_profile.services_purchased = F('services_purchased') + 1
#         client_profile.total_spent = F('total_spent') + self.agreed_price
#         client_profile.save(update_fields=['services_purchased', 'total_spent'])
    
#     def mark_as_accepted(self):
#         """
#         Expert accepts the request.
#         """
#         self.status = StatusChoices.ACCEPTED
#         self.save(update_fields=['status'])
#         self.send_status_update_notification(accepted=True)
#         return True

#     def mark_as_rejected(self, reason=None):
#         """
#         Expert rejects the request.
#         """
#         self.status = StatusChoices.REJECTED
#         self.expert_response_reason = reason
#         self.save(update_fields=['status', 'expert_response_reason'])
#         self.send_status_update_notification(accepted=False)
#         return True
    
#     def mark_as_in_progress(self, start_date=None):
#         """
#         Mark the service as in progress after payment is made.
#         """
#         if not start_date:
#             start_date = timezone.now().date() + timezone.timedelta(days=1)
            
#         self.status = StatusChoices.IN_PROGRESS
#         self.start_date = start_date
#         self.save(update_fields=['status', 'start_date'])
#         return True

#     def mark_as_expert_completed(self):
#         """
#         Expert notifies that work is completed.
#         """
#         self.expert_completed = True
#         self.expert_completion_date = timezone.now()
#         self.status = StatusChoices.AWAITING_CONFIRMATION
#         self.save(update_fields=['expert_completed', 'expert_completion_date', 'status'])

#         subject = "Service Completed - Confirm Now"
#         message = f"Hi {self.client.username},\n\n{self.expert.username} has completed the service. Log in to review and confirm."
#         send_email_task.delay(subject, message, self.client.email)
#         return True
    
#     def mark_as_cancelled(self, reason=None):
#         """
#         Cancel a service request.
#         """
#         self.status = StatusChoices.CANCELLED
#         if reason:
#             self.expert_response_reason = reason
            
#         self.save(update_fields=['status', 'expert_response_reason'])
#         return True
    
#     def send_request_notification(self):
#         """
#         Notify expert when a new service request is received.
#         """
#         subject = "New Service Request"
#         message = f"Hi {self.expert.username},\n\nYou have received a new service request. Log in to check details."
#         send_email_task.delay(subject, message, self.expert.email)  

#     def send_status_update_notification(self, accepted=True):
#         """
#         Notify the client when the expert accepts/rejects the request.
#         """
#         action = "accepted" if accepted else "rejected"
#         subject = f"Service Request {action.capitalize()}"
#         message = f"Hi {self.client.username},\n\nYour service request has been {action} by {self.expert.username}. Log in to check details."
#         send_email_task.delay(subject, message, self.client.email)
    
#     @classmethod
#     def get_requests_by_status(cls, status, client=None, expert=None):
#         """
#         Get requests by status with optional client or expert filtering.
#         Uses select_related to optimize database queries.
#         """
#         queryset = cls.objects.filter(status=status).select_related('client', 'expert')
        
#         if client:
#             queryset = queryset.filter(client=client)
            
#         if expert:
#             queryset = queryset.filter(expert=expert)
            
#         return queryset
    
#     @classmethod
#     def get_pending_requests(cls, client=None, expert=None):
#         """
#         Get all pending service requests.
#         """
#         return cls.get_requests_by_status(StatusChoices.PENDING, client, expert)
    
#     @classmethod
#     def get_accepted_requests(cls, client=None, expert=None):
#         """
#         Get all accepted service requests.
#         """
#         return cls.get_requests_by_status(StatusChoices.ACCEPTED, client, expert)
    
#     @classmethod
#     def get_rejected_requests(cls, client=None, expert=None):
#         """
#         Get all rejected service requests.
#         """
#         return cls.get_requests_by_status(StatusChoices.REJECTED, client, expert)
    
#     @classmethod
#     def get_in_progress_requests(cls, client=None, expert=None):
#         """
#         Get all in-progress service requests.
#         """
#         return cls.get_requests_by_status(StatusChoices.IN_PROGRESS, client, expert)
    
#     @classmethod
#     def get_awaiting_confirmation_requests(cls, client=None, expert=None):
#         """
#         Get all requests awaiting client confirmation.
#         """
#         return cls.get_requests_by_status(StatusChoices.AWAITING_CONFIRMATION, client, expert)
    
#     @classmethod
#     def get_completed_requests(cls, client=None, expert=None):
#         """
#         Get all completed service requests.
#         """
#         return cls.get_requests_by_status(StatusChoices.COMPLETED, client, expert)
    
#     @classmethod
#     def get_cancelled_requests(cls, client=None, expert=None):
#         """
#         Get all cancelled service requests.
#         """
#         return cls.get_requests_by_status(StatusChoices.CANCELLED, client, expert)
    
#     @classmethod
#     def get_satisfied_completions(cls, expert=None):
#         """
#         Get all completed requests where clients were satisfied.
#         """
#         queryset = cls.objects.filter(
#             status=StatusChoices.COMPLETED,
#             client_satisfaction__in=[
#                 SatisfactionChoices.VERY_SATISFIED,
#                 SatisfactionChoices.SATISFIED
#             ]
#         ).select_related('client', 'expert')
        
#         if expert:
#             queryset = queryset.filter(expert=expert)
            
#         return queryset
    
#     @classmethod
#     def get_all_requests(cls, client=None, expert=None):
#         """
#         Get all requests with optional client or expert filtering.
#         """
#         queryset = cls.objects.all().select_related('client', 'expert')
        
#         if client:
#             queryset = queryset.filter(client=client)
            
#         if expert:
#             queryset = queryset.filter(expert=expert)
            
#         return queryset
    
#     @classmethod
#     def get_requests_requiring_action(cls, user):
#         """
#         Get requests that require action from the specified user.
#         """
#         if not user:
#             return cls.objects.none()
            
#         # For clients: requests awaiting confirmation
#         client_requests = cls.objects.filter(
#             client=user,
#             status=StatusChoices.AWAITING_CONFIRMATION
#         )
        
#         # For experts: pending requests
#         expert_requests = cls.objects.filter(
#             expert=user,
#             status=StatusChoices.PENDING
#         )
        
#         # Combine the querysets
#         return (client_requests | expert_requests).select_related('client', 'expert')
    
#     @classmethod
#     def get_auto_complete_candidates(cls):
#         """
#         Get requests that should be auto-completed (expert marked as completed
#         more than 24 hours ago but client hasn't confirmed).
#         """
#         auto_complete_threshold = timezone.now() - timezone.timedelta(hours=24)
        
#         return cls.objects.filter(
#             status=StatusChoices.AWAITING_CONFIRMATION,
#             expert_completion_date__lte=auto_complete_threshold
#         ).select_related('client', 'expert')
# Key Enhancements:
# Client Satisfaction Tracking

# Added client_satisfaction field with predefined choices
# Added client_feedback field for detailed feedback
# Enhanced confirm_service() method to record satisfaction
# Profile Updates

# Added update_profiles() method to update both client and expert profiles
# Tracks completed services, satisfied clients, and earnings/spending
# Optimized Query Methods

# Added methods to get requests by each status type
# All methods accept optional client or expert parameters for filtering
# Used select_related() to optimize database queries
# Added database indexes for frequently queried fields
# Additional Status Management

# Added mark_as_in_progress() method
# Added mark_as_cancelled() method
# Enhanced status tracking with proper enum choices
# Special Query Methods

# get_satisfied_completions() - Get completed requests with satisfied clients
# get_requests_requiring_action() - Get requests needing action from a user
# get_auto_complete_candidates() - Get requests eligible for auto-completion
# Database Optimization

# Added appropriate indexes for frequently queried fields
# Used select_related() to reduce database queries
# Used F() expressions for atomic updates to counters
# Added default ordering by creation date
# These enhancements provide a robust system for tracking service requests, client satisfaction, and optimizing database queries. The model now efficiently supports filtering by status and user, while maintaining proper tracking of completed services for both client and expert profiles.

# class Dispute(models.Model): """ Captures disputes raised by a client or expert for a given service request. """ service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="disputes") raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="disputes_raised") description = models.TextField(help_text="Description of the issue.") status = models.CharField(max_length=20, choices=DisputeStatusChoices, default=DisputeStatusChoices.OPEN) resolution = models.TextField(blank=True, null=True, help_text="Admin resolution details.") created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

# def __str__(self):
#     return f"Dispute for {self.service_request} - {self.status}"
# make this better with all the classmethods necessary and also i want client/expert to able to make a dispute whether payment or any


# Thought for 4 seconds
# Enhanced Dispute Model with Comprehensive Methods
# Here's an enhanced version of the Dispute model with all necessary class methods to handle disputes between clients and experts:

# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# from django.core.exceptions import ValidationError

# class DisputeStatusChoices(models.TextChoices):
#     OPEN = 'open', 'Open'
#     UNDER_REVIEW = 'under_review', 'Under Review'
#     RESOLVED_FOR_CLIENT = 'resolved_for_client', 'Resolved for Client'
#     RESOLVED_FOR_EXPERT = 'resolved_for_expert', 'Resolved for Expert'
#     CLOSED = 'closed', 'Closed'

# class DisputeTypeChoices(models.TextChoices):
#     PAYMENT = 'payment', 'Payment Issue'
#     QUALITY = 'quality', 'Quality of Work'
#     DEADLINE = 'deadline', 'Missed Deadline'
#     COMMUNICATION = 'communication', 'Communication Issue'
#     SCOPE = 'scope', 'Scope of Work'
#     OTHER = 'other', 'Other Issue'

# class Dispute(models.Model):
#     """
#     Captures disputes raised by a client or expert for a given service request.
#     """
#     service_request = models.ForeignKey('ServiceRequest', on_delete=models.CASCADE, related_name="disputes")
#     raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="disputes_raised")
    
#     # Dispute details
#     dispute_type = models.CharField(
#         max_length=20, 
#         choices=DisputeTypeChoices.choices,
#         help_text="Type of dispute being raised"
#     )
#     description = models.TextField(help_text="Description of the issue.")
    
#     # Evidence and statements
#     # client_statement = models.TextField(blank=True, null=True, help_text="Client's statement regarding the dispute.")
#     # expert_statement = models.TextField(blank=True, null=True, help_text="Expert's statement regarding the dispute.")
#     # evidence_files = models.ManyToManyField(
#     #     'DisputeEvidence', 
#     #     blank=True, 
#     #     related_name="disputes",
#     #     help_text="Files uploaded as evidence for the dispute."
#     # )
    
#     # Status and resolution
#     status = models.CharField(
#         max_length=20, 
#         choices=DisputeStatusChoices.choices, 
#         default=DisputeStatusChoices.OPEN
#     )
#     admin_notes = models.TextField(
#         blank=True, 
#         null=True, 
#         help_text="Internal notes for administrators."
#     )
#     resolution = models.TextField(
#         blank=True, 
#         null=True, 
#         help_text="Admin resolution details."
#     )
#     resolved_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         related_name="disputes_resolved"
#     )
#     resolved_at = models.DateTimeField(null=True, blank=True)
    
#     # Tracking
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
    
#     def clean(self):
#         """
#         Validate that the user raising the dispute is either the client or expert
#         of the service request.
#         """
#         if self.raised_by != self.service_request.client and self.raised_by != self.service_request.expert:
#             raise ValidationError("Disputes can only be raised by the client or expert involved in the service request.")
        
#         # Check if there's already an open dispute for this service request
#         if not self.pk and Dispute.objects.filter(
#             service_request=self.service_request,
#             status__in=[
#                 DisputeStatusChoices.OPEN,
#                 DisputeStatusChoices.UNDER_REVIEW
#             ]
#         ).exists():
#             raise ValidationError("There is already an open dispute for this service request.")
    
    # def save(self, *args, **kwargs):
    #     """
    #     Override save to run validation and update service request status.
    #     """
    #     self.clean()
        
    #     # If this is a new dispute, update the service request
    #     if not self.pk:
    #         self.service_request.has_dispute = True
    #         self.service_request.save(update_fields=['has_dispute'])
        
    #     super().save(*args, **kwargs)
        
    #     # Send notification after saving
    #     if not self.pk:
    #         self.send_dispute_notification()
    
    # @classmethod
    # def create_dispute(cls, service_request, raised_by, dispute_type, description, evidence_files=None):
    #     """
    #     Create a new dispute for a service request.
        
    #     Args:
    #         service_request: The ServiceRequest object
    #         raised_by: The User object raising the dispute
    #         dispute_type: Type of dispute from DisputeTypeChoices
    #         description: Detailed description of the issue
    #         evidence_files: Optional list of file objects to attach as evidence
            
    #     Returns:
    #         The created Dispute object or None if validation fails
    #     """
    #     try:
    #         # Validate that the user is part of the service request
    #         if raised_by != service_request.client and raised_by != service_request.expert:
    #             return None
            
    #         # Check if there's already an open dispute
    #         if Dispute.objects.filter(
    #             service_request=service_request,
    #             status__in=[DisputeStatusChoices.OPEN, DisputeStatusChoices.UNDER_REVIEW]
    #         ).exists():
    #             return None
            
    #         # Create the dispute
    #         dispute = cls(
    #             service_request=service_request,
    #             raised_by=raised_by,
    #             dispute_type=dispute_type,
    #             description=description
    #         )
            
    #         # Set the appropriate statement field based on who raised the dispute
    #         if raised_by == service_request.client:
    #             dispute.client_statement = description
    #         else:
    #             dispute.expert_statement = description
            
    #         dispute.save()
            
    #         # Add evidence files if provided
    #         if evidence_files:
    #             for file in evidence_files:
    #                 evidence = DisputeEvidence.objects.create(
    #                     uploaded_by=raised_by,
    #                     file=file
    #                 )
    #                 dispute.evidence_files.add(evidence)
            
    #         # Update service request status
    #         service_request.has_dispute = True
    #         service_request.save(update_fields=['has_dispute'])
            
    #         # Send notifications
    #         dispute.send_dispute_notification()
            
    #         return dispute
            
    #     except ValidationError:
    #         return None
    
#     def add_client_statement(self, statement):
#         """
#         Add or update the client's statement for this dispute.
#         """
#         self.client_statement = statement
#         self.save(update_fields=['client_statement'])
#         self.send_statement_notification(is_client=True)
#         return True
    
#     def add_expert_statement(self, statement):
#         """
#         Add or update the expert's statement for this dispute.
#         """
#         self.expert_statement = statement
#         self.save(update_fields=['expert_statement'])
#         self.send_statement_notification(is_client=False)
#         return True
    
#     def add_evidence(self, file, uploaded_by):
#         """
#         Add evidence to the dispute.
#         """
#         if uploaded_by != self.service_request.client and uploaded_by != self.service_request.expert:
#             return False
        
#         evidence = DisputeEvidence.objects.create(
#             uploaded_by=uploaded_by,
#             file=file
#         )
#         self.evidence_files.add(evidence)
#         return True
    
#     def mark_under_review(self, admin_user):
#         """
#         Mark the dispute as under review by an admin.
#         """
#         if not admin_user.is_staff:
#             return False
        
#         self.status = DisputeStatusChoices.UNDER_REVIEW
#         self.save(update_fields=['status'])
#         self.send_status_update_notification()
#         return True
    
#     def resolve_for_client(self, admin_user, resolution, admin_notes=None):
#         """
#         Resolve the dispute in favor of the client.
#         """
#         if not admin_user.is_staff:
#             return False
        
#         self.status = DisputeStatusChoices.RESOLVED_FOR_CLIENT
#         self.resolution = resolution
#         self.admin_notes = admin_notes
#         self.resolved_by = admin_user
#         self.resolved_at = timezone.now()
#         self.save(update_fields=[
#             'status', 'resolution', 'admin_notes', 'resolved_by', 'resolved_at'
#         ])
        
#         # Handle refund or other actions for client resolution
#         self._handle_client_resolution()
        
#         self.send_resolution_notification()
#         return True
    
#     def resolve_for_expert(self, admin_user, resolution, admin_notes=None):
#         """
#         Resolve the dispute in favor of the expert.
#         """
#         if not admin_user.is_staff:
#             return False
        
#         self.status = DisputeStatusChoices.RESOLVED_FOR_EXPERT
#         self.resolution = resolution
#         self.admin_notes = admin_notes
#         self.resolved_by = admin_user
#         self.resolved_at = timezone.now()
#         self.save(update_fields=[
#             'status', 'resolution', 'admin_notes', 'resolved_by', 'resolved_at'
#         ])
        
#         # Handle payment release or other actions for expert resolution
#         self._handle_expert_resolution()
        
#         self.send_resolution_notification()
#         return True
    
#     def close_dispute(self, admin_user, resolution, admin_notes=None):
#         """
#         Close the dispute without resolving in favor of either party.
#         """
#         if not admin_user.is_staff:
#             return False
        
#         self.status = DisputeStatusChoices.CLOSED
#         self.resolution = resolution
#         self.admin_notes = admin_notes
#         self.resolved_by = admin_user
#         self.resolved_at = timezone.now()
#         self.save(update_fields=[
#             'status', 'resolution', 'admin_notes', 'resolved_by', 'resolved_at'
#         ])
        
#         self.send_resolution_notification()
#         return True
    
#     def _handle_client_resolution(self):
#         """
#         Handle actions needed when resolving in favor of client.
#         """
#         # Update service request status
#         service_request = self.service_request
        
#         # If this is a payment dispute, handle refund
#         if self.dispute_type == DisputeTypeChoices.PAYMENT:
#             payment = service_request.payments.filter(status="in_escrow").first()
#             if payment:
#                 payment.refund_to_client()
        
#         # Mark service request as cancelled
#         service_request.mark_as_cancelled(reason=f"Cancelled due to dispute resolution: {self.resolution}")
    
#     def _handle_expert_resolution(self):
#         """
#         Handle actions needed when resolving in favor of expert.
#         """
#         # Update service request status
#         service_request = self.service_request
        
#         # If this is a payment dispute, release payment to expert
#         if self.dispute_type == DisputeTypeChoices.PAYMENT:
#             payment = service_request.payments.filter(status="in_escrow").first()
#             if payment:
#                 payment.release_funds()
        
#         # If service was completed, mark as confirmed
#         if service_request.expert_completed:
#             service_request.confirm_service()
    
#     def send_dispute_notification(self):
#         """
#         Send notifications to all parties when a dispute is created.
#         """
#         # Determine who raised the dispute
#         is_client = self.raised_by == self.service_request.client
#         other_party = self.service_request.expert if is_client else self.service_request.client
        
#         # Notify the other party
#         subject = f"Dispute Opened for Service: {self.service_request}"
#         message = f"""
#         A dispute has been opened for the service request: {self.service_request}
        
#         Dispute Type: {self.get_dispute_type_display()}
#         Description: {self.description}
        
#         Please log in to provide your statement regarding this dispute.
#         """
#         send_email_task.delay(subject, message, other_party.email)
        
#         # Notify admins
#         admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
#         admin_subject = f"New Dispute: {self.service_request}"
#         admin_message = f"""
#         A new dispute has been opened:
        
#         Service Request: {self.service_request}
#         Raised By: {self.raised_by.username} ({'Client' if is_client else 'Expert'})
#         Dispute Type: {self.get_dispute_type_display()}
#         Description: {self.description}
        
#         Please review this dispute in the admin panel.
#         """
#         for email in admin_emails:
#             send_email_task.delay(admin_subject, admin_message, email)
    
#     def send_statement_notification(self, is_client):
#         """
#         Send notification when a statement is added.
#         """
#         statement = self.client_statement if is_client else self.expert_statement
#         statement_by = self.service_request.client if is_client else self.service_request.expert
#         notify_user = self.service_request.expert if is_client else self.service_request.client
        
#         subject = f"New Statement Added to Dispute: {self.service_request}"
#         message = f"""
#         A new statement has been added to the dispute for service request: {self.service_request}
        
#         Statement by: {statement_by.username} ({'Client' if is_client else 'Expert'})
#         Statement: {statement}
        
#         Please log in to review this statement and respond if necessary.
#         """
#         send_email_task.delay(subject, message, notify_user.email)
        
#         # Also notify admins
#         admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
#         for email in admin_emails:
#             send_email_task.delay(subject, message, email)
    
#     def send_status_update_notification(self):
#         """
#         Send notification when dispute status changes.
#         """
#         subject = f"Dispute Status Updated: {self.service_request}"
#         message = f"""
#         The status of your dispute for service request: {self.service_request} has been updated.
        
#         New Status: {self.get_status_display()}
        
#         Please log in to check the details.
#         """
        
#         # Notify both parties
#         send_email_task.delay(subject, message, self.service_request.client.email)
#         send_email_task.delay(subject, message, self.service_request.expert.email)
    
#     def send_resolution_notification(self):
#         """
#         Send notification when dispute is resolved.
#         """
#         subject = f"Dispute Resolved: {self.service_request}"
#         message = f"""
#         The dispute for service request: {self.service_request} has been resolved.
        
#         Resolution: {self.get_status_display()}
#         Details: {self.resolution}
        
#         Please log in to check the details.
#         """
        
#         # Notify both parties
#         send_email_task.delay(subject, message, self.service_request.client.email)
#         send_email_task.delay(subject, message, self.service_request.expert.email)
    
#     @classmethod
#     def get_disputes_by_status(cls, status, user=None):
#         """
#         Get disputes by status with optional user filtering.
#         """
#         queryset = cls.objects.filter(status=status).select_related(
#             'service_request', 'raised_by', 'resolved_by'
#         )
        
#         if user:
#             if user.is_staff:
#                 # Admins can see all disputes
#                 return queryset
#             else:
#                 # Regular users can only see disputes for their service requests
#                 return queryset.filter(
#                     models.Q(service_request__client=user) | 
#                     models.Q(service_request__expert=user)
#                 )
        
#         return queryset
    
#     @classmethod
#     def get_open_disputes(cls, user=None):
#         """
#         Get all open disputes.
#         """
#         return cls.get_disputes_by_status(DisputeStatusChoices.OPEN, user)
    
#     @classmethod
#     def get_under_review_disputes(cls, user=None):
#         """
#         Get all disputes under review.
#         """
#         return cls.get_disputes_by_status(DisputeStatusChoices.UNDER_REVIEW, user)
    
#     @classmethod
#     def get_resolved_disputes(cls, user=None):
#         """
#         Get all resolved disputes (both for client and expert).
#         """
#         queryset = cls.objects.filter(
#             status__in=[
#                 DisputeStatusChoices.RESOLVED_FOR_CLIENT,
#                 DisputeStatusChoices.RESOLVED_FOR_EXPERT,
#                 DisputeStatusChoices.CLOSED
#             ]
#         ).select_related('service_request', 'raised_by', 'resolved_by')
        
#         if user:
#             if user.is_staff:
#                 # Admins can see all disputes
#                 return queryset
#             else:
#                 # Regular users can only see disputes for their service requests
#                 return queryset.filter(
#                     models.Q(service_request__client=user) | 
#                     models.Q(service_request__expert=user)
#                 )
        
#         return queryset
    
#     @classmethod
#     def get_user_disputes(cls, user):
#         """
#         Get all disputes related to a specific user.
#         """
#         if not user:
#             return cls.objects.none()
        
#         if user.is_staff:
#             # Admins can see all disputes
#             return cls.objects.all().select_related(
#                 'service_request', 'raised_by', 'resolved_by'
#             )
        
#         # Regular users can only see disputes for their service requests
#         return cls.objects.filter(
#             models.Q(service_request__client=user) | 
#             models.Q(service_request__expert=user)
#         ).select_related('service_request', 'raised_by', 'resolved_by')
    
#     @classmethod
#     def get_service_request_disputes(cls, service_request):
#         """
#         Get all disputes for a specific service request.
#         """
#         return cls.objects.filter(
#             service_request=service_request
#         ).select_related('raised_by', 'resolved_by')


