# apps/projects/models.py
from django.db import models
from django.conf import settings
from commons.mixins import ModelMixin

class Project(ModelMixin):
    """
    Project created when a client hires an expert.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=255)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='client_projects'
    )
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='expert_projects'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class Review(ModelMixin):
    """
    Review left by a client for an expert after project completion.
    """
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='given_reviews'
    )
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_reviews'
    )
    rating = models.PositiveSmallIntegerField()  # 1-5 stars
    comment = models.TextField()
    
    def __str__(self):
        return f"Review for {self.project.title}"