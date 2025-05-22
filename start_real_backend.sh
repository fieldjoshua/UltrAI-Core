#!/bin/bash

echo "🚀 Starting UltraAI Backend with Real APIs..."
echo ""

# Check for API keys
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ No API keys found!"
    echo ""
    echo "Please set at least one API key:"
    echo "export OPENAI_API_KEY='sk-your-key-here'"
    echo "export ANTHROPIC_API_KEY='sk-ant-your-key-here'"
    echo "export GOOGLE_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

# Show which APIs are configured
echo "✅ API Keys Status:"
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "  🤖 OpenAI: Configured (${OPENAI_API_KEY:0:10}...)"
fi
if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo "  🧠 Anthropic: Configured (${ANTHROPIC_API_KEY:0:10}...)"
fi
if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo "  🔍 Google: Configured (${GOOGLE_API_KEY:0:10}...)"
fi
echo ""

# Kill any existing processes on port 8085
echo "🔧 Cleaning up existing processes..."
lsof -ti:8085 | xargs -r kill -9 2>/dev/null
sleep 2

# Start the backend
echo "🚀 Starting backend with real APIs..."
cd /Users/joshuafield/Documents/Ultra
PYTHONPATH=. ENABLE_AUTH=false MOCK_MODE=false python backend/app.py