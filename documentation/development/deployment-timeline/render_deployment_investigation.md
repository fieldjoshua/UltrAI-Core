# Render Deployment Investigation

## Current Issue

Render continues to use the wrong configuration despite multiple attempts to fix it.

## What's Happening

1. Render is installing from requirements-render.txt (full dependencies)
2. Render is running `gunicorn backend.app:app` instead of `app_health_only:app`
3. Our render.yaml changes don't seem to be taking effect

## Configurations Checked

- `/render.yaml` - Updated to use minimal config
- `/render-prod.yaml` - Also updated
- `/scripts/start-render.sh` - Hardcoded to run backend.app
- `/scripts/start-render-minimal.sh` - Created for minimal app

## Possible Causes

1. Render might be caching the build configuration
2. There might be another configuration file Render is using
3. Environment variables might be overriding our settings
4. Render dashboard settings might override file configs

## Next Steps

1. Check Render dashboard for manual configuration
2. Try forcing a fresh deployment
3. Consider deleting and recreating the service
4. Check for environment variable overrides
