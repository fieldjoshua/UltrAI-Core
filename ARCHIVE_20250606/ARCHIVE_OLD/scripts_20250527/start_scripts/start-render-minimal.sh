#!/bin/bash
set -e

echo "=== Starting minimal application ==="
exec python -m gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_health_only:app
