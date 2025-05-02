#!/bin/bash

# Export database environment variables
export DB_USER=ultra
export DB_PASSWORD=ultra_dev_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ultra_dev
export USE_MOCK=true

# Start a simple server without auto-reload
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000