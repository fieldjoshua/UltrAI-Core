.PHONY: install install-backend install-frontend install-dev format lint test test-backend test-frontend clean deploy deploy-backend run run-backend run-frontend

# Default target
help:
	@echo "Available commands:"
	@echo "  make install         - Install all dependencies"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make format          - Format code with Black and Prettier"
	@echo "  make lint            - Run linters (flake8, eslint)"
	@echo "  make test            - Run all tests"
	@echo "  make test-backend    - Run backend tests"
	@echo "  make test-frontend   - Run frontend tests"
	@echo "  make clean           - Clean temporary files and caches"
	@echo "  make deploy          - Deploy both frontend and backend"
	@echo "  make deploy-backend  - Deploy only backend"
	@echo "  make run             - Run the application (both frontend and backend)"
	@echo "  make run-backend     - Run only backend"
	@echo "  make run-frontend    - Run only frontend"

# Installation targets
install: install-backend install-frontend install-dev

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

install-dev:
	@echo "Installing development dependencies..."
	pip install pre-commit black flake8 isort pytest
	pre-commit install

# Code formatting and linting
format:
	@echo "Formatting Python code with Black..."
	black .
	@echo "Sorting Python imports with isort..."
	isort .
	@echo "Formatting JavaScript/TypeScript code with Prettier..."
	cd frontend && npx prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"

lint:
	@echo "Linting Python code with flake8..."
	flake8 .
	@echo "Linting JavaScript/TypeScript code with ESLint..."
	cd frontend && npx eslint . --ext .js,.jsx,.ts,.tsx

# Testing
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

# Cleaning
clean:
	@echo "Cleaning temporary files and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name ".cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".DS_Store" -delete
	find . -name "*.log" -delete

# Deployment
deploy: deploy-backend
	@echo "Deploying frontend..."
	cd frontend && npm run build && npx vercel --prod

deploy-backend:
	@echo "Deploying backend..."
	cd backend && bash deploy-backend.sh

# Running the application
run: run-backend run-frontend

run-backend:
	@echo "Starting backend server..."
	cd backend && python main.py

run-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev
