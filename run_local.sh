#!/bin/bash
set -e

# Export database environment variables
export DB_USER=ultra
export DB_PASSWORD=ultra_dev_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ultra_dev
export USE_MOCK=true

# Create necessary directories
mkdir -p logs
mkdir -p document_storage
mkdir -p temp
mkdir -p temp_uploads

# Start the FastAPI application with auto-reload for development
echo "Starting Ultra backend in development mode..."
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
