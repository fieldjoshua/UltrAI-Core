#!/bin/bash
set -e

# Check and install gunicorn if needed
if ! command -v gunicorn &> /dev/null; then
    echo "Gunicorn not found, installing..."
    pip install gunicorn
fi

# Run dependency check
/app/scripts/check_dependencies.sh

# Start the application with gunicorn
exec gunicorn --config gunicorn_conf.py backend.app:app
