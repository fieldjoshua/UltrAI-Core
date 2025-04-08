#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
python -m backend.utils.wait_for_db

# Run database migrations
echo "Running database migrations..."
cd /app && alembic upgrade head

# Start the FastAPI application with Gunicorn
echo "Starting Ultra backend..."
exec gunicorn --config /app/gunicorn_conf.py backend.app:app