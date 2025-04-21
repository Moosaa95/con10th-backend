import os
from celery import Celery
from django.conf import settings

# Set default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coronith.settings.development")

app = Celery("coronith")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in installed Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
