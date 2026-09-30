from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler as rest_exception_handler


class APIConflict(APIException):
    status_code = 409
    default_detail = "The request conflicts with the current resource state."
    default_code = "conflict"


def uniform_exception_handler(exc, context):
    response = rest_exception_handler(exc, context)
    if response is None:
        return None

    original = response.data
    status_codes = {
        400: "invalid_request",
        401: "not_authenticated",
        403: "permission_denied",
        404: "not_found",
        409: "conflict",
    }
    code = status_codes.get(
        response.status_code, getattr(exc, "default_code", "request_error")
    )
    if isinstance(original, dict) and "detail" in original:
        message = str(original["detail"])
        details = None
    elif response.status_code == 400:
        message = "Request validation failed."
        details = original
    else:
        message = "Request failed."
        details = original

    response.data = {
        "error": {"code": code, "message": message, "details": details}
    }
    return response
