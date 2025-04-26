#!/bin/bash

# UltraAI Development Environment Setup Script

# Exit on error
set -e

# Print commands
set -x

# Check Python version
python3 --version | grep -q "Python 3.9" || {
    echo "Error: Python 3.9+ is required"
    exit 1
}

# Check Node.js version
node --version | grep -q "v18" || {
    echo "Error: Node.js 18+ is required"
    exit 1
}

# Check Git
git --version || {
    echo "Error: Git is required"
    exit 1
}

# Check Docker
docker --version || {
    echo "Error: Docker is required"
    exit 1
}

# Install Poetry
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install pre-commit
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Install Python dependencies
echo "Installing Python dependencies..."
poetry install

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build frontend
echo "Building frontend..."
npm run build

# Build Docker images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Configure Git
echo "Configuring Git..."
git config --local core.hooksPath .git/hooks

echo "Development environment setup complete!"
