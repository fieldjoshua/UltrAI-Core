# Simple Deployment Guide

## Your Current Setup
- **Development**: Your laptop (localhost:8000)
- **Production**: ultrai-core.onrender.com
- **Staging**: ultrai-staging-api.onrender.com (needs fixing)

## Option 1: Keep It Simple (What You've Been Doing)
Just push to main and it deploys to production:

```bash
# Make your changes
git add .
git commit -m "your changes"
git push origin main

# Check if it worked
./scripts/check-deployment.sh production
```

**This is totally fine for a solo developer!**

## Option 2: Add a Safety Net (Staging)
Test changes on staging before they go to real users:

```bash
# Step 1: Push your changes (auto-deploys to staging)
git add .
git commit -m "your changes"
git push origin main

# Step 2: Check staging
./scripts/check-deployment.sh staging
# Visit: https://ultrai-staging-api.onrender.com

# Step 3: If it looks good, deploy to production
./scripts/deploy-production.sh
# Follow the manual steps it shows you
```

## Which Should You Choose?

### Stick with Option 1 if:
- You test thoroughly on localhost
- You're comfortable fixing issues quickly
- You want the simplest workflow

### Try Option 2 if:
- You want to test with real API keys/environment
- You're making big changes
- You want more confidence before users see changes

## Quick Setup

Run this to see what's currently working:
```bash
./scripts/setup-deployment.sh
```

## Common Commands

```bash
# Check what's deployed where
./scripts/check-deployment.sh production
./scripts/check-deployment.sh staging

# Deploy to staging (automatic with push to main)
./scripts/deploy-staging.sh

# Deploy to production (manual process)
./scripts/deploy-production.sh
```

## What Happens When You Push Code?

### Current Reality:
- Push to `main` → One of your Render services deploys (check dashboard to see which)

### What We Can Set Up:
- Push to `main` → Staging deploys automatically
- Run deploy script → Production deploys when you're ready

## Next Step

Tell me:
1. Do you want to keep it simple (Option 1)?
2. Or add staging for safety (Option 2)?

I'll configure everything to match your choice!