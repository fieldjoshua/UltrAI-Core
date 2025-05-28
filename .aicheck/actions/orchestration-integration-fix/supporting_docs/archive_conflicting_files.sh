#!/bin/bash

# Archive Conflicting Files Script
# Purpose: Move potentially conflicting deployment files to ARCHIVE
# Date: 2025-05-27

echo "🗂️  Archiving Conflicting Deployment Files"
echo "========================================="

# Create archive subdirectories if they don't exist
mkdir -p ARCHIVE/deployment_configs_20250527
mkdir -p ARCHIVE/scripts_20250527/start_scripts
mkdir -p ARCHIVE/scripts_20250527/deploy_scripts
mkdir -p ARCHIVE/scripts_20250527/run_scripts
mkdir -p ARCHIVE/docker_configs_20250527
mkdir -p ARCHIVE/backend_20250527

# Function to safely move files
move_if_exists() {
    if [ -f "$1" ]; then
        echo "Moving: $1 → $2"
        mv "$1" "$2"
    else
        echo "Skip: $1 (not found)"
    fi
}

echo -e "\n📁 Archiving Root Deployment Configs..."
move_if_exists "Procfile" "ARCHIVE/deployment_configs_20250527/"
move_if_exists "Dockerfile" "ARCHIVE/deployment_configs_20250527/"

echo -e "\n📁 Archiving Backend App Variants..."
move_if_exists "backend/app_minimal.py" "ARCHIVE/backend_20250527/"

echo -e "\n📁 Archiving Start Scripts..."
for script in start-backend-fixed.sh start-backend.sh start-dev.sh start-docker.sh \
              start-frontend.sh start-migrate.sh start-mvp-docker.sh start-production.sh \
              start-render-minimal.sh start-render.sh start-ultra-with-modelrunner.sh \
              start-ultra.sh start-with-all-llms.sh start.sh; do
    move_if_exists "scripts/$script" "ARCHIVE/scripts_20250527/start_scripts/"
done

echo -e "\n📁 Archiving Deploy Scripts..."
for script in deploy-mvp.sh deploy-to-cloud.sh deploy.sh deploy-frontend.sh; do
    move_if_exists "scripts/$script" "ARCHIVE/scripts_20250527/deploy_scripts/"
done

echo -e "\n📁 Archiving Run Scripts..."
for script in run.sh run-docker-orchestrator.sh run_app.sh; do
    move_if_exists "scripts/$script" "ARCHIVE/scripts_20250527/run_scripts/"
done

echo -e "\n📁 Archiving Docker Compose Files..."
for file in docker-compose.ci.yml docker-compose.override.yml \
            docker-compose.production.yml docker-compose.yml; do
    move_if_exists "$file" "ARCHIVE/docker_configs_20250527/"
done

echo -e "\n✅ Archiving Complete!"
echo -e "\n📋 Active Deployment Files:"
echo "  - app_production.py (imports from backend.app)"
echo "  - backend/app.py (main application with orchestrator routes)"
echo -e "\n🚀 Deployment is now simplified and conflict-free!"

# Create a manifest of what was archived
cat > ARCHIVE/ARCHIVE_MANIFEST_20250527.md << EOF
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
EOF

echo -e "\n📄 Archive manifest created: ARCHIVE/ARCHIVE_MANIFEST_20250527.md"