#!/bin/bash
set -e

# Define the port
PORT=8000

# Source the port clearing utility
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/clear_port.sh"

# Clear the port before starting
clear_port $PORT

# Check for required dependencies
echo "Checking for missing dependencies..."
# Install prometheus_client if missing
if ! python -c "import prometheus_client" &>/dev/null; then
    echo "Installing prometheus_client package..."
    pip install prometheus_client
fi
# Using stubs for other missing dependencies

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
python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT --reload
