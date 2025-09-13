#!/bin/bash

# Test the staging + production deployment flow
# Run this after configuring Render services

echo "🧪 Testing Deployment Flow"
echo "========================="
echo ""

# Step 1: Check current status
echo "📊 Step 1: Checking current service status..."
echo ""
echo "Production (ultrai-core):"
./scripts/check-deployment.sh production | grep -E "(✅|❌|http_code)"
echo ""
echo "Staging (ultrai-staging-api):"
./scripts/check-deployment.sh staging | grep -E "(✅|❌|http_code)"
echo ""

# Step 2: Create a test change
echo "📝 Step 2: Creating test change..."
test_file="deployment-test-$(date +%s).txt"
echo "Test deployment at $(date)" > "$test_file"
git add "$test_file"
git commit -m "Test: Staging deployment $(date +%Y-%m-%d_%H:%M:%S)"
echo "✅ Created test commit"
echo ""

# Step 3: Push to trigger staging
echo "🚀 Step 3: Pushing to main (should trigger staging)..."
git push origin main
echo "✅ Pushed to main"
echo ""

# Step 4: Wait and check staging
echo "⏳ Step 4: Waiting for staging deployment (3 minutes)..."
echo "   While waiting, check: https://dashboard.render.com"
echo "   Look for ultrai-staging-api build in progress"
echo ""

# Countdown
for i in {180..1}; do
    printf "\r   Time remaining: %d seconds " "$i"
    sleep 1
done
echo ""
echo ""

# Step 5: Verify staging deployed
echo "🔍 Step 5: Checking if staging deployed..."
./scripts/check-deployment.sh staging
echo ""

# Step 6: Instructions for production
echo "📋 Step 6: Production deployment instructions:"
echo ""
echo "If staging looks good, deploy to production:"
echo "1. Go to: https://dashboard.render.com"
echo "2. Click on 'ultrai-core' service"
echo "3. Go to 'Manual Deploy' (top right)"
echo "4. Deploy the latest commit from main"
echo ""
echo "Or run: ./scripts/deploy-production.sh"
echo ""

# Cleanup
echo "🧹 Cleaning up test file..."
rm -f "$test_file"
git rm "$test_file" 2>/dev/null
git commit -m "Cleanup: Remove test file" 2>/dev/null

echo "✅ Test complete!"