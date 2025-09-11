#!/bin/bash
# Run tests in OFFLINE mode - fast, no external dependencies

echo "🧪 Running tests in OFFLINE mode..."
echo "✓ All external services mocked"
echo "✓ No network calls"
echo "✓ Fast execution"
echo ""

export TEST_MODE=offline
source venv/bin/activate 2>/dev/null || true
pytest tests/ -v "$@"