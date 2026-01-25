"""
Signal handlers for olmachine_users app.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from oauth2_provider.models import Application
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_oauth_application(sender, instance, created, **kwargs):
    """
    Create OAuth application for new users.

    Args:
        sender: Model class
        instance: User instance
        created: Whether instance was created
        **kwargs: Additional arguments
    """
    if created:
        Application.objects.get_or_create(
            user=instance,
            defaults={
                'name': f'{instance.phone_number} Application',
                'client_type': Application.CLIENT_CONFIDENTIAL,
                'authorization_grant_type': (
                    Application.GRANT_PASSWORD
                ),
            }
        )

