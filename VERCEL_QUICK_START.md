# Quick Start: Deploy to Vercel (Beta Environment)

## ⚠️ Important Note

**Vercel is NOT ideal for Django**. Consider **Railway** instead (see `RAILWAY_DEPLOYMENT.md`).

However, if you still want to use Vercel, follow these steps:

## Prerequisites

1. ✅ Code pushed to GitHub/GitLab/Bitbucket
2. ✅ Vercel account: https://vercel.com

## Step 1: Set Environment Variables in Vercel

1. Go to https://vercel.com
2. Create new project or select existing
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```
DJANGO_ENV=beta
SECRET_KEY=your-secret-key-change-this
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=4Bth38seXu/S@x@
DB_HOST=db.wdcczvjigwrvdhzzpjwl.supabase.co
DB_PORT=5432
ALLOWED_HOSTS=*.vercel.app,your-app-name.vercel.app
```

## Step 2: Deploy

### Option A: GitHub Integration (Recommended)

1. Push code to GitHub
2. Go to Vercel dashboard
3. Click **"New Project"**
4. Import your repository
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
6. Add environment variables (from Step 1)
7. Click **"Deploy"**

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

## Step 3: Run Migrations

After deployment, run migrations:

```bash
# Using Vercel CLI
vercel exec -- python manage.py migrate
```

Or use Vercel dashboard → Functions → Run command.

## Step 4: Create Admin User

```bash
vercel exec -- python manage.py createsuperuser
```

## Step 5: Populate Sample Data (Optional)

```bash
vercel exec -- python manage.py populate_sample_data
```

## Files Created for Vercel

- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Serverless function handler
- ✅ `.vercelignore` - Files to ignore

## Troubleshooting

### Database Connection Issues
- Verify environment variables in Vercel dashboard
- Check Supabase allows connections from Vercel IPs

### Module Not Found
- All dependencies must be in `requirements.txt`
- Vercel installs automatically

## ⚠️ Better Alternative: Railway

For Django, **Railway is much better**:
- Built for Django/Python
- Easier setup
- Better performance
- Free tier available

See `RAILWAY_DEPLOYMENT.md` for Railway setup (recommended).

