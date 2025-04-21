from django.db import models

class UserRoles(models.TextChoices):
    """Defines the different user roles in the system."""
    CLIENT_USER = "client", "Client"
    EXPERT_USER = "expert", "Expert"
    STAFF = "staff", "Staff"
    ADMIN = "admin", "Admin"

class EVENTTYPES(models.TextChoices):
    SENT = "sent", "Sent"
    VERIFIED = "verified", "Verified"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"


class GENDERS(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"