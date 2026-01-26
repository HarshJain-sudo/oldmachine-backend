# How to Find Supabase Connection Details - Step by Step

## Method 1: Through Project Settings (Most Common)

1. **In the left sidebar**, click on the **gear icon** (⚙️) at the bottom
   - This opens "Project Settings"

2. In Project Settings, look for **"Database"** in the left menu
   - Click on **"Database"**

3. Scroll down to find **"Connection string"** section
   - It should show connection details

## Method 2: Through API Settings

1. Click **"Project Settings"** (gear icon)
2. Click **"API"** (instead of Database)
3. Look for **"Connection string"** or **"Database URL"**
4. You might see it under **"Config"** section

## Method 3: Check the URL

Look at your browser URL. It should be something like:
```
supabase.com/dashboard/project/[PROJECT-ID]/database/settings
```

The **PROJECT-ID** is part of your connection details.

## Method 4: Use Supabase CLI or Check Project Overview

1. Go back to your **project dashboard** (click project name in sidebar)
2. Look for **"Connection info"** or **"Database URL"** in the overview
3. Sometimes it's shown in a card/widget on the main dashboard

## Method 5: Create New Connection String

If you still can't find it:

1. Go to **Project Settings** → **Database**
2. Look for **"Connection Pooling"** section
3. There might be a **"New connection string"** or **"Generate connection string"** button
4. Click it to generate/view the connection string

## What the Connection String Looks Like

It will be in one of these formats:

**Format 1 (URI):**
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**Format 2 (Individual values):**
- Host: `db.xxxxx.supabase.co`
- Database: `postgres`
- Port: `5432`
- User: `postgres`
- Password: `[your-password]`

## Alternative: I Can Help You Build It

If you can find:
1. Your **project reference ID** (from the URL: `supabase.com/dashboard/project/[THIS-ID]/...`)
2. Your **database password** (the one you set when creating project)

I can help you construct the connection string!

## Quick Test: Check Your Project URL

Look at your browser address bar. What does it show?
- Is there a project ID like `wdcczvjigwrvdhzzpjwl`?
- Share that and I can help construct the host!

## Still Can't Find It?

Try this:
1. Click on **"Project Settings"** (gear icon at bottom of sidebar)
2. Look for any section that says:
   - "Database"
   - "Connection"
   - "API"
   - "Config"
3. Check each one for connection details

Let me know what sections you see in Project Settings and I'll guide you to the exact one!

