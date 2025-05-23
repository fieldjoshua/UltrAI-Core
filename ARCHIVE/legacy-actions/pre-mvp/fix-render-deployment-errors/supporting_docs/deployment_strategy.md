# Deployment Strategy

## Phase 1: Ultra-Minimal (Health Check Only)

### Working Configuration

- **App**: `app_health_only.py`
- **Requirements**: `requirements-ultra-minimal.txt`
- **Config**: `render-minimal.yaml`
- **Endpoints**: `/` and `/health`

### Files Created

1. **app_health_only.py**

   - FastAPI app with only health endpoints
   - No database, no auth, no LLM integration
   - Successfully tested locally on port 8001

2. **requirements-ultra-minimal.txt**

   - fastapi==0.109.0
   - uvicorn[standard]==0.27.0
   - gunicorn==23.0.0

3. **render-minimal.yaml**
   - Uses Python runtime
   - Minimal environment variables
   - Uses gunicorn with uvicorn worker

### Local Test Results

- App runs successfully
- Health check responds with `{"status":"ok"}`
- Root endpoint responds with `{"status":"alive"}`

### Next Steps

- Deploy to Render using render-minimal.yaml
- Verify health check works in production
- Document any deployment issues

### Deployment Issues Found

1. **Multiple render config files exist**:

   - `render.yaml` (might be the default)
   - `render-prod.yaml` (updated but still loading wrong requirements)
   - `render-minimal.yaml` (our intended minimal config)

2. **Deploy still uses full backend.app**:

   - Despite updating render-prod.yaml
   - Still installing all dependencies (sqlalchemy, redis, etc.)
   - Still running `gunicorn backend.app:app`

3. **Solution**: Need to ensure Render uses the correct config file
