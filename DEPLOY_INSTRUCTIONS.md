# Render Deployment Instructions

## Quick Deploy (5 minutes)

1. **Delete your current Render service** (to avoid caching issues)

2. **Create new service** from GitHub repo

3. **Choose "Python" runtime** (NOT Docker)

4. **Use these settings:**

   - Build Command: `pip install -r requirements-render.txt`
   - Start Command: `gunicorn backend.app:app`

5. **Add these environment variables:**

   ```
   PYTHON_VERSION=3.11.0
   GUNICORN_WORKERS=1
   GUNICORN_BIND=0.0.0.0:$PORT
   GUNICORN_TIMEOUT=120
   GUNICORN_WORKER_CLASS=uvicorn.workers.UvicornWorker
   WEB_CONCURRENCY=1
   USE_MOCK_REDIS=true
   PYTHONPATH=/opt/render/project/src

   # Your API Keys (add these from your .env.production file):
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_API_KEY=your_google_key_here
   JWT_SECRET=your_jwt_secret_here
   USE_MOCK=false
   ENVIRONMENT=production
   ```

## What This Solves:

1. **No Docker caching** - Uses Python runtime directly
2. **Single worker** - Explicitly set via env vars
3. **Correct port** - Uses Render's $PORT variable
4. **Minimal dependencies** - Only what's needed
5. **Works on free tier** - Under 512MB RAM usage

## Alternative: Use render-prod.yaml

If you have Render CLI:

```bash
render config apply render-prod.yaml
```

But you'll need to add the API keys manually in the yaml file.

## Troubleshooting:

- If imports fail, the app will fall back to `app_minimal.py`
- Check logs in Render dashboard
- Health check endpoint: `/api/health`
