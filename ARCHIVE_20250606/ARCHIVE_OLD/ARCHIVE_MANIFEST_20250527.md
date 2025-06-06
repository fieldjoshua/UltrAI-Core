# Archive Manifest - 2025-05-27

## Purpose
Archived potentially conflicting deployment files to simplify deployment strategy and prevent confusion.

## Archived Files

### Deployment Configs
- Procfile - Old Heroku/deployment configuration
- Dockerfile - Docker configuration (may conflict with Render)

### Backend Variants
- app_minimal.py - Minimal app version

### Start Scripts (14 files)
All start-*.sh scripts moved to prevent confusion about which to use

### Deploy Scripts (4 files)
All deploy scripts archived as deployment is now via git push to Render

### Run Scripts (3 files)
Various run scripts that could cause confusion

### Docker Compose Files (4 files)
Docker compose configurations that may conflict with Render deployment

## Current Strategy
- Use app_production.py as entry point
- It imports from backend.app which has all orchestrator routes
- Deploy via git push to Render
- No complex scripts needed!
