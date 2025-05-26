# Phase 3 Deployment - Cache Refresh Fix

## Issue
You're getting HTML 404 errors ("Cannot GET/POST") for all endpoints, which often indicates a caching or routing issue on Render.

## Solution: Clear Cache & Restart

### Method 1: Clear Build Cache & Redeploy

1. **Login to Render Dashboard**
   - Go to https://dashboard.render.com/
   - Navigate to your `ultra-backend` service

2. **Clear Build Cache**
   - Go to Settings tab
   - Scroll down to "Build & Deploy" section
   - Click on "Clear build cache & deploy"
   - This forces a complete rebuild without cached layers

### Method 2: Manual Deploy with Cache Clearing

1. **In the Render Dashboard**:
   - Go to your service
   - Click on "Manual Deploy" dropdown
   - Select "Clear build cache & deploy"

### Method 3: Update Configuration & Deploy

1. **Verify Build & Deploy Settings**:
   
   **Build Command**:
   ```
   pip install -r requirements-phase3.txt
   ```
   
   **Start Command**:
   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_auth:app
   ```

2. **Make a Small Change**:
   - Add a space at the end of the start command
   - Save changes
   - Remove the space
   - Save again
   - This forces a fresh deployment

### Method 4: Environment Variable Toggle

1. **Add a dummy environment variable**:
   - Name: `DEPLOY_VERSION`
   - Value: `phase3_v1`

2. **Save and deploy**

3. **After deployment, update the value**:
   - Change to: `phase3_v2`
   - This forces another deployment with fresh routing

## After Cache Clear

Once the cache is cleared and service redeployed:

1. Wait for deployment to complete (check logs)
2. Test the endpoints again:
   ```bash
   curl https://ultra-backend.onrender.com/
   curl https://ultra-backend.onrender.com/health
   ```

3. If still getting 404s, check deployment logs for:
   - Correct start command being used
   - FastAPI application starting successfully
   - Port binding messages

## Expected Results

After cache refresh, you should see:
- `/` returns `{"status":"alive","phase":3}`
- `/health` returns `{"status":"ok","services":["api","auth"]}`
- `/auth/register`, `/auth/login` endpoints work
- No more HTML 404 errors

## Still Having Issues?

If cache clearing doesn't resolve it:
1. Check deployment logs for startup errors
2. Verify the correct app file is being used
3. Ensure all dependencies are installed
4. Check for any import errors in app_with_auth.py