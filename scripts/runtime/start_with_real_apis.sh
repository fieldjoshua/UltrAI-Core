#!/bin/bash

echo "🚀 Starting UltraAI with Real APIs..."

# Kill any existing backend processes
echo "🔧 Stopping existing processes..."
pkill -f "python.*app.py" 2>/dev/null
lsof -ti:8085 | xargs -r kill -9 2>/dev/null
sleep 2

# Check for API keys in environment
echo "🔑 Checking API Keys..."
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "  ✅ OpenAI API Key found"
else
    echo "  ⚠️  OpenAI API Key not found"
fi

if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo "  ✅ Anthropic API Key found"
else
    echo "  ⚠️  Anthropic API Key not found"
fi

if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo "  ✅ Google API Key found"
else
    echo "  ⚠️  Google API Key not found"
fi

# Start backend with explicit environment variables and no mock mode
echo ""
echo "🚀 Starting backend with real APIs..."
cd /Users/joshuafield/Documents/Ultra

# Export the variables and start the backend
PYTHONPATH=. \
ENABLE_AUTH=false \
MOCK_MODE=false \
OPENAI_API_KEY="$OPENAI_API_KEY" \
ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
GOOGLE_API_KEY="$GOOGLE_API_KEY" \
python backend/app.py &

# Wait a moment for startup
sleep 5

# Test the connection
echo ""
echo "🧪 Testing backend connection..."
if curl -s http://localhost:8085/api/available-models > /dev/null; then
    echo "✅ Backend is running and responding!"
    echo "🌐 Frontend: http://localhost:3009/analyze"
    echo "🔗 Backend: http://localhost:8085"
else
    echo "❌ Backend not responding. Check the logs above."
fi