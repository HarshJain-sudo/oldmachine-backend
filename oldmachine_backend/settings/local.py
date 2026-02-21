"""
Local development environment settings for oldmachine_backend project.

This environment is optimized for local development:
- Uses Django default SQLite (no external database)
- Debug mode enabled
- Detailed logging
- Relaxed security settings
"""

import os

# Import base settings
from .base import *  # noqa: F403, F401

DEBUG = True

# Allow all localhost variants
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,0.0.0.0,*'
).split(',')

# Database: Django default SQLite (local only)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

# OTP Configuration
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6

# OTP Service (disabled for local - uses hardcoded OTP)
OTP_SERVICE_ENABLED = False

# Logging - More verbose for local development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '{levelname} {asctime} {module} '
                '{process:d} {thread:d} {message}'
            ),
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # More verbose for local
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'olmachine_users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'olmachine_products': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

