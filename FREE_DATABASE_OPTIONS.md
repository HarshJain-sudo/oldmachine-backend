# Free Database Options for Beta Environment

## Recommended Free Databases

### 1. **SQLite** (Current - Best for Local Development) ✅
- **Cost**: Free
- **Setup**: None required (already working)
- **Best for**: Local development, testing
- **Limitations**: Single file, not suitable for high concurrency

**Status**: Already configured and working!

### 2. **Supabase PostgreSQL** (Recommended for Cloud) ⭐
- **Cost**: Free tier available
- **Features**: 
  - 500 MB database storage
  - 2 GB bandwidth
  - PostgreSQL 15
  - Free forever tier
- **Setup**: 5 minutes
- **Best for**: Production-like testing, team collaboration

**Get started**: https://supabase.com

### 3. **ElephantSQL** (Easy PostgreSQL)
- **Cost**: Free tier available
- **Features**:
  - 20 MB database storage
  - PostgreSQL 15
  - Free tier available
- **Setup**: Very simple
- **Best for**: Quick PostgreSQL setup

**Get started**: https://www.elephantsql.com

### 4. **Railway PostgreSQL**
- **Cost**: Free tier with $5 credit monthly
- **Features**: 
  - PostgreSQL
  - Easy deployment
  - Good free tier
- **Best for**: Full-stack projects

**Get started**: https://railway.app

### 5. **Neon PostgreSQL**
- **Cost**: Free tier available
- **Features**:
  - Serverless PostgreSQL
  - 0.5 GB storage
  - Auto-scaling
- **Best for**: Modern serverless architecture

**Get started**: https://neon.tech

## Quick Setup Guide

### Option A: Keep SQLite (Recommended for Now)
✅ Already working - no changes needed!

### Option B: Supabase (Recommended for Cloud)

1. **Sign up**: https://supabase.com
2. **Create a new project**
3. **Get connection string** from Project Settings > Database
4. **Update settings** (see configuration below)

### Option C: ElephantSQL (Easiest)

1. **Sign up**: https://www.elephantsql.com
2. **Create instance** (select Tiny Turtle - Free)
3. **Copy connection URL**
4. **Update settings** (see configuration below)

## Configuration

### For Supabase/ElephantSQL/Any PostgreSQL Cloud Service

Update `oldmachine_backend/settings/beta.py`:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'your_db_name'),
        'USER': os.environ.get('DB_USER', 'your_db_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password'),
        'HOST': os.environ.get('DB_HOST', 'your_host.supabase.co'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',  # Required for cloud databases
        },
    }
}
```

Or use connection string:

```python
import os
import dj_database_url

# Parse connection string from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_beta.sqlite3',
        }
    }
```

## Recommendation

**For now**: Keep SQLite (already working, zero setup)

**For production/testing**: Use **Supabase** (best free tier, easy setup)

## Comparison

| Database | Free Tier | Setup Time | Best For |
|----------|-----------|------------|----------|
| SQLite | ✅ Unlimited | 0 minutes | Local dev |
| Supabase | 500 MB | 5 minutes | Cloud testing |
| ElephantSQL | 20 MB | 3 minutes | Quick PostgreSQL |
| Railway | $5 credit | 10 minutes | Full projects |
| Neon | 0.5 GB | 5 minutes | Serverless |

