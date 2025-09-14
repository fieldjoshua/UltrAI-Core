# Fix Staging Deployment

## The Problem
Staging is failing because the frontend isn't being built. The error shows:
```
RuntimeError: Directory '/opt/render/project/src/frontend/dist/assets' does not exist
```

## The Fix

### Go to Render Dashboard: https://dashboard.render.com

1. Click on **ultrai-staging-api**

2. Go to **Settings** tab

3. Under **Build & Deploy**, update the **Build Command** to:
   ```bash
   pip install -r requirements-production.txt && cd frontend && npm install && npm run build && cd ..
   ```

4. Make sure **Start Command** is:
   ```bash
   python app_production.py
   ```

5. Click **Save Changes**

6. Click **Manual Deploy** to trigger a new build

## Alternative Quick Fix (if npm isn't available)

If the build still fails, we can disable frontend serving for staging:

1. Add this environment variable:
   ```
   SERVE_FRONTEND=false
   ```

2. This will make staging API-only (which is fine for testing the backend)

## What's Happening

- **Good**: Your API keys are working (OpenAI, Anthropic, Google all loaded)
- **OK**: Database and Redis aren't configured (using fallbacks)
- **Bad**: Frontend build is missing, causing startup to fail

## Next Steps

After updating the build command:
1. Wait 10-15 minutes for the build
2. Check logs for any npm errors
3. Run: `./scripts/check-deployment.sh staging`

The build command will:
1. Install Python dependencies
2. Install frontend dependencies
3. Build the frontend
4. Then start the server