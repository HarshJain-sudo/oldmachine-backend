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

# Database Configuration
# Option 1: SQLite (default for beta - no setup required) ✅ RECOMMENDED
# Option 2: PostgreSQL Cloud (Supabase, ElephantSQL, etc.)
# Option 3: Local PostgreSQL

# Database Configuration
# Currently using Supabase PostgreSQL
# To switch back to SQLite, comment PostgreSQL and uncomment SQLite below

# PostgreSQL Cloud Database (Supabase)
# IMPORTANT: For Vercel serverless, use Supabase Connection Pooler to avoid IPv6 issues
# 
# The error "Cannot assign requested address" is caused by IPv6 connection attempts
# that Vercel serverless functions don't support well.
#
# Solution: Use Supabase Connection Pooler (port 6543)
# 1. Go to Supabase Dashboard → Settings → Database → Connection Pooling
# 2. Copy the "Connection Pooler" host (format: aws-0-us-east-1.pooler.supabase.com)
# 3. Set DB_HOST to the pooler host in Vercel environment variables
# 4. Set DB_PORT to 6543 in Vercel environment variables
#
# Direct connection (port 5432) may fail with IPv6 on Vercel serverless

db_host = os.environ.get('DB_HOST', 'db.wdcczvjigwrvdhzzpjwl.supabase.co')
db_port = os.environ.get('DB_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '4Bth38seXu/S@x@'),
        'HOST': db_host,
        'PORT': db_port,
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',  # Required for Supabase
        },
        # Disable persistent connections for serverless (critical!)
        # Serverless functions should close connections after each request
        'CONN_MAX_AGE': 0,
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

