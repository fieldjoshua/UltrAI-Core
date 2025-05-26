# Development & Deployment Strategy

## Current Problems

1. **Multiple Deployment Configurations**:
   - Docker files (Dockerfile, docker-compose.yml)
   - Render configurations (render.yaml)
   - Local development scripts
   - No clear "source of truth"

2. **Environment Toggle Issues**:
   - Development vs Production confusion
   - Port conflicts (8000, 8001, etc.)
   - Different configurations in different files

3. **Frontend Deployment Confusion**:
   - Originally separate service
   - Now served from backend
   - Still referenced in multiple places

## Recommended Solution: Render-First Strategy

### Why Render?
- Already working in production
- Free tier available
- Simple deployment from GitHub
- No Docker complexity for deployment
- Handles HTTPS, scaling, monitoring

### Development Setup

#### 1. Single Configuration File
Create `.env.example`:
```
# Development
ENVIRONMENT=development
PORT=8000
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key

# Production (set in Render dashboard)
# ENVIRONMENT=production
# PORT=$PORT
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://...
# JWT_SECRET=<generated>
```

#### 2. Single Entry Point
`run.py`:
```python
import os
import uvicorn
from app_production import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "development":
        # Development: hot reload, debug mode
        uvicorn.run("app_production:app", 
                   host="0.0.0.0", 
                   port=port, 
                   reload=True)
    else:
        # Production: no reload, optimized
        uvicorn.run(app, 
                   host="0.0.0.0", 
                   port=port)
```

#### 3. Development Commands
`Makefile`:
```makefile
# Development
dev:
	cp .env.example .env
	python run.py

# Install dependencies
install:
	pip install -r requirements-production.txt
	cd frontend && npm install

# Build frontend
build-frontend:
	cd frontend && npm run build

# Full setup
setup: install build-frontend

# Clean ports
clean-ports:
	lsof -ti:8000 | xargs kill -9 || true
	lsof -ti:8001 | xargs kill -9 || true

# Run with clean ports
run: clean-ports dev
```

### Deployment Strategy

#### 1. GitHub → Render Pipeline
- Push to main branch
- Render auto-deploys
- No manual Docker builds
- No complex CI/CD

#### 2. Render Configuration
Keep simple `render.yaml`:
```yaml
services:
  - type: web
    name: ultrai-core
    runtime: python
    buildCommand: "pip install -r requirements-production.txt && cd frontend && npm install && npm run build"
    startCommand: "python run.py"
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: JWT_SECRET
        generateValue: true
    healthCheckPath: /health
```

#### 3. Remove/Archive Docker Files
Move to `archive/docker/`:
- Dockerfile*
- docker-compose*.yml
- Docker-related scripts

### Frontend Strategy

#### 1. Single Service Architecture
- Frontend served from backend at root
- API endpoints at `/api/*`
- Static files handled by FastAPI

#### 2. Remove Frontend Confusion
- Delete references to separate frontend service
- Update all documentation
- Single URL: ultrai-core.onrender.com

### Port Management

#### 1. Standard Ports
- Development: 8000 (always)
- Production: $PORT (Render provides)
- No more port hunting

#### 2. Port Conflict Resolution
```bash
# Add to ~/.bashrc or ~/.zshrc
alias killport='function _killport(){ lsof -ti:$1 | xargs kill -9; }; _killport'

# Usage
killport 8000
```

## Implementation Steps

1. **Clean Up** (30 min):
   - Archive Docker files
   - Remove duplicate configs
   - Clean up scripts folder

2. **Create Single Config** (30 min):
   - Create .env.example
   - Create run.py
   - Create Makefile

3. **Update Documentation** (30 min):
   - README with clear instructions
   - Remove Docker references
   - Single deployment guide

4. **Test & Deploy** (30 min):
   - Test local development
   - Push to GitHub
   - Verify Render deployment

## Benefits

1. **Simplicity**: One way to develop, one way to deploy
2. **Consistency**: Same code runs locally and in production
3. **No Port Issues**: Fixed ports, clean commands
4. **No Docker Complexity**: Unless you specifically need it
5. **Free Hosting**: Render free tier is sufficient

## Future Options

If you need Docker later:
- Keep it separate in `docker/` folder
- Use for specific microservices only
- Not for main deployment

## Summary

**Development**: `make run` (port 8000)
**Deployment**: `git push origin main` (Render handles rest)
**Frontend**: Always at root URL
**No more confusion!**