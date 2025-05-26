# Render Dashboard Configuration Check

## Current Issue

Render is using `backend.app:app` and `requirements-render.txt` instead of our minimal configuration in render.yaml.

## Steps to Fix

### 1. Access Your Service Settings

1. Login to Render dashboard
2. Navigate to your `ultra-backend` service
3. Click the "Settings" tab

### 2. Update Build & Deploy Settings

In the "Build & Deploy" section, update:

**Build Command**:

- Current (likely): `pip install -r requirements-render.txt`
- Change to: `pip install -r requirements-ultra-minimal.txt`

**Start Command**:

- Current (likely): `gunicorn backend.app:app` or similar
- Change to: `gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_health_only:app`

**Note**: Don't use `python -m gunicorn` - just use `gunicorn` directly as it's installed in the environment

### 3. Check Environment Variables

In the "Environment" section:

- Ensure `PORT` is set to `10000` (or whatever you prefer)
- Check if there are any variables forcing specific app modules

### 4. Save and Deploy

- Click "Save Changes" for each modification
- This will automatically trigger a new deployment
- Monitor the deployment logs to verify correct configuration is used

## Important Notes

1. **Dashboard Overrides render.yaml**: Manual dashboard settings take precedence over render.yaml until the next Blueprint sync

2. **To Use render.yaml Instead**:

   - Go to Blueprints section
   - Find your Blueprint
   - Click "Sync" to apply render.yaml settings
   - This will override dashboard settings

3. **For Testing**: It's often easier to use dashboard settings for quick tests, then update render.yaml once working

## Expected Outcome

After these changes, deployment should:

- Install only `fastapi`, `uvicorn`, and `gunicorn`
- Run `app_health_only.py` instead of `backend.app`
- Successfully serve health endpoints at `/` and `/health`
