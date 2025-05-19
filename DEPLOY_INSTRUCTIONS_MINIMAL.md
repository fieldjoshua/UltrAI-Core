# Minimal Deployment Instructions

## Quick Start

This deployment uses a minimal configuration optimized for Render's infrastructure.

### 1. Files Required
- `app_with_database.py` - Minimal FastAPI app
- `requirements-phase2.txt` - 27 essential dependencies
- `render.yaml` - Deployment configuration

### 2. Deploy to Render

#### Option A: Auto-deploy from GitHub
1. Push to main branch
2. Render auto-deploys

#### Option B: Manual Deploy
1. Login to Render dashboard
2. Go to your service
3. Click "Manual Deploy"

### 3. Configuration

In Render Dashboard → Settings:

**Build Command**:
```
pip install -r requirements-phase2.txt
```

**Start Command**:
```
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app
```

### 4. Environment Variables

Add in dashboard:
- `DATABASE_URL` - PostgreSQL connection (optional)
- `PORT` - Usually auto-set by Render

### 5. Verify Deployment

```bash
# Check status
curl https://your-app.onrender.com/

# Expected response
{"status":"alive","phase":2}
```

## Performance

- **Build time**: ~2 minutes
- **Response time**: ~350ms average
- **Memory usage**: < 512MB
- **Dependencies**: 27 (vs 71 original)

## Troubleshooting

1. **Endpoints return HTML errors**
   - Clear Render cache
   - Check dashboard commands

2. **Build fails**
   - Verify requirements file name
   - Check Python version (3.11.0)

3. **App doesn't start**
   - Verify full gunicorn command
   - Check deployment logs

## Next Steps

1. Add `DATABASE_URL` for database support
2. Configure custom domain
3. Set up monitoring
4. Add authentication layer

---

For detailed documentation, see `/documentation/deployment/render_minimal_deployment_guide.md`