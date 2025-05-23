#!/bin/bash

# Set Python path to avoid import issues
export PYTHONPATH=/app:$PYTHONPATH

# Disable Redis if not configured
if [ -z "$REDIS_URL" ]; then
    export USE_MOCK_REDIS=true
fi

# Start gunicorn with explicit single worker and correct port
exec gunicorn \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-10000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    backend.app:app