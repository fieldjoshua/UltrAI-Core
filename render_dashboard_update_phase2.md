# Update Render Dashboard for Phase 2 Deployment

## Issue
Render is using incorrect build command - it's treating the requirements file as a command.

## Solution

1. **Login to Render Dashboard**
   - Go to https://dashboard.render.com/
   - Navigate to your `ultra-backend` service

2. **Update Build & Deploy Settings**
   
   In the Settings tab → Build & Deploy section:
   
   **Build Command**:
   ```
   pip install -r requirements-phase2.txt
   ```
   
   **Start Command**:
   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app
   ```

3. **Check Environment Variables**
   - Ensure `PORT` is set to `10000`
   - Add `DATABASE_URL` if you want database support

4. **Save and Deploy**
   - Click "Save Changes"
   - This will trigger a new deployment

## Expected Results
- Build should complete successfully
- App should start with database health check endpoint
- All three endpoints should be accessible:
  - `/` - Returns `{"status":"alive","phase":2}`
  - `/health` - Returns `{"status":"ok","services":["api"]}`
  - `/health/database` - Returns database status

## Verification
Once deployed, run:
```bash
./scripts/verify-phase2-deployment.sh https://ultra-backend.onrender.com
```