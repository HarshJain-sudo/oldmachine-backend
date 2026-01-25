"""Settings module for environment-based configuration."""

import os

from django.core.exceptions import ImproperlyConfigured

# Import base settings first
from .base import *  # noqa: F403, F401


def get_environment():
    """Get current environment from DJANGO_ENV variable."""
    env = os.environ.get('DJANGO_ENV', 'beta').lower()
    if env not in ['beta', 'prod']:
        raise ImproperlyConfigured(
            f"DJANGO_ENV must be 'beta' or 'prod', got '{env}'"
        )
    return env


ENVIRONMENT = get_environment()

if ENVIRONMENT == 'beta':
    from .beta import *  # noqa: F403, F401
elif ENVIRONMENT == 'prod':
    from .prod import *  # noqa: F403, F401
