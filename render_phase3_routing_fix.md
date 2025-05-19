# Phase 3 Deployment - Routing Fix

## Issue
The FastAPI app is running correctly (confirmed locally), but Render is returning HTML 404 errors for all endpoints. This indicates a routing/proxy issue.

## Diagnosis
1. App starts successfully on port 10000
2. Gunicorn is running with correct configuration
3. Local testing shows all endpoints work
4. Render returns HTML 404s (not FastAPI JSON 404s)

## Solution

### Option 1: Check Render's Port Configuration

1. **Go to Render Dashboard**
   - Navigate to your service
   - Check Environment Variables

2. **Ensure PORT is set correctly**:
   - Add/Update: `PORT=10000`
   - Render might be expecting a different port

### Option 2: Update Start Command to Use Render's PORT

Change the start command to explicitly use Render's PORT variable:

```bash
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT app_with_auth:app
```

(Remove the default port fallback)

### Option 3: Add Host Header Support

Create a new file `app_with_auth_render.py`:

```python
from app_with_auth import app

# Add middleware to handle Render's reverse proxy
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["ultra-backend.onrender.com", "localhost", "127.0.0.1"]
)
```

Then update start command to use this wrapper.

### Option 4: Check Render Service Type

1. Ensure your service is configured as "Web Service" not "Private Service"
2. Check that "Auto-Deploy" is enabled
3. Verify no custom domains are misconfigured

### Option 5: Force ASGI Application Detection

Try this start command:
```bash
uvicorn app_with_auth:app --host 0.0.0.0 --port $PORT
```

Or with gunicorn:
```bash
gunicorn app_with_auth:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## Debugging Steps

1. Check Render logs for any proxy/routing errors
2. Try accessing with different paths:
   - `https://ultra-backend.onrender.com/docs` (FastAPI's built-in docs)
   - `https://ultra-backend.onrender.com/openapi.json`
3. Add logging to app startup to confirm it's receiving requests

## Quick Fix to Try

In Render Dashboard:
1. Clear build cache
2. Update start command to:
   ```
   uvicorn app_with_auth:app --host 0.0.0.0 --port $PORT --forwarded-allow-ips='*'
   ```
3. Save and redeploy

This handles reverse proxy headers that Render might be using.