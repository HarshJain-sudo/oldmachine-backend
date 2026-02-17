"""
OAuth service for token generation.
"""

import logging
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class OAuthService:
    """Service for OAuth token management."""

    @staticmethod
    def get_or_create_application(user):
        """
        Get or create OAuth application for user.

        Args:
            user: User instance

        Returns:
            Application: OAuth application instance
        """
        application, created = Application.objects.get_or_create(
            user=user,
            defaults={
                'name': f'{user.phone_number} Application',
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': (
                    Application.GRANT_PASSWORD
                ),
            }
        )
        return application

    @staticmethod
    def generate_tokens(user):
        """
        Generate access and refresh tokens for user.

        Args:
            user: User instance

        Returns:
            dict: Dictionary with access_token and refresh_token
        """
        application = OAuthService.get_or_create_application(user)

        # Delete existing tokens for user
        AccessToken.objects.filter(user=user, application=application).delete()

        # Generate access token
        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=generate_token(),
            expires=timezone.now() + timedelta(
                seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
            ),
            scope='read write'
        )

        # Generate refresh token
        refresh_token = RefreshToken.objects.create(
            user=user,
            token=generate_token(),
            access_token=access_token,
            application=application
        )

        logger.info(f"Tokens generated for user {user.phone_number}")

        return {
            'access_token': access_token.token,
            'refresh_token': refresh_token.token,
        }

    @staticmethod
    def refresh_access_token(refresh_token_string):
        """
        Exchange a refresh token for a new access token.

        Args:
            refresh_token_string: The refresh token string from verify_otp.

        Returns:
            dict: Dictionary with access_token and refresh_token (same refresh
                  token string, valid for further refreshes).

        Raises:
            ValueError: When refresh token is missing, invalid, or revoked.
        """
        if not refresh_token_string or not str(refresh_token_string).strip():
            raise ValueError("Refresh token is required")

        refresh_token = RefreshToken.objects.filter(
            token=refresh_token_string.strip(),
            revoked__isnull=True,
        ).select_related('user', 'application', 'access_token').first()

        if not refresh_token:
            raise ValueError("Invalid or expired refresh token")

        user = refresh_token.user
        application = refresh_token.application
        old_access_token = refresh_token.access_token

        # Create new access token
        new_access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=generate_token(),
            expires=timezone.now() + timedelta(
                seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
            ),
            scope='read write',
        )

        # Revoke old access token (deletes it) and link refresh token to new one
        if old_access_token:
            old_access_token.revoke()
        refresh_token.access_token = new_access_token
        refresh_token.save(update_fields=['access_token'])

        logger.info(f"Refreshed access token for user {user.phone_number}")

        return {
            'access_token': new_access_token.token,
            'refresh_token': refresh_token.token,
        }

