# Pre-Archive Audit Report

Date: 2025-05-27
Purpose: Document files to be archived to prevent deployment conflicts

## 🎯 Objective

Clean up the project structure by archiving scripts and configurations that could cause confusion or conflicts with our simplified deployment strategy.

## 📋 Files to Archive

### 1. Root Directory (2 files)
- **Procfile**: Old Heroku-style deployment config
- **Dockerfile**: Docker config that might conflict with Render

### 2. Backend Directory (1 file)
- **backend/app_minimal.py**: Minimal version that could be confused with main app

### 3. Scripts Directory (21 files)

#### Start Scripts (14)
- start-backend-fixed.sh
- start-backend.sh
- start-dev.sh
- start-docker.sh
- start-frontend.sh
- start-migrate.sh
- start-mvp-docker.sh
- start-production.sh
- start-render-minimal.sh
- start-render.sh
- start-ultra-with-modelrunner.sh
- start-ultra.sh
- start-with-all-llms.sh
- start.sh

#### Deploy Scripts (4)
- deploy-mvp.sh
- deploy-to-cloud.sh
- deploy.sh
- deploy-frontend.sh

#### Run Scripts (3)
- run.sh
- run-docker-orchestrator.sh
- run_app.sh

### 4. Docker Compose Files (4)
- docker-compose.ci.yml
- docker-compose.override.yml
- docker-compose.production.yml
- docker-compose.yml

## ✅ Files to Keep

### Active Deployment Files
1. **app_production.py** - Simple bridge to backend.app
2. **backend/app.py** - Main application with all routes
3. **backend/routes/orchestrator_routes.py** - Sophisticated orchestration

### Useful Scripts (Keep)
- Scripts for testing, checking, utilities
- Non-deployment scripts that don't cause confusion

## 🚀 Benefits

1. **Clarity**: One clear deployment path
2. **Simplicity**: No confusion about which script to use
3. **Maintenance**: Easier to understand deployment
4. **Safety**: Old configs won't accidentally be used

## 📝 Post-Archive Strategy

Deployment becomes simple:
1. Edit code
2. Commit and push to GitHub
3. Render automatically deploys
4. No scripts needed!

The sophisticated orchestration features are in the code, not in complex deployment scripts.