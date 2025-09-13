#!/bin/bash
# Run tests in MOCK mode - sophisticated mocks with realistic behavior

echo "🎭 Running tests in MOCK mode (sophisticated mocks)"
echo "=================================================="

# Set test mode
export TEST_MODE=MOCK

# Set required environment variables
export JWT_SECRET_KEY="test-secret-key"
export ENVIRONMENT="test"
export DATABASE_URL="sqlite:///:memory:"
export REDIS_URL="redis://localhost:6379/1"

# Run tests with mock configuration
pytest tests/ \
    -v \
    --tb=short \
    --color=yes \
    -m "not live and not live_online and not production" \
    "$@"