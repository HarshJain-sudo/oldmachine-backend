# How to Get Supabase Connection Details

## You're on the Database Settings Page - Here's What to Do:

### Option 1: Find Connection String (Easiest)

1. On the Database Settings page, look for a section called:
   - **"Connection string"**
   - **"Connection info"**
   - **"Connection parameters"**

2. You might need to click on a tab like:
   - **"Connection Pooling"**
   - **"Connection Info"**

3. Look for a string that looks like:
   ```
   postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

### Option 2: Get Individual Values

If you see individual fields, you need:

1. **Host** or **Hostname**: 
   - Looks like: `db.xxxxx.supabase.co`
   - Or: `xxxxx.supabase.co`

2. **Database name**: 
   - Usually: `postgres`

3. **Port**: 
   - Usually: `5432`

4. **User** or **Username**: 
   - Usually: `postgres`

5. **Password**: 
   - The password you set when creating the project
   - If you forgot it, click **"Reset database password"** button

### Option 3: Check Project Settings

If you can't find it on the current page:

1. Click on **"Project Settings"** (gear icon) in the left sidebar
2. Go to **"Database"** section
3. Look for **"Connection string"** or **"Connection info"**

### What I Need From You

Once you find the connection details, share with me:

1. **Host**: `db.xxxxx.supabase.co`
2. **Password**: (the database password)

Or just copy the full connection string and I'll help you configure it!

## Quick Check

Can you see any of these on your screen?
- A section with "Connection string"
- A tab that says "Connection Pooling" or "Connection Info"
- Any text that contains "db." followed by ".supabase.co"

Let me know what you see and I'll guide you to the exact location!

