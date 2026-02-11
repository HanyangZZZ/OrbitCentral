"""
Custom DRF exception handler.

Adds structured error logging and includes the HTTP status code in every
error response body so clients can inspect it without parsing headers.
"""
import logging

from rest_framework.views import exception_handler

logger = logging.getLogger('api')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Inject status code into the response body
        response.data['status_code'] = response.status_code
        logger.warning(
            "API error %s: %s [view=%s]",
            response.status_code,
            response.data,
            context.get('view'),
        )
    else:
        # Unhandled exception — will return 500
        logger.exception(
            "Unhandled exception in %s", context.get('view'), exc_info=exc,
        )

    return response
