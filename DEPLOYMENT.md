# Cross-Platform Deployment Checklist

This repository deploys to multiple platforms. Use this checklist for every PR affecting deployment.

## Required Checks (CI)
- Frontend build succeeds: `cd frontend && npm ci && npm run build`
- Render YAML (if present) validated (publish paths, health checks)
- Required env flags present for APIs:
  - `RAG_ENABLED=false`
  - `MINIMUM_MODELS_REQUIRED=3`
  - `ENABLE_SINGLE_MODEL_FALLBACK=false`
  - `ALLOW_PUBLIC_ORCHESTRATION=false` (prod)

## Platform Settings

### Render
- API services (web):
  - Build: `pip install -r requirements-production.txt`
  - Start: `uvicorn app_production:app --host 0.0.0.0 --port $PORT`
  - Health Check Path: `/health`
  - Env via Env Group; no secrets in service-level vars
- Static sites:
  - Publish: `frontend/dist`

### Netlify
- netlify.toml present with:
  - `[build] base = "frontend"`, `publish = "dist"`, `command = "npm ci && npm run build"`
  - `[[redirects]]` SPA rewrite to `/index.html`
- Deploy previews point to staging API via `[context.deploy-preview.environment] VITE_API_URL`

### Vercel
- Project root set to `frontend`
- Build command: `npm run build`
- Output directory: `dist`

### Docker (if used)
- Env flags wired the same as Render
- Health check endpoint `/health`

## Branching
- Staging: `main`
- Production: `production`
- Auto-merge enabled when CI is green and branch is up to date

## Review Notes
- Keep Netlify previews non-blocking; required checks: lint/tests, frontend build, Vercel, up-to-date branch
