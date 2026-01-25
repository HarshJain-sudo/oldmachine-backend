# Database Configuration Guide

## Beta Environment Database Configuration

The beta environment database is configured in:
**`oldmachine_backend/settings/beta.py`**

### Current Configuration (SQLite - Default)

By default, beta uses SQLite which requires no setup:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_beta.sqlite3',
    }
}
```

**Location**: Database file is created at: `db_beta.sqlite3` in project root

### Switch to PostgreSQL for Beta

If you want to use PostgreSQL for beta environment:

1. **Edit** `oldmachine_backend/settings/beta.py`

2. **Comment out SQLite** and **uncomment PostgreSQL**:

```python
# SQLite Database (Default)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db_beta.sqlite3',
#     }
# }

# PostgreSQL Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'oldmachine_beta_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

3. **Set Environment Variables** (optional, or use defaults):

```bash
export DB_NAME=oldmachine_beta_db
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
```

4. **Create PostgreSQL Database**:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE oldmachine_beta_db;

# Exit
\q
```

5. **Run Migrations**:

```bash
export DJANGO_ENV=beta
python manage.py migrate
```

## Production Environment Database

Production database is configured in:
**`oldmachine_backend/settings/prod.py`**

It uses PostgreSQL and reads from environment variables.

## Quick Reference

| Environment | Database | Config File | Default DB Name |
|------------|----------|-------------|----------------|
| Beta | SQLite | `settings/beta.py` | `db_beta.sqlite3` |
| Beta | PostgreSQL | `settings/beta.py` | `oldmachine_beta_db` |
| Prod | PostgreSQL | `settings/prod.py` | `oldmachine_db` |

## Current Database Location

**SQLite (Beta)**: `/home/nxtwave/backend_projects/oldmachine-backend/db_beta.sqlite3`

To view database:
```bash
sqlite3 db_beta.sqlite3
.tables
.schema users
```

