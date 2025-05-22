# UltraAI Core - Development Guide

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/fieldjoshua/UltrAI-Core.git
cd UltrAI-Core

# 2. Setup (one time)
make setup

# 3. Run development server
make dev

# 4. Open in browser
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Development Workflow

### Daily Development
```bash
# Start development server (port 8000)
make dev

# If port conflicts
make run  # This cleans ports first

# Run tests
make test
```

### Frontend Development
The frontend is automatically served from the backend. Any changes to frontend code require:
```bash
cd frontend
npm run build
```

Or use the Makefile:
```bash
make build-frontend
```

### Deployment
```bash
# Deploy to production (Render)
make deploy

# Or manually
git push origin main
```

## Architecture

### Single Service
- Backend serves both API and frontend
- Frontend at root URL (`/`)
- API endpoints at various paths (`/auth/*`, `/documents/*`, etc.)
- API documentation at `/docs`

### No Docker Required
- Development: Direct Python/Node
- Production: Render handles everything
- Docker files archived for future use if needed

## Environment Configuration

### Development (.env)
```
ENVIRONMENT=development
PORT=8000
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379
JWT_SECRET=dev-secret-key
```

### Production (Render Dashboard)
All production environment variables are set in Render dashboard:
- DATABASE_URL (PostgreSQL)
- REDIS_URL (Redis)
- JWT_SECRET (generated)
- PORT (provided by Render)

## Common Issues

### Port Already in Use
```bash
make run  # Automatically cleans ports
# Or manually:
lsof -ti:8000 | xargs kill -9
```

### Frontend Not Loading
1. Check if frontend is built: `ls frontend/dist`
2. If not: `make build-frontend`
3. Restart server: `make dev`

### Database Issues
- Development uses SQLite (no setup needed)
- File: `test.db` in project root
- Delete to reset: `rm test.db`

## Project Structure
```
UltrAI-Core/
├── app_production.py      # Main application
├── run.py                # Unified entry point
├── Makefile              # Development commands
├── .env.example          # Environment template
├── requirements-production.txt
├── frontend/             # React frontend
│   ├── dist/            # Built frontend (served by backend)
│   └── src/             # Frontend source
├── tests/               # Test files
└── render.yaml          # Render deployment config
```

## Key Commands Summary

| Command | Description |
|---------|-------------|
| `make setup` | Initial setup |
| `make dev` | Start development server |
| `make run` | Clean ports + start server |
| `make test` | Run tests |
| `make deploy` | Deploy to production |
| `make build-frontend` | Build frontend assets |

## No More Confusion!

- **One way to develop**: `make dev`
- **One way to deploy**: `make deploy`
- **One port**: 8000 (always)
- **One URL**: http://localhost:8000 (dev) or https://ultrai-core.onrender.com (prod)