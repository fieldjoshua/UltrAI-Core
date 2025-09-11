# UltraAI Core - Production/Development Toggle
.PHONY: help dev prod install setup clean-ports run test test-offline test-mock test-integration test-live test-production deploy e2e

# Default target
help:
	@echo "UltraAI Core - Production/Development Toggle:"
	@echo ""
	@echo "  make setup       - Initial setup (install deps + build frontend)"
	@echo "  make dev         - Start DEVELOPMENT server (fast, minimal deps)"
	@echo "  make prod        - Start PRODUCTION server (full features)"
	@echo "  make run         - Clean ports and start dev server"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test        - Run offline tests with mocks (default)"
	@echo "  make test-mock   - Run tests with sophisticated mocks"
	@echo "  make test-integration - Run integration tests with local services"
	@echo "  make test-live   - Run tests against real LLM providers"
	@echo "  make test-production - Run tests against production endpoints"
	@echo "  make e2e         - Run end-to-end tests (E2E)"
	@echo ""
	@echo "  make deploy      - Deploy to production"
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

# Run tests (default: offline mode with mocks)
test: test-offline

# Run tests in OFFLINE mode (all external dependencies mocked)
test-offline:
	@echo "🧪 Running tests in OFFLINE mode..."
	@. venv/bin/activate && TEST_MODE=offline pytest tests/ -v

# Run tests in MOCK mode (sophisticated mocks)
test-mock:
	@echo "🧪 Running tests in MOCK mode..."
	@. venv/bin/activate && TEST_MODE=mock pytest tests/ -v

# Run tests in INTEGRATION mode (local services)
test-integration:
	@echo "🧪 Running tests in INTEGRATION mode..."
	@. venv/bin/activate && TEST_MODE=integration pytest tests/ -v

# Run tests in LIVE mode (real LLM providers)
test-live:
	@echo "🧪 Running tests in LIVE mode..."
	@echo "⚠️  Requires API keys for LLM providers"
	@. venv/bin/activate && TEST_MODE=live pytest tests/ -v -m ""

# Run tests in PRODUCTION mode (against deployed endpoints)
test-production:
	@echo "🧪 Running tests in PRODUCTION mode..."
	@echo "⚠️  Tests against production endpoints"
	@. venv/bin/activate && TEST_MODE=production pytest tests/ -v -m ""
	@./scripts/run_tests_production.sh

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
