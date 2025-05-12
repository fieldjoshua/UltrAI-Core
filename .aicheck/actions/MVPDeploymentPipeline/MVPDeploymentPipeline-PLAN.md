# MVPDeploymentPipeline Action Plan (10 of 16)

## Overview

**Status:** Planning  
**Created:** 2025-05-11  
**Last Updated:** 2025-05-11  
**Expected Completion:** 2025-05-28  

## Objective

Create a streamlined, reliable deployment pipeline for the Ultra MVP to enable consistent deployment to production and development environments with appropriate verification and rollback capabilities.

## Value to Program

This action directly addresses deployment requirements for the MVP by:

1. Establishing a standardized deployment process for consistency
2. Creating verification tests to ensure deployments work correctly
3. Setting up environment configuration management
4. Providing rollback capabilities for failed deployments
5. Documenting the release process for all team members

## Success Criteria

- [ ] Finalize Docker containerization for all components
- [ ] Create environment configuration management
- [ ] Implement deployment verification testing
- [ ] Establish rollback procedures for failed deployments
- [ ] Document release process for development and production
- [ ] Create deployment automation scripts
- [ ] Test full deployment process

## Implementation Plan

### Phase 1: Containerization Finalization (Days 1-3)

1. Audit and finalize Docker container configuration:
   - Review existing Dockerfiles for best practices
   - Optimize container size and startup time
   - Ensure proper caching and layer management

2. Create container versioning strategy:
   - Version tagging approach
   - Container registry management
   - Image promotion workflow

3. Implement container health checks:
   - Startup health verification
   - Runtime health monitoring
   - Graceful shutdown handling

### Phase 2: Environment Configuration (Days 4-6)

1. Create environment configuration system:
   - Development, staging, and production environments
   - Environment variable management
   - Configuration file templating

2. Implement secure secret management:
   - API key storage and rotation
   - Database credential management
   - Service account management

3. Develop environment provisioning scripts:
   - Resource allocation
   - Network and security setup
   - Database initialization

### Phase 3: Deployment Automation (Days 7-9)

1. Create deployment scripts:
   - Automated build process
   - Container deployment
   - Service startup orchestration

2. Implement verification tests:
   - Post-deployment smoke tests
   - Integration verification
   - Rollback triggers

3. Develop rollback procedures:
   - Version rollback implementation
   - Data consistency preservation
   - Rollback validation

### Phase 4: Documentation and Testing (Days 10-12)

1. Document deployment process:
   - Release checklist
   - Deployment guide
   - Troubleshooting procedures

2. Test deployment pipeline:
   - Full deployment test
   - Rollback test
   - Partial update test

3. Training and knowledge transfer:
   - Team training on deployment
   - Incident response procedures
   - Deployment schedule and planning

## Dependencies

- DockerComposeSetup (Completed)
- DockerizedOrchestrator (Completed)
- MVPTestCoverage (In Progress)
- MonitoringAndLogging (To Be Created)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Environment-specific issues | High | Medium | Environment parity, comprehensive testing in all environments |
| Configuration errors | High | Medium | Configuration validation, automatic verification |
| Deployment failures | High | Medium | Automated rollback, canary deployments |
| Performance issues in production | Medium | Medium | Load testing prior to deployment, gradual rollout |

## Technical Specifications

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Frontend service
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NODE_ENV=${NODE_ENV:-production}
    image: ultrai/frontend:${VERSION:-latest}
    ports:
      - "${FRONTEND_PORT:-3000}:80"
    environment:
      - API_URL=${API_URL:-http://backend:8085}
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # Backend API service
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        - PYTHON_ENV=${PYTHON_ENV:-production}
    image: ultrai/backend:${VERSION:-latest}
    ports:
      - "${BACKEND_PORT:-8085}:8085"
    environment:
      - MONGODB_URI=${MONGODB_URI:-mongodb://mongodb:27017/ultrai}
      - REDIS_URI=${REDIS_URI:-redis://redis:6379/0}
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
    depends_on:
      - mongodb
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8085/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s

  # MongoDB database
  mongodb:
    image: mongo:5.0
    ports:
      - "${MONGODB_PORT:-27017}:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGODB_ROOT_USER:-admin}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGODB_ROOT_PASSWORD:-adminpassword}
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017 --quiet
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  # Redis cache
  redis:
    image: redis:6.2-alpine
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mongodb_data:
  redis_data:
```

### Deployment Script

```bash
#!/bin/bash
set -e

# Configuration
VERSION="$1"
ENV="$2"
DEPLOY_DIR="/opt/ultrai/${ENV}"
BACKUP_DIR="/opt/ultrai/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Validation
if [ -z "$VERSION" ] || [ -z "$ENV" ]; then
  echo "Usage: $0 <version> <environment>"
  echo "Example: $0 1.0.0 production"
  exit 1
fi

# Load environment-specific configuration
echo "Loading configuration for ${ENV} environment..."
source "./env.${ENV}"

# Backup current deployment
echo "Backing up current deployment..."
if [ -d "$DEPLOY_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
  cp -r "$DEPLOY_DIR" "${BACKUP_DIR}/ultrai_${ENV}_${TIMESTAMP}"
  cp "${DEPLOY_DIR}/.env" "${BACKUP_DIR}/ultrai_${ENV}_${TIMESTAMP}/.env.backup"
fi

# Prepare deployment directory
echo "Preparing deployment directory..."
mkdir -p "$DEPLOY_DIR"

# Export version for Docker Compose
export VERSION="$VERSION"

# Copy deployment files
echo "Copying deployment files..."
cp -r docker-compose.yml "$DEPLOY_DIR"
cp -r .env.template "$DEPLOY_DIR/.env"

# Update environment variables
echo "Updating environment variables..."
for var in $(compgen -e | grep '^ULTRAI_'); do
  key=${var#ULTRAI_}
  value=${!var}
  sed -i "s#{{$key}}#$value#g" "$DEPLOY_DIR/.env"
done

# Pull/build Docker images
echo "Building Docker images..."
cd "$DEPLOY_DIR"
docker-compose pull || true
docker-compose build

# Run pre-deployment tests
echo "Running pre-deployment tests..."
docker-compose run --rm backend pytest -xvs tests/deployment/

# Deploy services
echo "Deploying services..."
docker-compose up -d

# Verify deployment
echo "Verifying deployment..."
for i in {1..30}; do
  if curl -s http://localhost:${BACKEND_PORT:-8085}/health | grep -q "healthy"; then
    echo "Backend is healthy!"
    BACKEND_HEALTHY=true
    break
  fi
  echo "Waiting for backend to become healthy... ($i/30)"
  sleep 2
done

if [ -z "$BACKEND_HEALTHY" ]; then
  echo "ERROR: Backend failed to become healthy within timeout"
  echo "Rolling back deployment..."
  ./rollback.sh "$ENV" "${TIMESTAMP}"
  exit 1
fi

for i in {1..30}; do
  if curl -s http://localhost:${FRONTEND_PORT:-3000}/health | grep -q "healthy"; then
    echo "Frontend is healthy!"
    FRONTEND_HEALTHY=true
    break
  fi
  echo "Waiting for frontend to become healthy... ($i/30)"
  sleep 2
done

if [ -z "$FRONTEND_HEALTHY" ]; then
  echo "ERROR: Frontend failed to become healthy within timeout"
  echo "Rolling back deployment..."
  ./rollback.sh "$ENV" "${TIMESTAMP}"
  exit 1
fi

# Run post-deployment tests
echo "Running post-deployment tests..."
docker-compose run --rm backend pytest -xvs tests/e2e/

# Deployment successful
echo "Deployment of version ${VERSION} to ${ENV} successful!"
echo "Deployed at: $(date)"
echo "${VERSION}" > "$DEPLOY_DIR/version.txt"
```

### Rollback Script

```bash
#!/bin/bash
set -e

# Configuration
ENV="$1"
BACKUP_TIMESTAMP="$2"
DEPLOY_DIR="/opt/ultrai/${ENV}"
BACKUP_DIR="/opt/ultrai/backups"

# Validation
if [ -z "$ENV" ] || [ -z "$BACKUP_TIMESTAMP" ]; then
  echo "Usage: $0 <environment> <backup_timestamp>"
  echo "Example: $0 production 20250511_123045"
  exit 1
fi

BACKUP_PATH="${BACKUP_DIR}/ultrai_${ENV}_${BACKUP_TIMESTAMP}"

# Check backup exists
if [ ! -d "$BACKUP_PATH" ]; then
  echo "ERROR: Backup not found at ${BACKUP_PATH}"
  
  # List available backups
  echo "Available backups:"
  ls -l "${BACKUP_DIR}" | grep "ultrai_${ENV}_"
  exit 1
fi

# Stop current deployment
echo "Stopping current deployment..."
cd "$DEPLOY_DIR"
docker-compose down

# Restore from backup
echo "Restoring from backup ${BACKUP_TIMESTAMP}..."
rm -rf "${DEPLOY_DIR}/*"
cp -r "${BACKUP_PATH}/"* "$DEPLOY_DIR"
cp "${BACKUP_PATH}/.env.backup" "${DEPLOY_DIR}/.env"

# Start restored services
echo "Starting restored services..."
cd "$DEPLOY_DIR"
docker-compose up -d

# Verify rollback
echo "Verifying rollback..."
for i in {1..30}; do
  if curl -s http://localhost:${BACKEND_PORT:-8085}/health | grep -q "healthy"; then
    echo "Backend is healthy after rollback!"
    BACKEND_HEALTHY=true
    break
  fi
  echo "Waiting for backend to become healthy after rollback... ($i/30)"
  sleep 2
done

if [ -z "$BACKEND_HEALTHY" ]; then
  echo "ERROR: Backend failed to become healthy after rollback"
  exit 1
fi

echo "Rollback to backup ${BACKUP_TIMESTAMP} successful!"
echo "Rollback completed at: $(date)"
```

### Environment Configuration

```bash
# .env.template
# Base Configuration
NODE_ENV={{NODE_ENV}}
PYTHON_ENV={{PYTHON_ENV}}
VERSION={{VERSION}}

# Port Configuration
FRONTEND_PORT={{FRONTEND_PORT}}
BACKEND_PORT={{BACKEND_PORT}}
MONGODB_PORT={{MONGODB_PORT}}
REDIS_PORT={{REDIS_PORT}}

# Database Configuration
MONGODB_URI={{MONGODB_URI}}
MONGODB_ROOT_USER={{MONGODB_ROOT_USER}}
MONGODB_ROOT_PASSWORD={{MONGODB_ROOT_PASSWORD}}

# Redis Configuration
REDIS_URI={{REDIS_URI}}

# API Keys
OPENAI_API_KEY={{OPENAI_API_KEY}}
CLAUDE_API_KEY={{CLAUDE_API_KEY}}
COHERE_API_KEY={{COHERE_API_KEY}}

# Logging
LOG_LEVEL={{LOG_LEVEL}}

# Security
JWT_SECRET={{JWT_SECRET}}
JWT_EXPIRY={{JWT_EXPIRY}}
CORS_ORIGINS={{CORS_ORIGINS}}
```

## Implementation Details

### Verification Tests

```python
# tests/deployment/test_deployment.py

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("API_URL", "http://localhost:8085")

def test_health_endpoint():
    """Verify the health endpoint is responding correctly."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    
def test_database_connection():
    """Verify the database connection is working."""
    response = requests.get(f"{BASE_URL}/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    
def test_redis_connection():
    """Verify the Redis connection is working."""
    response = requests.get(f"{BASE_URL}/health/redis")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    
def test_llm_providers():
    """Verify LLM provider connections."""
    response = requests.get(f"{BASE_URL}/health/llm-providers")
    assert response.status_code == 200
    data = response.json()
    
    # At least one provider should be available
    available_providers = [p for p in data["providers"] if p["status"] == "available"]
    assert len(available_providers) > 0
    
def test_api_endpoints():
    """Test critical API endpoints."""
    # This is a basic smoke test - more comprehensive tests in e2e
    endpoints = [
        "/api/models",
        "/api/analysis-patterns"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code in (200, 401), f"Endpoint {endpoint} failed with {response.status_code}"
```

### Deployment Documentation

The deployment documentation will include:

1. **Release Process**
   - Pre-release checklist
   - Deployment steps
   - Verification procedures
   - Rollback instructions

2. **Environment Setup**
   - Development environment setup
   - Staging environment configuration
   - Production environment requirements

3. **Troubleshooting Guide**
   - Common deployment issues
   - Log inspection guidelines
   - Health check interpretation

4. **Maintenance Procedures**
   - Backup and restore
   - Database maintenance
   - Log rotation and cleanup

## Documentation Plan

The following documentation will be created:
- Deployment pipeline overview
- Environment configuration guide
- Release process documentation
- Rollback procedures
- Deployment verification guidelines
- Troubleshooting guide