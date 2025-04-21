from django.db import models
from django.utils import timezone
import uuid


class ModelMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = models.Manager()

    class Meta:
        abstract = True
