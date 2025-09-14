#!/bin/bash

# Verify Render setup is configured correctly

echo "🔍 Verifying Render Setup"
echo "========================"
echo ""

# Check if services are responding
echo "📡 Checking service health..."
echo ""

echo "1. Production (ultrai-prod-api):"
prod_status=$(curl -s -o /dev/null -w "%{http_code}" https://ultrai-prod-api.onrender.com/api/health)
if [ "$prod_status" = "200" ]; then
    echo "   ✅ Healthy"
    prod_env=$(curl -s https://ultrai-prod-api.onrender.com/api/health | jq -r '.environment')
    echo "   Environment: $prod_env"
else
    echo "   ❌ Not healthy (HTTP $prod_status)"
fi
echo ""

echo "2. Staging (ultrai-staging-api):"
staging_status=$(curl -s -o /dev/null -w "%{http_code}" https://ultrai-staging-api.onrender.com/api/health)
if [ "$staging_status" = "200" ]; then
    echo "   ✅ Healthy"
    staging_env=$(curl -s https://ultrai-staging-api.onrender.com/api/health | jq -r '.environment')
    echo "   Environment: $staging_env"
else
    echo "   ❌ Not healthy (HTTP $staging_status)"
    echo "   This needs to be fixed in Render dashboard"
fi
echo ""

# Check git status
echo "📊 Git Status:"
echo "   Current branch: $(git branch --show-current)"
echo "   Last commit: $(git log -1 --oneline)"
echo ""

# Configuration checklist
echo "📋 Configuration Checklist:"
echo ""
echo "In Render Dashboard (https://dashboard.render.com):"
echo ""
echo "For STAGING (ultrai-staging-api):"
if [ "$staging_status" != "200" ]; then
    echo "  ❌ Service is down - needs configuration"
    echo "     [ ] Add environment variables"
    echo "     [ ] Set branch to 'main'"
    echo "     [ ] Enable auto-deploy"
    echo "     [ ] Click 'Manual Deploy' to start"
else
    echo "  ✅ Service is running"
    echo "     [ ] Verify auto-deploy is ON"
fi
echo ""

echo "For PRODUCTION (ultrai-prod-api):"
if [ "$prod_status" = "200" ]; then
    echo "  ✅ Service is running"
    echo "     [ ] Verify auto-deploy is OFF (manual only)"
else
    echo "  ❌ Service needs attention"
fi
echo ""

# Test workflow
echo "💡 To test the workflow:"
echo "1. Make a change and push to main"
echo "2. Wait for staging to auto-deploy (5-10 min)"
echo "3. Check staging: https://ultrai-staging-api.onrender.com"
echo "4. If good, manually deploy to production in Render dashboard"
echo ""

# Show helpful commands
echo "🛠️  Useful Commands:"
echo "   ./scripts/check-deployment.sh staging    # Check staging"
echo "   ./scripts/check-deployment.sh production # Check production"
echo "   ./scripts/deploy-production.sh          # Deploy to production"