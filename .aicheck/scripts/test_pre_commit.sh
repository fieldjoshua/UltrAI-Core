#!/bin/bash

# Test script for pre-commit hooks
# This script verifies that the pre-commit hooks are working correctly

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Security functions
validate_path() {
    local path="$1"
    if [[ "$path" != .aicheck/* ]]; then
        echo -e "${RED}Error: Invalid path access attempt${NC}"
        exit 1
    fi
}

check_permissions() {
    local file="$1"
    if [[ ! -O "$file" ]]; then
        echo -e "${RED}Error: Insufficient permissions for $file${NC}"
        exit 1
    fi
}

# Function to check if a file exists
check_file() {
    local file="$1"
    validate_path "$file"
    if [ -f "$file" ]; then
        check_permissions "$file"
        echo -e "${GREEN}✓${NC} $file exists"
        return 0
    else
        echo -e "${RED}✗${NC} $file does not exist"
        return 1
    fi
}

# Function to check if a file is executable
check_executable() {
    local file="$1"
    validate_path "$file"
    if [ -x "$file" ]; then
        check_permissions "$file"
        echo -e "${GREEN}✓${NC} $file is executable"
        return 0
    else
        echo -e "${RED}✗${NC} $file is not executable"
        return 1
    fi
}

# Main test function
run_tests() {
    echo "Running pre-commit hook tests..."
    echo "--------------------------------"

    # Check if pre-commit hook exists
    check_file ".aicheck/hooks/pre-commit"

    # Check if pre-commit hook is executable
    check_executable ".aicheck/hooks/pre-commit"

    # Check if style script exists
    check_file ".aicheck/scripts/aicheck_style.sh"

    # Check if style script is executable
    check_executable ".aicheck/scripts/aicheck_style.sh"

    echo "--------------------------------"
    echo "Tests completed"
}

# Run the tests
run_tests
