"""
Custom permissions for olmachine_seller_portal app.
"""

from rest_framework import permissions
from olmachine_seller_portal.models import SellerProfile


class IsSeller(permissions.BasePermission):
    """
    Permission class to check if user is a seller.
    """

    def has_permission(self, request, view):
        """
        Check if user has seller permission.

        Args:
            request: HTTP request object
            view: API view instance

        Returns:
            bool: True if user is a seller
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has a seller profile
        return SellerProfile.objects.filter(user=request.user).exists()


class IsAdminOrTeam(permissions.BasePermission):
    """
    Permission class to check if user is admin or team member.
    """

    def has_permission(self, request, view):
        """
        Check if user has admin or team permission.

        Args:
            request: HTTP request object
            view: API view instance

        Returns:
            bool: True if user is admin or staff
        """
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.is_staff or request.user.is_superuser


class IsSellerOrReadOnly(permissions.BasePermission):
    """
    Permission class: sellers can edit, others can only read.
    """

    def has_permission(self, request, view):
        """
        Check if user has permission.

        Args:
            request: HTTP request object
            view: API view instance

        Returns:
            bool: True if permission granted
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        return SellerProfile.objects.filter(user=request.user).exists()

