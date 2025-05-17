#!/bin/bash
# Setup script for AuditEngine performance dependencies

set -e

echo "Setting up AuditEngine performance dependencies..."

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo "Error: Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

# Install core dependencies
pip install -q requests>=2.28.0 packaging>=21.0 toml>=0.10.2

# Install performance dependencies
pip install -q numpy>=1.21.0 numba>=0.61.0

# Optional: Install PyPy if requested
if [ "$INSTALL_PYPY" = "true" ]; then
    echo "Installing PyPy for additional performance..."
    # Platform-specific PyPy installation would go here
fi

echo "AuditEngine dependencies installed successfully!"
