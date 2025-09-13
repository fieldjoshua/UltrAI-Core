# Render Configuration for Staging + Production

## Current Status
- **ultrai-core.onrender.com** - ✅ Active (Use as PRODUCTION)
- **ultrai-staging-api.onrender.com** - ❌ Down (Need to fix for STAGING)
- **ultrai-prod-api.onrender.com** - ✅ Active (Consider removing - duplicate)

## Step-by-Step Configuration

### 1. Configure Staging Service (ultrai-staging-api)

Go to: https://dashboard.render.com

Find **ultrai-staging-api** service and check:

1. **Settings → Build & Deploy**:
   - Branch: `main` ✅
   - Auto-Deploy: `Yes` ✅
   - Build Command: `pip install -r requirements-production.txt`
   - Start Command: `python app_production.py`

2. **Environment Variables** - Add these:
   ```
   ENVIRONMENT=staging
   PORT=10000
   ENABLE_BILLING=false
   ENABLE_PRICING=false
   
   # Add your API keys:
   OPENAI_API_KEY=your-key
   ANTHROPIC_API_KEY=your-key
   GOOGLE_API_KEY=your-key
   HUGGINGFACE_API_KEY=your-key
   ```

3. **Restart the service** to apply changes

### 2. Configure Production Service (ultrai-core)

Find **ultrai-core** service and check:

1. **Settings → Build & Deploy**:
   - Branch: `main` 
   - Auto-Deploy: `No` ❌ (Turn this OFF for manual control)
   - Build Command: `pip install -r requirements-production.txt`
   - Start Command: `python app_production.py`

2. **Environment Variables** should already be set (since it's working)

3. **Save changes**

### 3. Clean Up (Optional)

If **ultrai-prod-api** is redundant:
1. Make sure it's not being used
2. Consider suspending or deleting it to avoid confusion

## How It Will Work After Configuration

1. **You push to main** → Staging auto-deploys
2. **Test on staging** → https://ultrai-staging-api.onrender.com
3. **When ready** → Go to ultrai-core and click "Manual Deploy"

## Quick Test

After configuring, test the flow:

```bash
# 1. Make a small change
echo "# Test deployment $(date)" >> README.md
git add README.md
git commit -m "Test staging deployment"
git push origin main

# 2. Wait 2-3 minutes, then check staging
./scripts/check-deployment.sh staging

# 3. If staging works, deploy to production
# Go to Render dashboard → ultrai-core → Manual Deploy
```

## Environment Variables Needed

### Both Staging and Production:
- `ENVIRONMENT` (staging or production)
- `PORT` (10000)
- LLM API keys (OPENAI_API_KEY, etc.)

### Production Only:
- `DATABASE_URL` (if using database)
- `REDIS_URL` (if using Redis)
- `JWT_SECRET` (for authentication)

### Staging Can Use:
- Simplified/test versions of the above
- `ENABLE_BILLING=false`
- `ENABLE_PRICING=false`

## Troubleshooting

If staging doesn't start:
1. Check the build logs in Render dashboard
2. Make sure all required environment variables are set
3. Verify the branch setting is `main`
4. Check that auto-deploy is enabled

If production doesn't update:
1. Make sure auto-deploy is DISABLED
2. Use Manual Deploy button in Render dashboard
3. Select the correct commit from main branch