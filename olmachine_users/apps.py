"""App configuration for olmachine_users."""

from django.apps import AppConfig


class OlmachineUsersConfig(AppConfig):
    """Configuration for olmachine_users app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'olmachine_users'

    def ready(self):
        """Import signals when app is ready."""
        import olmachine_users.signals  # noqa: F401

