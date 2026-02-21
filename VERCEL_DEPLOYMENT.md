# Deploy Django to Vercel - Beta Environment

## Important Note

Vercel is primarily designed for serverless functions. For Django, consider:
- **Railway** (Recommended for Django)
- **Render** (Free tier available)
- **Fly.io** (Good for Django)
- **Heroku** (Paid)

However, Vercel CAN work with Django using serverless functions.

## Prerequisites

1. Vercel account: https://vercel.com
2. Vercel CLI installed: `npm i -g vercel`
3. Git repository (GitHub/GitLab/Bitbucket)

## Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

## Step 2: Configure for Vercel

The following files are already created:
- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function handler

## Step 3: Set Environment Variables

You need to set these in Vercel dashboard:

### Required Environment Variables:

Beta uses **DATABASE_URL** only (e.g. AWS RDS PostgreSQL):

```bash
DJANGO_ENV=beta
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://USER:PASSWORD@your-rds-endpoint.region.rds.amazonaws.com:5432/DBNAME
```

Optional for RDS SSL: `DB_SSLMODE=require`

### Optional (if using):
```bash
ALLOWED_HOSTS=your-vercel-domain.vercel.app,localhost
```

## Step 4: Deploy to Vercel

### Method 1: Using Vercel CLI

```bash
# Login to Vercel
vercel login

# Deploy (first time - will ask questions)
vercel

# Deploy to production
vercel --prod
```

### Method 2: Using GitHub Integration

1. Push your code to GitHub
2. Go to https://vercel.com
3. Click "New Project"
4. Import your GitHub repository
5. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty or `pip install -r requirements.txt`)
   - **Output Directory**: (leave empty)
6. Add environment variables (from Step 3)
7. Click "Deploy"

## Step 5: Update Settings for Vercel

Vercel provides environment variables automatically. Make sure your `beta.py` uses:

```python
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost'
).split(',')
```

## Step 6: Migrations (automatic on deploy)

Migrations run **automatically** during each Vercel build. This is configured in `vercel.json`:

```json
"buildCommand": "python manage.py migrate --noinput"
```

- **When**: After dependencies are installed and before the serverless function is deployed.
- **Requirement**: `DATABASE_URL` must be set in Vercel (Project → Settings → Environment Variables) and your database must accept connections from Vercel’s build network. If the DB is not reachable during build, the deployment will fail.
- **Manual run** (if needed): `vercel env pull .env.local` then `vercel exec -- python manage.py migrate --noinput`

## Alternative: Use Railway (Recommended for Django)

Railway is better suited for Django:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variables
6. Railway auto-detects Django and deploys

## Troubleshooting

### Issue: "Module not found"
- Make sure all dependencies are in `requirements.txt`
- Vercel installs from `requirements.txt` automatically

### Issue: "Database connection failed"
- Check environment variables in Vercel dashboard
- Verify Supabase allows connections from Vercel IPs

### Issue: "Static files not found"
- Configure static file serving (Vercel handles this automatically)

## Post-Deployment

1. **Migrations**: Run automatically on each deploy (see Step 6). To run manually: `vercel exec -- python manage.py migrate --noinput`.

2. **Create superuser**:
   ```bash
   vercel exec -- python manage.py createsuperuser
   ```

3. **Populate sample data** (optional):
   ```bash
   vercel exec -- python manage.py populate_sample_data
   ```

## Vercel Limitations for Django

- Serverless functions have execution time limits
- Cold starts can be slow
- Not ideal for long-running processes
- Database connections need to be managed carefully

## Recommendation

For Django projects, consider:
- **Railway**: https://railway.app (Best for Django)
- **Render**: https://render.com (Free tier)
- **Fly.io**: https://fly.io (Good performance)

Would you like me to set up Railway deployment instead? It's much easier for Django!

