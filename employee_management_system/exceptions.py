from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import (APIException, PermissionDenied,
                                       ValidationError)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ValidationError):
            error_detail = exc.detail
            if isinstance(error_detail, dict):
                error_messages = [
                    ", ".join(messages) for messages in error_detail.values()
                ]
                error_message = "; ".join(error_messages)
            elif isinstance(error_detail, list):
                error_message = " ".join(error_detail)
            else:
                error_message = str(error_detail)

            response.data = {
                "status": "error",
                "code": 400,
                "message": error_message,
                "data": {},
            }
        elif isinstance(exc, PermissionDenied):
            response.data = {
                "status": "error",
                "code": 403,
                "message": str(exc.detail)
                or "You do not have permission to perform this action.",
                "data": {},
            }
        elif isinstance(response.data, dict) and "detail" in response.data:
            response.data = {
                "status": "error",
                "code": response.status_code,
                "message": response.data.get("detail", "An error occurred."),
                "data": {},
            }
        else:
            response.data = {
                "status": "error",
                "code": response.status_code,
                "message": "An unexpected error occurred.",
                "data": {},
            }
    else:
        if isinstance(exc, ObjectDoesNotExist):
            response = Response(
                {
                    "status": "error",
                    "code": 404,
                    "message": "Resource not found.",
                    "data": {},
                },
                status=404,
            )
        elif isinstance(exc, PermissionDenied):
            response = Response(
                {
                    "status": "error",
                    "code": 403,
                    "message": "You do not have permission to perform this action.",
                    "data": {},
                },
                status=403,
            )
        elif isinstance(exc, APIException):
            response = Response(
                {
                    "status": "error",
                    "code": exc.status_code,
                    "message": str(exc.detail),
                    "data": {},
                },
                status=exc.status_code,
            )
        else:
            response = Response(
                {
                    "status": "error",
                    "code": 500,
                    "message": "An unexpected error occurred.",
                    "data": {},
                },
                status=500,
            )

    return response
