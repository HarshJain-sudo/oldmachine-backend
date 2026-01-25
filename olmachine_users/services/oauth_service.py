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

