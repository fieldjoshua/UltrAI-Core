#!/bin/bash
# Start the complete Ultra stack with Docker Compose and Docker Model Runner

# Ensure necessary directories exist
mkdir -p logs
mkdir -p document_storage
mkdir -p temp
mkdir -p temp_uploads

# Set environment variables
export USE_MODEL_RUNNER=true
export ENABLE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=cli
export DEFAULT_LOCAL_MODEL=ai/smollm2

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker Model Runner
echo "Checking Docker Model Runner..."
docker model list
if [ $? -ne 0 ]; then
    echo "Docker Model Runner is not available or not working"
    echo "Make sure Docker Desktop is running and Docker Model Runner is enabled"
    exit 1
fi

# Start with docker-compose
echo "Starting Ultra stack with Docker Compose..."
echo "This will include backend, database, and Redis services"
echo "Frontend will be available at http://localhost:3009"
echo "Backend API will be available at http://localhost:8000"

# Use docker-compose v2 syntax if available
if docker compose version &> /dev/null; then
    docker compose up --build "$@"
else
    docker-compose up --build "$@"
fi
