# Fix Phase 2 Deployment - Start Command Issue

## Problem
Render is interpreting the start command incorrectly. It's treating `app_with_database:app` as a command instead of arguments to gunicorn.

## Solution

1. **Login to Render Dashboard**
   - Navigate to ultra-backend service
   - Go to Settings → Build & Deploy

2. **Update Start Command**
   
   The FULL command should be:
   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app
   ```
   
   Make sure the ENTIRE command is in the Start Command field, not just `app_with_database:app`

3. **Verify the command includes**:
   - `gunicorn` at the beginning
   - All the worker and bind parameters
   - `app_with_database:app` at the end

4. **Save Changes**
   - This will trigger another deployment

## Expected Logs
After deployment, you should see:
```
==> Running 'gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app'
```

NOT:
```
==> Running 'app_with_database:app'
```

## Verification
Once deployed correctly, the endpoints will work:
- `/` → `{"status":"alive","phase":2}`
- `/health` → `{"status":"ok","services":["api"]}`
- `/health/database` → Database status