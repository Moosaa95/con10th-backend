from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.types import ErrorResponse


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats serializer validation errors globally.
    """
    # Get the standard response
    response = exception_handler(exc, context)

    # Handle serializer validation errors specifically
    if isinstance(exc, ValidationError):
        formatted_errors = []
        for field, errors in exc.detail.items():
            for error in errors:
                formatted_errors.append(f"{field}: {error}")

        return Response(
            {"status": "error", "message": formatted_errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    return response




class APIExceptionFormatter(ExceptionFormatter):
    def format_error_response(self, error_response: ErrorResponse):
        error = error_response.errors[0]
        if error_response.type == "validation_error" and error.attr != "non_field_errors" and error.attr is not None:
            error_message = f"{error.attr}: {error.detail}"
        else:
            error_message = error.detail
        return {
            "status": False,
            "error_code": error.code,
            "message": error_message,
            "data": None,
        }
