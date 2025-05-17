# Fix for "app_health_only: command not found" Error

## Issue

Render is trying to run `app_health_only` as a command instead of loading it as a Python module.

## Solution

Update the Start Command in Render dashboard:

1. Go to Render dashboard → ultra-backend service → Settings
2. In Build & Deploy section, update Start Command to:
   ```
   gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_health_only:app
   ```

## Important Notes

1. **Don't use `python -m`**: Just use `gunicorn` directly
2. **Module format**: Use `app_health_only:app` (module:object)
3. **Port binding**: Use `${PORT:-10000}` for Render's dynamic port

## Alternative Commands to Try

If the above doesn't work, try these variations:

1. Simple gunicorn:

   ```
   gunicorn app_health_only:app --bind 0.0.0.0:${PORT:-10000}
   ```

2. With explicit Python:

   ```
   python -m gunicorn app_health_only:app --bind 0.0.0.0:${PORT:-10000}
   ```

3. Using uvicorn directly:
   ```
   uvicorn app_health_only:app --host 0.0.0.0 --port ${PORT:-10000}
   ```

## Verification

After updating and deploying, check:

- Deployment logs for successful startup
- Visit https://ultra-backend.onrender.com/health
- Should return `{"status": "ok"}`
