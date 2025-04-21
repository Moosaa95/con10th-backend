from .base import *

# settings.py

# Cookie settings
AUTH_COOKIE_SECURE = not DEBUG  # True in production, False in development
AUTH_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
AUTH_COOKIE_DOMAIN = 'localhost' if DEBUG else '.yourdomain.com'  # Adjust as needed

# Other settings remain the same
ACCESS_COOKIE_NAME = 'access'
REFRESH_COOKIE_NAME = 'refresh'
AUTH_COOKIE_ACCESS_MAX_AGE = 60 * 5  # 5 minutes
AUTH_COOKIE_REFRESH_MAX_AGE = 60 * 60 * 24 * 7  # 7 days