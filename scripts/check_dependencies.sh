#!/bin/bash

# Script to check and install missing dependencies before starting the backend

# Set error handling
set -e

echo "Checking for missing dependencies..."

# List of critical packages to check
CRITICAL_PACKAGES=(
  "prometheus_client"
  "fastapi"
  "uvicorn"
  "pydantic"
  "sqlalchemy"
  "httpx"
)

# Function to check if a package is installed
check_package() {
  python -c "import $1" 2>/dev/null
  return $?
}

# Check and install missing packages
MISSING_PACKAGES=()
for package in "${CRITICAL_PACKAGES[@]}"; do
  echo "Checking $package..."
  if ! check_package $package; then
    echo "Package $package is missing, will be installed."
    MISSING_PACKAGES+=("$package")
  fi
done

# Install missing packages if any
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
  echo "Installing missing packages: ${MISSING_PACKAGES[*]}"
  for package in "${MISSING_PACKAGES[@]}"; do
    pip install --no-cache-dir $package
  done
  echo "All missing packages have been installed."
else
  echo "All dependencies are already installed."
fi

echo "Dependency check completed successfully."

# Check and install gunicorn if not found
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Use python module if gunicorn command not found
if ! command -v gunicorn &> /dev/null; then
    echo "Starting with python -m gunicorn..."
    exec python -m gunicorn --config gunicorn_conf.py backend.app:app
else
    exec gunicorn --config gunicorn_conf.py backend.app:app
fi
