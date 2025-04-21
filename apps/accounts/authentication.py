from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CustomJWTAuthentication(JWTAuthentication):
    '''
    Custom JWT Authentication class to handle custom headers

    '''
    def authenticate(self, request):
        try:
            header = self.get_header(request) # Get the header from the request

            if header is None:
                # raw_token = self.COOKIES.get(settings.AUTH_ACCESS_TOKEN_NAME) # Get the token from the cookies
                raw_token = request.COOKIES.get(settings.AUTH_ACCESS_TOKEN_NAME) # Get the token from the cookies
            else:
                raw_token = self.get_raw_token(header)
            
            if raw_token is None:
                return None
            
            
            validated_token = self.get_validated_token(raw_token) # Validate the token


            return self.get_user(validated_token), validated_token # Return the user and the token
        
        except (InvalidToken, TokenError) as e:
            return None
        
        except Exception as e:
            return None
    