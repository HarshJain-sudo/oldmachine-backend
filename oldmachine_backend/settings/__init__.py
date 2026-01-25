"""Settings module for environment-based configuration."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Load environment variables from .env file (for local development)
# This automatically loads .env file if it exists
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    ENV_FILE = BASE_DIR / '.env'
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
        print(f"✅ Loaded environment variables from {ENV_FILE}")
except ImportError:
    # python-dotenv not installed, will use os.environ directly
    # This is fine for Vercel where env vars are set in dashboard
    pass
except Exception as e:
    # If .env file has issues, continue without it
    print(f"⚠️  Warning: Could not load .env file: {e}")

# Import base settings first
from .base import *  # noqa: F403, F401


def get_environment():
    """Get current environment from DJANGO_ENV variable."""
    env = os.environ.get('DJANGO_ENV', 'local').lower()
    if env not in ['local', 'beta', 'prod']:
        raise ImproperlyConfigured(
            f"DJANGO_ENV must be 'local', 'beta', or 'prod', got '{env}'"
        )
    return env


ENVIRONMENT = get_environment()

if ENVIRONMENT == 'local':
    from .local import *  # noqa: F403, F401
elif ENVIRONMENT == 'beta':
    from .beta import *  # noqa: F403, F401
elif ENVIRONMENT == 'prod':
    from .prod import *  # noqa: F403, F401
