#!/bin/bash

# Deploy to Staging Script
# This happens automatically when you push to main, but this script lets you force it

echo "🚀 Deploying to STAGING environment..."
echo ""

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  Warning: You're on branch '$current_branch', not 'main'"
    echo "   Staging typically deploys from main branch"
    read -p "   Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Commit these changes first? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " commit_msg
        git add -A
        git commit -m "$commit_msg"
    else
        echo "❌ Please commit your changes before deploying"
        exit 1
    fi
fi

# Push to main (this triggers staging deployment)
echo "📤 Pushing to main branch..."
git push origin main

echo ""
echo "✅ Pushed to main branch!"
echo ""
echo "🔄 Render will automatically deploy to staging in a few minutes"
echo "📍 Check deployment at: https://dashboard.render.com"
echo "🌐 Staging URL: https://ultrai-staging-api.onrender.com"
echo ""
echo "💡 Tip: Use './scripts/check-deployment.sh staging' to monitor deployment"