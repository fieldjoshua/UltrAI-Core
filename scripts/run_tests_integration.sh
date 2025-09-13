#!/bin/bash
# Run tests in INTEGRATION mode - local services but mocked APIs

echo "🧪 Running tests in INTEGRATION mode..."
echo "✓ Using local Redis (if available)"
echo "✓ Using local PostgreSQL (if available)" 
echo "✓ LLM APIs mocked"
echo ""

export TEST_MODE=integration
source venv/bin/activate 2>/dev/null || true
pytest tests/ -v "$@"