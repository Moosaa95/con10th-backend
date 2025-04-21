from django.conf import settings
from django.core.exceptions import ValidationError


def set_auth_cookies(response, access_token, refresh_token):
    """
    Set authentication cookies for access and refresh tokens on the response.

    Uses common cookie settings from Django settings and applies distinct
    max_age values for the access and refresh tokens.

    Args:
        response (HttpResponse): The response object to which cookies are added.
        access_token (str): The JWT access token.
        refresh_token (str): The JWT refresh token.

    Returns:
        HttpResponse: The response object with the authentication cookies set.
    """
    cookie_common = {
        'path': settings.AUTH_COOKIE_PATH,
        'secure': settings.AUTH_COOKIE_SECURE,
        'httponly': settings.AUTH_COOKIE_HTTP_ONLY,
        'samesite': settings.AUTH_COOKIE_SAMESITE,
    }

    response.set_cookie(
        settings.AUTH_ACCESS_TOKEN_NAME,
        access_token,
        max_age=settings.AUTH_COOKIE_ACCESS_TOKEN_MAX_AGE,
        **cookie_common
    )
    response.set_cookie(
        settings.AUTH_REFRESH_TOKEN_NAME,
        refresh_token,
        max_age=settings.AUTH_COOKIE_REFRESH_TOKEN_MAX_AGE,
        **cookie_common
    )
    return response



def _validate_photo(photo):
    """Validate photo file size and type."""
    if photo.size > 2 * 1024 * 1024:  # 2MB
        raise ValidationError("File size exceeds 2MB limit")
        
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    if photo.content_type not in allowed_types:
        raise ValidationError("File type not supported. Please upload JPEG or PNG")
