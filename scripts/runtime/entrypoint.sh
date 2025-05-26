#!/bin/bash

# Set default port if not provided
PORT=${PORT:-8000}

# Start the application
exec gunicorn backend.app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level info