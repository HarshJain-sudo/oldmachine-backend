"""
Beta environment settings for oldmachine_backend project.
"""

import os

# Import base settings
from .base import *  # noqa: F403, F401

DEBUG = True

# Allow Vercel domains and localhost
# Vercel provides multiple domain patterns:
# - Production: your-project.vercel.app
# - Preview: your-project-git-branch-username.vercel.app
# - Custom: your-custom-domain.com
#
# For beta environment (DEBUG=True), we allow all hosts using '*'
# to handle dynamic Vercel preview URLs that we can't predict.
# WARNING: This is only safe in beta/development, never in production!
vercel_url = os.environ.get('VERCEL_URL', '')
default_hosts = ['127.0.0.1', 'localhost', '0.0.0.0', '*']

# Add Vercel URL if provided
if vercel_url:
    # VERCEL_URL might include protocol, extract just the domain
    if '://' in vercel_url:
        vercel_url = vercel_url.split('://')[1]
    # Remove port if present
    if ':' in vercel_url:
        vercel_url = vercel_url.split(':')[0]
    default_hosts.append(vercel_url)

# Allow explicit ALLOWED_HOSTS override
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    # If ALLOWED_HOSTS is explicitly set, use it (don't use '*')
    env_hosts = [
        h.strip() for h in allowed_hosts_env.split(',') if h.strip()
    ]
    default_hosts.extend(env_hosts)
    ALLOWED_HOSTS = list(set(default_hosts))  # Remove duplicates
else:
    # For beta environment with DEBUG=True, allow all hosts
    # This handles dynamic Vercel preview URLs automatically
    # Django 4.2+ supports '*' in ALLOWED_HOSTS when DEBUG=True
    ALLOWED_HOSTS = ['*']

# Database: PostgreSQL via DATABASE_URL only (e.g. AWS RDS).
from urllib.parse import urlparse, unquote

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('Set DATABASE_URL for beta environment.')
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
            'CONN_MAX_AGE': 0,
        }
    }
except Exception as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(f'Invalid DATABASE_URL for beta: {e}') from e

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

