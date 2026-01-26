# Deploy Django to Railway (Recommended for Django)

Railway is much better suited for Django than Vercel. Here's how to deploy:

## Why Railway?

- ✅ Built for Django/Python apps
- ✅ Free tier available ($5 credit/month)
- ✅ Automatic deployments from GitHub
- ✅ Easy database integration
- ✅ No serverless limitations

## Step 1: Sign Up

1. Go to https://railway.app
2. Sign up with GitHub (recommended)

## Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway will auto-detect Django

## Step 3: Add Environment Variables

In Railway dashboard → Your Project → Variables:

```bash
DJANGO_ENV=beta
SECRET_KEY=your-secret-key-here
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=4Bth38seXu/S@x@
DB_HOST=db.wdcczvjigwrvdhzzpjwl.supabase.co
DB_PORT=5432
ALLOWED_HOSTS=*.railway.app,your-app-name.railway.app
```

## Step 4: Configure Build Settings

Railway auto-detects, but you can set:

- **Build Command**: (leave empty, Railway handles it)
- **Start Command**: `python manage.py migrate && python manage.py runserver 0.0.0.0:$PORT`
- **Python Version**: 3.12

## Step 5: Deploy

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Run migrations (if configured)
3. Start your Django app
4. Provide a public URL

## Step 6: Run Migrations

After first deployment:

1. Go to Railway dashboard
2. Click on your service
3. Open **"Deployments"** tab
4. Click **"View Logs"**
5. Or use Railway CLI:
   ```bash
   railway run python manage.py migrate
   ```

## Step 7: Create Admin User

```bash
railway run python manage.py createsuperuser
```

## Step 8: Populate Sample Data (Optional)

```bash
railway run python manage.py populate_sample_data
```

## Railway CLI (Optional)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Run commands
railway run python manage.py migrate
```

## Cost

- **Free tier**: $5 credit/month
- **Hobby plan**: $5/month (if you exceed free tier)
- Perfect for beta/testing!

## That's It!

Railway handles everything automatically. Much easier than Vercel for Django!

