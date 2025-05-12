#!/bin/bash
set -e

# Create necessary directories
mkdir -p logs
mkdir -p document_storage
mkdir -p temp
mkdir -p temp_uploads

# Wait for database to be ready
echo "Waiting for database to be ready..."
python -m backend.utils.wait_for_db

# Skip database migrations for now since alembic is not installed
echo "Skipping database migrations (alembic not installed)"

# Start the FastAPI application with auto-reload for development
echo "Starting Ultra backend in development mode..."
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload