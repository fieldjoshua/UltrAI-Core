#!/bin/bash
# Start Ultra with Docker Model Runner and cloud LLMs

# Set environment variables for Docker Model Runner
export USE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=cli
export DEFAULT_LOCAL_MODEL=ai/smollm2

# Ensure we have directories needed
mkdir -p logs
mkdir -p temp
mkdir -p document_storage
mkdir -p temp_uploads

echo "Starting Ultra backend with Docker Model Runner and cloud LLMs..."
echo "Using Docker Model Runner with model: $DEFAULT_LOCAL_MODEL"
echo "Cloud LLMs are also enabled (OpenAI, Anthropic, Google)"

# Verify Docker Model CLI is available
if command -v docker &> /dev/null && docker model list &> /dev/null; then
    echo "✅ Docker Model Runner CLI is available"
    echo "Available models:"
    docker model list
else
    echo "⚠️  Docker Model Runner CLI not available or not working"
    echo "Cloud LLMs will still be available"
fi

# Check API keys
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key is set"
else
    echo "⚠️  OpenAI API key is not set"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ Anthropic API key is set"
else
    echo "⚠️  Anthropic API key is not set"
fi

if [ -n "$GOOGLE_API_KEY" ]; then
    echo "✅ Google API key is set"
else
    echo "⚠️  Google API key is not set"
fi

# Run the backend with uvicorn
cd "$(dirname "$0")/.." || exit
python3 -m uvicorn backend.app:app --reload

# Optionally start frontend separately:
# cd frontend && npm run dev
