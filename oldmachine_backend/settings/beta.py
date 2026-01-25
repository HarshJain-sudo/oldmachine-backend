"""
Beta environment settings for oldmachine_backend project.
"""

import os

# Import base settings
from .base import *  # noqa: F403, F401

DEBUG = True

# Allow Vercel domains and localhost
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost,0.0.0.0'
).split(',')

# Database Configuration
# Option 1: SQLite (default for beta - no setup required) ✅ RECOMMENDED
# Option 2: PostgreSQL Cloud (Supabase, ElephantSQL, etc.)
# Option 3: Local PostgreSQL

# Database Configuration
# Currently using Supabase PostgreSQL
# To switch back to SQLite, comment PostgreSQL and uncomment SQLite below

# PostgreSQL Cloud Database (Supabase)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '4Bth38seXu/S@x@'),
        'HOST': os.environ.get('DB_HOST', 'db.wdcczvjigwrvdhzzpjwl.supabase.co'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',  # Required for Supabase
        },
    }
}

# SQLite Database (Fallback - Uncomment to use SQLite instead)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db_beta.sqlite3',  # noqa: F405
#     }
# }

# OTP Configuration
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6

# OTP Service (mock for beta - use actual SMS service in prod)
OTP_SERVICE_ENABLED = False  # Set to True when SMS service is configured

# Logging
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
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
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

