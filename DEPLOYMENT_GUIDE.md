# 🚀 UltraAI Deployment Guide (Simplified)

Last Updated: 2025-05-27

## ✅ Current Deployment Strategy

### Production Deployment (Render)

1. **Make changes** to code
2. **Commit** your changes
3. **Push to GitHub**: `git push origin main`
4. **Automatic deployment** via Render

That's it! No scripts needed.

## 📁 Key Files

### Entry Points

- **app_production.py** - Production entry point (imports from backend.app)
- **backend/app.py** - Main application with all routes including orchestrator

### Important Routes

- **backend/routes/orchestrator_routes.py** - Sophisticated 4-stage Feather orchestration
- All routes are automatically included via backend/app.py

## 🎯 Simplified Architecture

```
app_production.py
    └── imports from → backend/app.py
                           ├── includes all routes
                           ├── orchestrator routes ✓
                           ├── auth routes ✓
                           ├── document routes ✓
                           └── all other routes ✓
```

## ⚡ Local Development

For local testing:

```bash
# From project root
python -m uvicorn backend.app:app --reload --port 8000
```

Or use one of the remaining utility scripts in `/scripts/`

## 🗂️ Archived Files

All potentially conflicting scripts and configs have been moved to `/ARCHIVE/` including:

- Old start scripts (start-\*.sh)
- Old deploy scripts (deploy-\*.sh)
- Docker configurations
- Alternative app files

See `/ARCHIVE/ARCHIVE_MANIFEST_20250527.md` for details.

## 🔍 Troubleshooting

1. **Deployment not updating?**

   - Check Render dashboard for build logs
   - Ensure you pushed to the correct branch

2. **Routes not found?**

   - Verify app_production.py exists in root
   - Check that it imports from backend.app

3. **Local testing issues?**
   - Use the uvicorn command above
   - Don't use archived scripts

## 🎉 Benefits

- **Simple**: One clear path to deployment
- **Clean**: No conflicting scripts
- **Reliable**: Same code runs locally and in production
- **Sophisticated**: All patent-protected features included automatically

## 🩺 Health & Monitoring Endpoints

- **Health Check:** `GET /health` — Returns system health status (JSON: status, uptime, services, etc.)
- **Prometheus Metrics:** `GET /api/metrics` — Returns Prometheus metrics for monitoring (for Prometheus/Grafana or external monitoring tools)

## 📈 Monitoring & Alerting Setup

- Monitor `/health` for uptime and status (`status` should be `healthy` or `degraded`).
- Monitor `/api/metrics` for Prometheus scraping.
- Set up alerts for:
  - HTTP 5xx errors or endpoint downtime
  - Health status not `healthy`
  - High error rates or latency in metrics
- Review logs in Render dashboard or your logging solution.
- Rotate secrets and review environment variables regularly.

## 🛠️ Environment Variables

See `.env.example` for all required and optional environment variables for local and production deployment.
