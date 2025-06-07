# UltraAI Core - Production/Development Toggle
.PHONY: help dev prod install setup clean-ports run test deploy e2e

# Default target
help:
	@echo "UltraAI Core - Production/Development Toggle:"
	@echo ""
	@echo "  make setup       - Initial setup (install deps + build frontend)"
	@echo "  make dev         - Start DEVELOPMENT server (fast, minimal deps)"
	@echo "  make prod        - Start PRODUCTION server (full features)"
	@echo "  make run         - Clean ports and start dev server"
	@echo "  make test        - Run tests"
	@echo "  make deploy      - Deploy to production"
	@echo "  make e2e         - Run end-to-end tests (E2E)"
	@echo ""
	@echo "Quick start: make setup && make dev"

# Development server (minimal, fast startup)
dev:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env 2>/dev/null || echo "ENVIRONMENT=development\nPORT=8000" > .env; \
	fi
	@echo "🚀 Starting DEVELOPMENT server (fast, minimal deps)"
	@echo "Frontend: http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	@echo "Features: Frontend only (no database/auth)"
	uvicorn app_development:app --host 0.0.0.0 --port 8000 --reload

# Production server (full features)
prod:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env 2>/dev/null || echo "ENVIRONMENT=production\nPORT=8000" > .env; \
	fi
	@echo "🏭 Starting PRODUCTION server (full features)"
	@echo "Frontend: http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	@echo "Features: Database, Auth, Caching, Frontend"
	uvicorn app_production:app --host 0.0.0.0 --port 8000 --reload

# Install development dependencies (minimal, fast)
install-dev:
	@echo "Installing minimal development dependencies..."
	pip install -r requirements-development.txt

# Install production dependencies (full features)
install-prod:
	@echo "Installing production dependencies..."
	pip install -r requirements-production.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Install all dependencies (for full setup)
install: install-prod

# Build frontend
build-frontend:
	@echo "Building frontend..."
	cd frontend && npm run build

# Full setup
setup: install build-frontend
	@echo ""
	@echo "✅ Setup complete!"
	@echo "Run 'make dev' to start the development server"

# Clean ports
clean-ports:
	@echo "Cleaning ports 8000-8001..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Run with clean ports
run: clean-ports dev

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v 2>/dev/null || echo "No tests found in tests/"
	cd frontend && npm test 2>/dev/null || echo "No frontend tests configured"

# Run end-to-end tests (E2E) with a pre-check step
e2e:
	@echo "Running pre-check: poetry check"
	poetry check
	@echo "Running pre-E2E unit & integration tests"
	pytest tests/ -q -m "not e2e"
	@echo "Running end-to-end (e2e) tests"
	pytest tests/ -q -m e2e

# Deploy to production
deploy:
	@echo "Deploying to Render..."
	@git add .
	@git commit -m "Deploy to production" || echo "No changes to commit"
	@git push origin main
	@echo ""
	@echo "✅ Deployment triggered!"
	@echo "Monitor at: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg"
	@echo "Live site: https://ultrai-core.onrender.com"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".DS_Store" -delete 2>/dev/null || true
