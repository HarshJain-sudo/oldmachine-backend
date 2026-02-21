"""
Production environment settings for oldmachine_backend project.
"""

from .base import *  # noqa: F403, F401
import os
from urllib.parse import urlparse, unquote

DEBUG = False

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost'
).split(',')

# Database: PostgreSQL via DATABASE_URL only (e.g. AWS RDS).
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('Set DATABASE_URL for production.')
try:
    parsed = urlparse(database_url)
    password = unquote(parsed.password) if parsed.password else ''
    _db_opts = {'connect_timeout': 10}
    if os.environ.get('DB_SSLMODE'):
        _db_opts['sslmode'] = os.environ.get('DB_SSLMODE')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': parsed.path[1:] if parsed.path else 'postgres',
            'USER': parsed.username,
            'PASSWORD': password,
            'HOST': parsed.hostname,
            'PORT': str(parsed.port or 5432),
            'OPTIONS': _db_opts,
        }
    }
except Exception as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(f'Invalid DATABASE_URL for production: {e}') from e

# OTP Configuration
OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_LENGTH = 6

# OTP Service (configure actual SMS service)
OTP_SERVICE_ENABLED = os.environ.get('OTP_SERVICE_ENABLED', 'False') == 'True'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

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
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',  # noqa: F405
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'olmachine_users': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'olmachine_products': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

