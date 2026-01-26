"""
Custom permissions for olmachine_products app.
"""

from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser


class AllowAnyOrValidToken(permissions.BasePermission):
    """
    Permission class that allows:
    - Public access if no token is provided
    - Validates token if provided and returns 401 if invalid
    - Allows access if token is valid
    
    This ensures that if a client sends an Authorization header,
    it must be valid, otherwise a 401 error is returned.
    """

    def has_permission(self, request, view):
        """
        Check if request has permission.

        Args:
            request: HTTP request object
            view: API view instance

        Returns:
            bool: True if permission granted

        Raises:
            AuthenticationFailed: If invalid token is provided
        """
        # Check if Authorization header is present
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        # If no auth header, allow public access
        if not auth_header:
            return True

        # If auth header exists, validate that authentication succeeded
        # Check if user is authenticated (not AnonymousUser)
        if (
            isinstance(request.user, AnonymousUser) or
            not request.user.is_authenticated
        ):
            # Authorization header was provided but authentication failed
            # This means the token is invalid or expired
            raise AuthenticationFailed(
                detail='Invalid or expired access token.',
                code='authentication_failed'
            )

        # User is authenticated with valid token, allow access
        return True

