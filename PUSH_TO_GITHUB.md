# Push to GitHub Guide

## Option 1: Create New Repository on GitHub (Recommended)

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `oldmachine-backend`
3. Description: (optional)
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license
6. Click **Create repository**

### Step 2: Update Remote (if needed)
If you created a new repository with a different name or under a different account:

```bash
# Remove old remote
git remote remove origin

# Add new remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/oldmachine-backend.git
```

### Step 3: Push to GitHub

**Option A: Using Personal Access Token (HTTPS)**
```bash
# Push (GitHub will prompt for username and token)
git push -u origin main

# Username: Your GitHub username
# Password: Use a Personal Access Token (not your password)
#   Create token at: https://github.com/settings/tokens
#   Select scopes: repo (full control)
```

**Option B: Using SSH (Recommended)**
```bash
# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/oldmachine-backend.git

# Push
git push -u origin main
```

**Option C: Using GitHub CLI**
```bash
# If you have GitHub CLI installed
gh auth login
git push -u origin main
```

## Option 2: If Repository Already Exists

If you recreated the repository with the same name:

```bash
# Just push (will prompt for credentials)
git push -u origin main
```

## Verify Push

After pushing, check your repository:
- https://github.com/YOUR_USERNAME/oldmachine-backend

## Troubleshooting

### Authentication Issues
- **HTTPS**: Use Personal Access Token instead of password
- **SSH**: Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Repository Not Found
- Make sure the repository exists on GitHub
- Check the repository URL is correct
- Verify you have access to the repository

### Permission Denied
- Check if you have write access to the repository
- Verify your authentication credentials

