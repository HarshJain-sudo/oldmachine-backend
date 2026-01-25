#!/bin/bash
# Script to push code to GitHub

echo "🚀 Pushing to GitHub..."
echo ""
echo "📋 Steps:"
echo "1. Make sure you've created the repository on GitHub:"
echo "   https://github.com/new"
echo "   Repository name: oldmachine-backend"
echo ""
echo "2. When prompted for credentials:"
echo "   Username: HarshJain-sudo"
echo "   Password: Use a Personal Access Token (not your password)"
echo ""
echo "   Create token at: https://github.com/settings/tokens"
echo "   Select scope: repo (full control)"
echo ""
read -p "Press Enter when ready to push..."

# Push to GitHub
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 View your repo: https://github.com/HarshJain-sudo/oldmachine-backend"
else
    echo ""
    echo "❌ Push failed. Please check:"
    echo "   1. Repository exists on GitHub"
    echo "   2. You have correct credentials"
    echo "   3. You have write access to the repository"
fi

