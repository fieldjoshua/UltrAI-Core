# Render Setup Instructions - Step by Step

## Current Situation
- **ultrai-prod-api.onrender.com** - Your ACTIVE production (working)
- **ultrai-staging-api.onrender.com** - Staging (needs to be fixed)
- **ultrai-core.onrender.com** - Old service (keep suspended)

## Step 1: Fix Staging Service

Go to: https://dashboard.render.com

### A. Find and click on "ultrai-staging-api" service

### B. Go to "Environment" tab and add these variables:
```
ENVIRONMENT=staging
PORT=10000
ENABLE_BILLING=false
ENABLE_PRICING=false
ENABLE_AUTH=false
ENABLE_RATE_LIMIT=false

# Add your API keys (same ones from production):
OPENAI_API_KEY=<copy from ultrai-prod-api>
ANTHROPIC_API_KEY=<copy from ultrai-prod-api>
GOOGLE_API_KEY=<copy from ultrai-prod-api>
HUGGINGFACE_API_KEY=<copy from ultrai-prod-api>
```

### C. Go to "Settings" tab:
1. Scroll to "Build & Deploy" section
2. Check these settings:
   - **Branch**: main
   - **Auto-Deploy**: Yes ✓
   - **Build Command**: `pip install -r requirements-production.txt`
   - **Start Command**: `python app_production.py`

### D. Click "Manual Deploy" to start it now
- This will build and deploy with the new settings

## Step 2: Configure Production Service

### A. Find and click on "ultrai-prod-api" service

### B. Go to "Settings" tab:
1. Scroll to "Build & Deploy" section
2. Change these settings:
   - **Branch**: main
   - **Auto-Deploy**: No ✗ (TURN THIS OFF)
   - Keep other settings the same

### C. Click "Save Changes"

## Step 3: Test the Setup

After staging finishes deploying (5-10 minutes):

```bash
# Check if staging is working
./scripts/check-deployment.sh staging

# Check production is still working
./scripts/check-deployment.sh production
```

## Step 4: Test the Workflow

```bash
# Make a test change
echo "# Staging test $(date)" >> README.md
git add README.md
git commit -m "Test staging deployment"
git push

# Wait 5 minutes, then check staging
./scripts/check-deployment.sh staging

# If staging looks good, deploy to production manually:
# 1. Go to Render dashboard
# 2. Click on ultrai-prod-api
# 3. Click "Manual Deploy"
# 4. Select the latest commit from main
```

## Troubleshooting

### If staging doesn't start:
1. Check the Logs tab in Render
2. Common issues:
   - Missing environment variables
   - Wrong start command
   - Branch mismatch

### If production auto-deploys when you don't want it:
1. Make sure Auto-Deploy is set to "No"
2. Save the changes

## Your New Workflow

1. **Develop locally** → test on localhost:8000
2. **Push to main** → Automatically deploys to staging
3. **Test on staging** → https://ultrai-staging-api.onrender.com
4. **Deploy to production** → Manual deploy in Render dashboard

## Quick Reference

- **Staging**: https://ultrai-staging-api.onrender.com (auto-deploys from main)
- **Production**: https://ultrai-prod-api.onrender.com (manual deploy only)
- **Dashboard**: https://dashboard.render.com