#!/bin/bash

# Initial setup script for deployment configuration
# Run this once to configure your deployment setup

echo "🛠️  UltraAI Deployment Setup"
echo "============================"
echo ""
echo "This script will help you configure your deployment setup."
echo ""

# Make all scripts executable
echo "📝 Making deployment scripts executable..."
chmod +x scripts/deploy-staging.sh
chmod +x scripts/deploy-production.sh
chmod +x scripts/check-deployment.sh
chmod +x scripts/check-render-services.sh
echo "✅ Scripts ready!"
echo ""

# Check current git status
echo "📊 Current Git Status:"
echo "  Branch: $(git branch --show-current)"
echo "  Remote: $(git remote get-url origin)"
echo ""

# Check which services are accessible
echo "🔍 Checking Render services..."
echo ""

services=(
    "ultrai-core.onrender.com|Production"
    "ultrai-staging-api.onrender.com|Staging"
    "ultrai-prod-api.onrender.com|Alternative Production"
)

active_services=0
for service_info in "${services[@]}"; do
    IFS='|' read -r service label <<< "$service_info"
    echo -n "  $label ($service): "
    response=$(curl -s -o /dev/null -w "%{http_code}" -I "https://$service/api/health" 2>/dev/null)
    if [ "$response" != "000" ] && [ "$response" != "502" ]; then
        echo "✅ Active (HTTP $response)"
        ((active_services++))
    else
        echo "❌ Not accessible"
    fi
done

echo ""
echo "📋 Recommended Setup:"
echo ""

if [ $active_services -eq 0 ]; then
    echo "⚠️  No services are currently accessible."
    echo "   Please check your Render dashboard."
elif [ $active_services -eq 1 ]; then
    echo "📍 Single Service Mode (Current)"
    echo "   - Push to main → Deploys to production"
    echo "   - Simple but no staging environment"
    echo ""
    echo "   To continue with this setup:"
    echo "   1. Just use 'git push origin main' to deploy"
    echo "   2. Check status with './scripts/check-deployment.sh production'"
else
    echo "📍 Staging + Production Mode (Recommended)"
    echo "   - Push to main → Auto-deploys to staging"
    echo "   - Manual promote → Production"
    echo ""
    echo "   To use this setup:"
    echo "   1. Deploy to staging: './scripts/deploy-staging.sh'"
    echo "   2. Test at: https://ultrai-staging-api.onrender.com"
    echo "   3. Deploy to prod: './scripts/deploy-production.sh'"
fi

echo ""
echo "🚀 Quick Start Commands:"
echo "   ./scripts/check-deployment.sh staging     # Check staging"
echo "   ./scripts/check-deployment.sh production  # Check production"
echo "   ./scripts/deploy-staging.sh              # Deploy to staging"
echo "   ./scripts/deploy-production.sh           # Deploy to production"
echo ""
echo "📚 Next Steps:"
echo "1. Go to https://dashboard.render.com"
echo "2. Check each service's 'Settings' → 'Build & Deploy'"
echo "3. Verify which branch each service watches"
echo "4. Update DEPLOYMENT_STRATEGY.md with your choice"