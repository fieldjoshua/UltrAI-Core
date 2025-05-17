# Render Deployment - Phase 2

## Add Database Support

### Steps to Deploy

1. **Login to Render Dashboard**

   - Navigate to ultra-backend service
   - Go to Settings tab

2. **Update Build & Deploy Settings**

   **Build Command**:

   ```
   pip install -r requirements-phase2.txt
   ```

   **Start Command**:

   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app
   ```

3. **Add Database**

   - If no PostgreSQL database exists:
     - Go to Dashboard → New → PostgreSQL
     - Create database with appropriate plan
   - Copy the Internal Database URL

4. **Set Environment Variables**

   - Go to Environment section
   - Add: `DATABASE_URL` = [Internal Database URL]
   - Save changes

5. **Deploy and Verify**
   - Deployment will start automatically
   - Check deployment logs
   - Test endpoints:
     - `/` - Should return `{"status":"alive","phase":2}`
     - `/health` - Should return `{"status":"ok","services":["api"]}`
     - `/health/database` - Should return `{"status":"ok","database":"connected"}`

### Expected Results

Without database URL:

- `/health/database` returns `{"status":"warning","message":"No database URL configured","database":"not_configured"}`

With database URL:

- `/health/database` returns `{"status":"ok","database":"connected"}`

### Troubleshooting

If database connection fails:

1. Check DATABASE_URL is set correctly
2. Ensure it uses internal database URL (starts with `postgres://`)
3. Check deployment logs for specific errors
4. Verify database is running in Render dashboard
