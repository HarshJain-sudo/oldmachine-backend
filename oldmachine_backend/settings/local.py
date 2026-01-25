"""
Local development environment settings for oldmachine_backend project.

This environment is optimized for local development:
- Uses SQLite database (no external setup required)
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
    '127.0.0.1,localhost,0.0.0.0'
).split(',')

# Database Configuration
# Use SQLite for local development (simple, no setup required)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local.sqlite3',  # noqa: F405
    }
}

# Optional: Use PostgreSQL if DB_* env vars are set
# Uncomment below and comment SQLite above to use PostgreSQL
# if all(os.environ.get(k) for k in ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']):
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql',
#             'NAME': os.environ.get('DB_NAME', 'postgres'),
#             'USER': os.environ.get('DB_USER', 'postgres'),
#             'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#             'HOST': os.environ.get('DB_HOST', 'localhost'),
#             'PORT': os.environ.get('DB_PORT', '5432'),
#         }
#     }

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

