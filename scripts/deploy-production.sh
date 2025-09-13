#!/bin/bash

# Deploy to Production Script
# This helps you safely deploy to production after testing on staging

echo "🚀 Deploying to PRODUCTION environment..."
echo ""

# Safety check
echo "⚠️  PRODUCTION DEPLOYMENT CHECK:"
echo "   Have you tested on staging? (https://ultrai-staging-api.onrender.com)"
read -p "   Continue with production deployment? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    echo "💡 Test on staging first with: ./scripts/deploy-staging.sh"
    exit 1
fi

# Get current commit hash
current_commit=$(git rev-parse --short HEAD)
echo ""
echo "📍 Current commit: $current_commit"
echo "📝 Commit message: $(git log -1 --pretty=%B)"
echo ""

# Show what will be deployed
echo "📋 Changes in this deployment:"
echo "--------------------------------"
# Show commits since last tag (or last 5 if no tags)
if git describe --tags --abbrev=0 2>/dev/null; then
    last_tag=$(git describe --tags --abbrev=0)
    git log --oneline $last_tag..HEAD
else
    git log --oneline -5
fi
echo "--------------------------------"
echo ""

# Final confirmation
read -p "Deploy commit $current_commit to PRODUCTION? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Tag this deployment
tag_name="deploy-$(date +%Y%m%d-%H%M%S)"
echo ""
echo "🏷️  Creating deployment tag: $tag_name"
git tag -a "$tag_name" -m "Production deployment on $(date)"
git push origin "$tag_name"

echo ""
echo "✅ Tagged deployment!"
echo ""
echo "📋 MANUAL STEPS REQUIRED:"
echo "1. Go to: https://dashboard.render.com"
echo "2. Select the 'ultrai-core' service"
echo "3. Go to 'Settings' → 'Build & Deploy'"
echo "4. Click 'Manual Deploy'"
echo "5. Select commit: $current_commit"
echo "6. Click 'Deploy'"
echo ""
echo "🌐 Production URL: https://ultrai-core.onrender.com"
echo ""
echo "💡 After deployment completes, verify at:"
echo "   https://ultrai-core.onrender.com/api/health"
echo ""
echo "🔖 To rollback to previous deployment, use:"
echo "   git checkout $last_tag"