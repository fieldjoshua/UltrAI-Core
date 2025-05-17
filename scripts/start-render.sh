#!/bin/bash
set -e

echo "=== Debug: Environment Info ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "PATH: $PATH"
echo

echo "=== Debug: Checking installed packages ==="
pip list | grep -E "(gunicorn|fastapi|uvicorn)" || echo "No packages found"
echo

echo "=== Debug: Looking for gunicorn ==="
which gunicorn || echo "gunicorn not found in PATH"
find /usr/local -name gunicorn 2>/dev/null || echo "gunicorn not found in /usr/local"
echo

echo "=== Debug: Installing gunicorn directly ==="
pip install gunicorn
echo

echo "=== Debug: Gunicorn location after install ==="
which gunicorn || echo "Still not in PATH"
python -m site --user-site
echo

echo "=== Starting application with direct python module ==="
echo "Running: python -m gunicorn --config gunicorn_conf.py backend.app:app"
exec python -m gunicorn --config gunicorn_conf.py backend.app:app
