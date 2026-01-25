# Deploy to Vercel - Step by Step Guide

## ⚠️ Important: Vercel Limitations for Django

Vercel is designed for serverless functions, not full Django apps. Consider:
- **Railway** (Best for Django) - See `RAILWAY_DEPLOYMENT.md`
- **Render** (Free tier)
- **Fly.io**

But if you want to proceed with Vercel, here's how:

## Quick Deployment Steps

### Step 1: Push Code to GitHub

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### Step 2: Sign Up / Login to Vercel

1. Go to https://vercel.com
2. Sign up with GitHub (recommended)

### Step 3: Create New Project

1. Click **"New Project"**
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)

### Step 4: Add Environment Variables

In Vercel project → **Settings** → **Environment Variables**, add:

```bash
DJANGO_ENV=beta
SECRET_KEY=change-this-to-random-string
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=4Bth38seXu/S@x@
DB_HOST=db.wdcczvjigwrvdhzzpjwl.supabase.co
DB_PORT=5432
ALLOWED_HOSTS=*.vercel.app,your-app-name.vercel.app
```

**Important**: 
- Replace `your-app-name.vercel.app` with your actual Vercel domain
- Change `SECRET_KEY` to a random string

### Step 5: Deploy

Click **"Deploy"** button. Vercel will:
1. Install dependencies from `requirements.txt`
2. Build your project
3. Deploy to a URL like: `your-app.vercel.app`

### Step 6: Run Migrations

After deployment, you need to run migrations:

**Option A: Using Vercel CLI**
```bash
npm install -g vercel
vercel login
vercel link
vercel exec -- python manage.py migrate
```

**Option B: Using Vercel Dashboard**
1. Go to your project
2. Open **"Functions"** tab
3. Use the terminal/console to run commands

### Step 7: Create Admin User

```bash
vercel exec -- python manage.py createsuperuser
```

### Step 8: Test Your API

Your API will be available at:
```
https://your-app.vercel.app/api/marketplace/
```

Test endpoints:
```
https://your-app.vercel.app/api/marketplace/login_or_sign_up/v1/
https://your-app.vercel.app/api/marketplace/categories_details/get/v1/
```

## Files Created

✅ `vercel.json` - Vercel configuration
✅ `api/index.py` - Serverless function handler
✅ `.vercelignore` - Files to exclude

## Troubleshooting

### Database Connection Failed
- Verify all environment variables are set correctly
- Check Supabase allows connections from Vercel

### 500 Error
- Check Vercel logs: Dashboard → Deployments → View Logs
- Verify `DJANGO_ENV=beta` is set

### Module Not Found
- All dependencies must be in `requirements.txt`
- Vercel installs automatically

## Better Alternative: Railway

For Django, **Railway is recommended**:
- ✅ Built for Django
- ✅ Easier setup
- ✅ Better performance
- ✅ Free tier ($5 credit/month)

See `RAILWAY_DEPLOYMENT.md` for Railway setup.

## Next Steps After Deployment

1. ✅ Update `ALLOWED_HOSTS` with your Vercel domain
2. ✅ Run migrations
3. ✅ Create admin user
4. ✅ Test all API endpoints
5. ✅ Update frontend to use new API URL

