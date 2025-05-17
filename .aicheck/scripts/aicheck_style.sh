#!/bin/bash

# AICheck style script
# This script sets up and maintains AICheck directory styling

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to set up directory styling
setup_style() {
    # Create necessary directories
    mkdir -p .aicheck/sessions
    mkdir -p .aicheck/hooks
    mkdir -p .aicheck/scripts
    mkdir -p .aicheck/actions
    mkdir -p .aicheck/templates
    mkdir -p .aicheck/docs

    # Set up Git hooks
    if [ -d ".git" ]; then
        if [ ! -f ".git/hooks/pre-commit" ]; then
            ln -s ../../.aicheck/hooks/pre-commit .git/hooks/pre-commit
        fi
    fi

    echo -e "${GREEN}AICheck directory styling has been set up.${NC}"
    echo "Please add the following line to your shell's configuration file:"
    echo "source ~/.aicheck/scripts/aicheck_style.sh"
}

# Main script
setup_style
