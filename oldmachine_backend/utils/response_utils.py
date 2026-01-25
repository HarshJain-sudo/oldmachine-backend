"""
Response utility functions for consistent API responses.
"""

from rest_framework.response import Response
from rest_framework import status


def success_response(data, http_status_code=status.HTTP_200_OK):
    """
    Create a success response.

    Args:
        data: Response data dictionary
        http_status_code: HTTP status code

    Returns:
        Response: Success response
    """
    return Response(data, status=http_status_code)


def error_response(
    message,
    res_status,
    http_status_code=status.HTTP_400_BAD_REQUEST
):
    """
    Create an error response with consistent format.

    Args:
        message: Error message
        res_status: Error status code (e.g., 'INVALID_PHONE_NUMBER')
        http_status_code: HTTP status code

    Returns:
        Response: Error response
    """
    return Response(
        {
            'response': message,
            'http_status_code': http_status_code,
            'res_status': res_status,
        },
        status=http_status_code
    )

