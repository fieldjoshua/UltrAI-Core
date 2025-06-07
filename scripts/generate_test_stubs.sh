#!/usr/bin/env bash
set -e

# Script to scaffold pytest stubs for service modules without tests
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_SERVICES_DIR="$BASE_DIR/app/services"
TEST_DIR="$BASE_DIR/tests"

mkdir -p "$TEST_DIR"

for svc in "$APP_SERVICES_DIR"/*.py; do
  module=$(basename "$svc" .py)
  # Skip __init__ and private modules
  if [[ "$module" == "__init__" || "$module" == _* ]]; then
    continue
  fi
  test_file="$TEST_DIR/test_${module}.py"
  if [[ ! -f "$test_file" ]]; then
    echo "Scaffolding $test_file"
    cat > "$test_file" <<EOF
import pytest
from app.services.${module} import *  # noqa: F401,F403

# TODO: Implement unit tests for ${module}

EOF
  fi
done