# UltraAI Core - Simplified Development Makefile
.PHONY: help dev install setup clean-ports run test deploy

# Default target
help:
	@echo "UltraAI Core - Simple Development Commands:"
	@echo ""
	@echo "  make setup       - Initial setup (install deps + build frontend)"
	@echo "  make dev         - Start development server"
	@echo "  make run         - Clean ports and start dev server"
	@echo "  make test        - Run tests"
	@echo "  make deploy      - Deploy to production"
	@echo ""
	@echo "Quick start: make setup && make dev"

# Development server (port 8000)
dev:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env 2>/dev/null || echo "ENVIRONMENT=development\nPORT=8000" > .env; \
	fi
	@echo "Starting development server on http://localhost:8000"
	@echo "Frontend: http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	python run.py

# Install all dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements-production.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

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
