#!/bin/bash
# Run tests in LIVE mode - real API calls to LLM providers

echo "🧪 Running tests in LIVE mode..."
echo "⚠️  Requires API keys for:"
echo "   - OpenAI"
echo "   - Anthropic"
echo "   - Google Gemini"
echo "   - HuggingFace"
echo ""

# Check for required API keys
if [ -z "$OPENAI_API_KEY" ] || [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Missing required API keys!"
    echo "Please set: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
    exit 1
fi

export TEST_MODE=live
source venv/bin/activate 2>/dev/null || true
pytest tests/ -v -m "" "$@"  # Empty marker to run all tests