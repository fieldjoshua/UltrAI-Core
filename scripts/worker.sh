#!/bin/bash
set -e

# Wait for database and backend to be ready
echo "Waiting for database to be ready..."
python -m backend.utils.wait_for_db

echo "Waiting for backend to be ready..."
until $(curl --output /dev/null --silent --head --fail http://backend:8000/api/health); do
    printf '.'
    sleep 2
done

# Start the background worker
echo "Starting Ultra worker..."
exec python -m backend.worker.main