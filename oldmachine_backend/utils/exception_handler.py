"""
Custom exception handler for REST Framework.

Provides consistent error response format across all APIs.
"""

import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.

    Args:
        exc: Exception instance
        context: Request context

    Returns:
        Response: Formatted error response
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'response': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            'http_status_code': response.status_code,
        }

        # Add res_status based on exception type
        if hasattr(exc, 'default_code'):
            custom_response_data['res_status'] = exc.default_code
        elif hasattr(exc, 'default_detail'):
            custom_response_data['res_status'] = (
                exc.default_detail.upper().replace(' ', '_')
            )
        else:
            custom_response_data['res_status'] = 'ERROR'

        logger.error(
            f"Exception occurred: {custom_response_data['res_status']} - "
            f"{custom_response_data['response']}"
        )

        return Response(custom_response_data, status=response.status_code)

    return response

