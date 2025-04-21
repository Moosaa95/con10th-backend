from .base import *


# Authentication Token Cookie Settings
AUTH_ACCESS_TOKEN_NAME = "access_token"  # Name of the access token cookie
AUTH_REFRESH_TOKEN_NAME = "refresh_token"  # Name of the refresh token cookie

# Cookie expiration time (in seconds)
AUTH_COOKIE_ACCESS_TOKEN_MAX_AGE = 60 * 15  # 15 minutes for access token
AUTH_COOKIE_REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # 7 days for refresh token

# Common Cookie Settings
AUTH_COOKIE_PATH = "/"  # Available across the entire domain
AUTH_COOKIE_SECURE = True  # Set to True in production (requires HTTPS)
AUTH_COOKIE_HTTP_ONLY = True  # Prevents JavaScript access (helps mitigate XSS)
AUTH_COOKIE_SAMESITE = "Lax"  # "Lax" allows safe cross-site use, "Strict" prevents CSRF risks
# AUTH_COOKIE_SAMESITE = "None"  # "Lax" allows safe cross-site use, "Strict" prevents CSRF risks
