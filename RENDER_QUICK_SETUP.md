# Render Quick Setup Guide

## ⚠️ SECURITY WARNING
The `.env.render-*` files contain your actual API keys. 
- NEVER commit these files to git
- Delete them after copying to Render
- They are already in .gitignore for safety

## Step 1: Fix Staging Service

1. Go to: https://dashboard.render.com
2. Click on **ultrai-staging-api**
3. Click on **Environment** tab
4. Click **Add Environment Variable** and add each line from `.env.render-staging`
   - Open the file: `.env.render-staging`
   - Copy each line (KEY=value format)
   - Add them one by one
5. Go to **Settings** tab
6. Under **Build & Deploy**:
   - Branch: `main`
   - Auto-Deploy: `Yes` ✓
7. Click **Manual Deploy** button (top right)
8. Select **Deploy latest commit**

## Step 2: Update Production Service

1. Still in Render Dashboard
2. Click on **ultrai-prod-api**
3. Go to **Settings** tab
4. Under **Build & Deploy**:
   - Auto-Deploy: `No` ✗ (TURN OFF)
5. Save changes

## Step 3: Verify Setup

Wait 5-10 minutes for staging to deploy, then run:

```bash
# Check both services
./scripts/verify-render-setup.sh

# If staging shows ✅ Healthy, test the workflow:
echo "Test $(date)" >> README.md
git add . && git commit -m "Test staging auto-deploy" && git push

# Wait 5 minutes, then check staging updated
./scripts/check-deployment.sh staging
```

## Step 4: Clean Up Sensitive Files

After copying to Render, delete the sensitive files:

```bash
rm -f .env.render-staging .env.render-production
```

## Your New Workflow

1. **Push to main** → Staging auto-deploys
2. **Test staging** → https://ultrai-staging-api.onrender.com
3. **Deploy to prod** → Go to Render, click ultrai-prod-api, Manual Deploy

## Troubleshooting

If staging still shows 502:
- Check Logs tab in Render for errors
- Verify all API keys were added
- Make sure PORT=10000 is set
- Check build/start commands match production