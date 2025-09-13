#!/bin/bash
# Run tests in PRODUCTION mode - tests against deployed production endpoints

echo "🚀 Running tests in PRODUCTION mode (against deployed endpoints)"
echo "================================================================"
echo "⚠️  WARNING: This will test against the live production environment!"
echo ""

read -p "Are you sure you want to run tests against production? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Check production availability
echo "Checking production endpoint..."
if ! curl -s -f -o /dev/null "https://ultrai-core.onrender.com/"; then
    echo "❌ Production endpoint is not responding"
    exit 1
else
    echo "✅ Production endpoint is available"
fi

# Set test mode
export TEST_MODE=PRODUCTION

# Set production test token if available
if [ -n "$PRODUCTION_TEST_TOKEN" ]; then
    echo "✅ Using PRODUCTION_TEST_TOKEN for authentication"
else
    echo "⚠️  PRODUCTION_TEST_TOKEN not set, authentication tests may fail"
fi

# Run tests with production configuration
pytest tests/ \
    -v \
    --tb=short \
    --color=yes \
    --timeout=180 \
    -m "production or e2e" \
    "$@"