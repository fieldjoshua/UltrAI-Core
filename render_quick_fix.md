# Quick Fix for Render Phase 3 Deployment

## The Issue
- App works locally
- Render returns HTML 404s (not FastAPI JSON responses)
- This means Render's proxy isn't connecting to your app

## Most Likely Cause: Port Mismatch

## Immediate Fix

1. **Login to Render Dashboard**
2. **Go to your `ultra-backend` service**
3. **Update the Start Command to**:
   ```
   uvicorn app_with_auth:app --host 0.0.0.0 --port $PORT
   ```
   
   Note: Use `$PORT` not `${PORT:-10000}` - Render sets this automatically

4. **Save Changes and Deploy**

## Alternative Commands to Try

If the above doesn't work, try these in order:

1. **Basic Uvicorn**:
   ```
   uvicorn app_with_auth:app --host 0.0.0.0 --port $PORT
   ```

2. **With Proxy Headers**:
   ```
   uvicorn app_with_auth:app --host 0.0.0.0 --port $PORT --forwarded-allow-ips='*'
   ```

3. **With Gunicorn** (if uvicorn fails):
   ```
   gunicorn app_with_auth:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

## After Deployment

Test with:
```bash
curl https://ultra-backend.onrender.com/
```

You should see:
```json
{"status":"alive","phase":3}
```

## Still Not Working?

Check these in Render Dashboard:
1. Service type is "Web Service" (not Private)
2. No custom domain issues
3. Look at deployment logs for actual port binding
4. Try accessing `/docs` endpoint for FastAPI documentation

The key insight: Render automatically assigns a PORT, and your app must listen on exactly that port.