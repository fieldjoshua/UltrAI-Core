# Working Minimal Deployment Configuration

## Phase 1 Success - Ultra Minimal App

Successfully deployed a minimal FastAPI app to Render with health check endpoints.

### Working Configuration

#### Files Created

1. **app_health_only.py**

   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   def root():
       return {"status": "alive"}

   @app.get("/health")
   def health():
       return {"status": "ok"}
   ```

2. **requirements-ultra-minimal.txt**
   ```
   fastapi==0.109.0
   uvicorn[standard]==0.27.0
   gunicorn==23.0.0
   ```

#### Render Dashboard Settings

- **Build Command**: `pip install -r requirements-ultra-minimal.txt`
- **Start Command**: `gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_health_only:app`
- **Runtime**: Python 3.11.0
- **Health Check Path**: /health

### Deployment Results

- URL: https://ultra-backend.onrender.com/
- Root endpoint (`/`): Returns `{"status":"alive"}`
- Health endpoint (`/health`): Returns `{"status":"ok"}`
- Status: ✅ Deployed and running

### Key Learnings

1. Render dashboard settings override render.yaml
2. Use `gunicorn module:app` format, not just module name
3. Dashboard configuration is fastest for testing
4. Start with absolute minimum and build up

### Next Steps

Proceed to Phase 2: Add Core Dependencies (database, Redis)
