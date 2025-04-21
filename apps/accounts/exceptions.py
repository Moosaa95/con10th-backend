from rest_framework.exceptions import APIException

class CustomException(APIException):
    status_code = 400
    default_detail = 'A server error occurred.'
    default_code = 'error'

class UserNotFound(CustomException):
    status_code = 404
    default_detail = 'User not found.'
    default_code = 'user_not_found'

class UserAlreadyExists(CustomException):
    status_code = 400
    default_detail = 'User already exists.'
    default_code = 'user_already_exists'

class InvalidCredentials(CustomException):
    status_code = 400
    default_detail = 'Invalid credentials.'
    default_code = 'invalid_credentials'


class InvalidToken(CustomException):
    status_code = 400
    default_detail = 'Invalid token.'
    default_code = 'invalid_token'

class TokenExpired(CustomException):
    status_code = 400
    default_detail = 'Token expired.'
    default_code = 'token_expired'

