from django.db import models


class StatusChoices(models.TextChoices):
    STATUS_PENDING = 'pending', 'Pending'
    STATUS_APPROVED = 'approved', 'Approved'
    STATUS_REJECTED = 'rejected', 'Rejected'