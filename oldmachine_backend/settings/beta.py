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
# The error "Tenant or user not found" means the connection pooler credentials are wrong.
# 
# Solution: Use Supabase Connection Pooler with correct credentials
# 1. Go to Supabase Dashboard → Settings → Database → Connection Pooling
# 2. Copy the "Connection Pooler" connection string (URI format)
# 3. Set DATABASE_URL in Vercel environment variables with the full connection string
#
# OR use individual variables (see format below)

# Try to use connection string first (recommended for pooler)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Parse connection string from Supabase Connection Pooler
    from urllib.parse import urlparse, unquote
    
    try:
        parsed = urlparse(database_url)
        # Extract password (may be URL encoded)
        password = unquote(parsed.password) if parsed.password else ''
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path[1:] if parsed.path else 'postgres',  # Remove leading /
                'USER': parsed.username,
                'PASSWORD': password,
                'HOST': parsed.hostname,
                'PORT': parsed.port or 6543,
                'OPTIONS': {
                    'connect_timeout': 10,
                    'sslmode': 'require',  # Required for Supabase
                },
                'CONN_MAX_AGE': 0,  # Disable persistent connections for serverless
            }
        }
    except Exception as e:
        # If parsing fails, fall back to individual variables
        print(f"Warning: Could not parse DATABASE_URL: {e}")
        database_url = None

# Fall back to individual variables if DATABASE_URL not set
if not database_url:
    db_host = os.environ.get('DB_HOST', 'db.wdcczvjigwrvdhzzpjwl.supabase.co')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'postgres')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', '4Bth38seXu/S@x@')
    
    # For connection pooler, user format is usually: postgres.[PROJECT-REF]
    # If DB_USER doesn't contain a dot and we're using pooler port, add project ref
    if db_port == '6543' and '.' not in db_user:
        # Try to extract project ref from host if it's the direct connection host
        if 'db.' in db_host and '.supabase.co' in db_host:
            project_ref = db_host.replace('db.', '').replace('.supabase.co', '')
            db_user = f'postgres.{project_ref}'
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
            'OPTIONS': {
                'connect_timeout': 10,
                'sslmode': 'require',  # Required for Supabase
            },
            'CONN_MAX_AGE': 0,  # Disable persistent connections for serverless
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

