from django.conf import settings


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from accounts.utils import set_auth_cookies
from apps.accounts.serializers import CustomTokenObtainPairSerializer
# Create your views here.


class CustomTokenObtainView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:

            
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            if access_token and refresh_token:
                set_auth_cookies(response, access_token, refresh_token)
            
            response.data["status"] = True
        print("RESPONSE ", response)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """Handles token refresh by reading the refresh token from cookies if not provided in the request body."""

    def post(self, request, *args, **kwargs):
        """Overrides the default post method to get the refresh token from cookies if not provided."""
        
        # Fix: Ensure `request.data` is mutable (Django's `QueryDict` may be immutable)
        data = request.data.copy()

        # Fix: Use correct assignment syntax
        refresh_token = request.COOKIES.get(settings.AUTH_REFRESH_TOKEN_NAME)
        if refresh_token and 'refresh' not in data:
            data['refresh'] = refresh_token

        # Call the parent class's `post` method with the modified request data
        request._full_data = data  # Override request data
        response = super().post(request, *args, **kwargs)

        # Fix: Ensure access token is set correctly in cookies
        # if response.status_code == 200:
        #     access_token = response.data.get('access')
        #     if access_token:
        #         set_auth_cookies(response, access_token, refresh_token)  # Fix parameter order
        if response.status_code == 200:
            access_token = response.data.get("access")
            new_refresh_token = response.data.get("refresh")  # May not exist if rotation is disabled

            if access_token:
                # If refresh token rotation is enabled, update both cookies
                if new_refresh_token:
                    set_auth_cookies(response, access_token, new_refresh_token)
                else:
                    set_auth_cookies(response, access_token, refresh_token)  # Keep existing refresh token


        return response



class CustomTokenVerifyView(TokenVerifyView):
    """
    Custom token verification view to handle token verification.
    """

    def post(self, request, *args, **kwargs):
        """
        Handle token verification.
        """
        access_token = request.COOKIES.get(settings.AUTH_ACCESS_TOKEN_NAME)
        if access_token:
            data = request.data.copy()
            data['access'] = access_token
            request._full_data = data  # Override the request data safely

        return super().post(request, *args, **kwargs)