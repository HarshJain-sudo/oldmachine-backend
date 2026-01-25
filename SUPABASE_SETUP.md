# Supabase Setup Guide

## Step-by-Step Instructions

### Step 1: Sign Up for Supabase

1. Go to **https://supabase.com**
2. Click **"Start your project"** or **"Sign up"**
3. Sign up with:
   - GitHub (recommended)
   - Google
   - Email

### Step 2: Create a New Project

1. Click **"New Project"** button
2. Fill in the details:
   - **Name**: `oldmachine-backend` (or any name you prefer)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you (e.g., `Southeast Asia (Singapore)`)
   - **Pricing Plan**: Select **"Free"** tier
3. Click **"Create new project"**
4. Wait 2-3 minutes for project to be created

### Step 3: Get Database Connection Details

1. You're already on the **Database Settings** page (good!)
2. Look for **"Connection string"** or **"Connection info"** section
   - It might be in a different tab or section
   - Sometimes it's under **"Connection Pooling"** tab
3. If you don't see it, try:
   - Click on **"Connection Pooling"** tab (if available)
   - Or go to: **Project Settings** → **Database** → Look for connection details
4. You need these values:
   - **Host**: `db.xxxxx.supabase.co` (or similar)
   - **Database name**: Usually `postgres`
   - **Port**: `5432`
   - **User**: Usually `postgres`
   - **Password**: Click **"Reset database password"** if you forgot it, or use the one you set

**Alternative**: Look for a **"Connection string"** that looks like:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

### Step 4: Copy Connection String (Easier Method)

1. In the **"Connection string"** section
2. Find **"URI"** tab
3. Copy the connection string (it looks like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

### Step 5: Configure Django Settings

1. **Edit** `oldmachine_backend/settings/beta.py`

2. **Comment out SQLite** and **uncomment PostgreSQL**:

```python
# SQLite Database (Default - Free, No Setup Required)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db_beta.sqlite3',
#     }
# }

# PostgreSQL Cloud Database (Supabase)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_supabase_password'),
        'HOST': os.environ.get('DB_HOST', 'db.xxxxx.supabase.co'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'require',  # Required for Supabase
        },
    }
}
```

3. **Set environment variables** (recommended for security):

```bash
export DB_NAME=postgres
export DB_USER=postgres
export DB_PASSWORD=your_supabase_password_here
export DB_HOST=db.xxxxx.supabase.co
export DB_PORT=5432
```

Or create a `.env` file in project root:

```bash
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password_here
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
```

### Step 6: Test Connection

```bash
cd /home/nxtwave/backend_projects/oldmachine-backend
source venv/bin/activate
export DJANGO_ENV=beta

# Test connection
python manage.py dbshell
# If it connects, type \q to exit
```

### Step 7: Run Migrations

```bash
# Make sure you're in the project directory
export DJANGO_ENV=beta

# Run migrations to create tables in Supabase
python manage.py migrate
```

### Step 8: Populate Sample Data (Optional)

```bash
python manage.py populate_sample_data
```

### Step 9: Create Admin User

```bash
python manage.py createsuperuser
```

### Step 10: Start Server

```bash
python manage.py runserver
```

## Quick Reference: What You Need from Supabase

From Supabase dashboard → Settings → Database:

- **Host**: `db.xxxxx.supabase.co`
- **Database**: `postgres`
- **Port**: `5432`
- **User**: `postgres`
- **Password**: (the one you set when creating project)

## Troubleshooting

### Connection Error: "SSL required"

Make sure `'sslmode': 'require'` is in OPTIONS.

### Connection Error: "Password authentication failed"

Double-check your password in Supabase Settings → Database.

### Connection Error: "Connection timeout"

- Check if your IP is allowed (Supabase allows all by default on free tier)
- Verify the host address is correct
- Check if port 5432 is accessible

### "No module named 'psycopg2'"

Already installed in requirements.txt, but if error occurs:
```bash
pip install psycopg2-binary
```

## Security Note

⚠️ **Never commit passwords to git!**

Use environment variables or `.env` file (add `.env` to `.gitignore`).

## Verify It's Working

1. Check Supabase Dashboard → Table Editor
2. You should see your Django tables:
   - `users`
   - `otps`
   - `categories`
   - `products`
   - etc.

## Switch Back to SQLite (if needed)

Just comment out PostgreSQL and uncomment SQLite in `beta.py`.

