# Fix Phase 2 Deployment - Wrong App Running

## Issue
The deployment succeeded but it's running the wrong app:
- Running: `app_health_only:app` (Phase 1)
- Should be: `app_with_database:app` (Phase 2)

## Solution

1. **Login to Render Dashboard**
   - Navigate to ultra-backend service
   - Go to Settings tab

2. **Update Start Command**
   
   Change from:
   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_health_only:app
   ```
   
   To:
   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app
   ```

3. **Save Changes**
   - This will trigger a new deployment
   - Monitor logs to ensure it starts correctly

## Expected Results
After deployment:
- `/` should return `{"status":"alive","phase":2}`
- `/health` should return `{"status":"ok","services":["api"]}`
- `/health/database` should return database status

## Verification
Once deployed, run:
```bash
./scripts/verify-phase2-deployment.sh https://ultra-backend.onrender.com
```