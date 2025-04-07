#!/bin/bash

# Set the desired port
PORT=8081

# Check if the port is in use
echo "Checking if port $PORT is in use..."
if lsof -i :$PORT > /dev/null; then
    echo "Port $PORT is in use. Killing existing process..."
    # Get PID of process using the port
    PID=$(lsof -t -i :$PORT)
    # Kill the process
    kill -9 $PID
    echo "Process killed."
else
    echo "Port $PORT is available."
fi

# Check for --mock flag
MOCK_FLAG=""
if [[ "$*" == *"--mock"* ]]; then
    MOCK_FLAG="--mock"
    echo "Starting server in MOCK MODE..."
    
    # Check if mock_llm_service.py exists
    if [ ! -f "backend/mock_llm_service.py" ]; then
        echo "ERROR: mock_llm_service.py not found in backend directory."
        echo "Creating mock_llm_service.py now..."
        
        cat > backend/mock_llm_service.py << 'EOF'
# backend/mock_llm_service.py
import random
import asyncio
import json

MOCK_RESPONSES = {
    "gpt4o": "This is a mock response from GPT-4. It would analyze your prompt in great detail if this were the real API.",
    "gpt4turbo": "GPT-4 Turbo mock response with even more insightful analysis that would be very helpful.",
    "gpto3mini": "GPT-3.5 Turbo would provide a solid analysis here, though perhaps not as detailed as GPT-4.",
    "claude3opus": "Claude 3 Opus mock response with very thoughtful and well-structured analysis of your prompt.",
    "claude37": "Claude 3 Sonnet would respond with a comprehensive, nuanced analysis of the given text.",
    "gemini15": "Gemini Pro mock response analyzing your prompt with Google's perspective and approach."
}

class MockLLMService:
    """Mock implementation of LLM service that returns predefined responses"""
    
    @staticmethod
    async def get_available_models():
        """Return all models as available in mock mode"""
        return {
            "status": "success",
            "available_models": [
                "gpt4o", "gpto1", "gpto3mini", "gpt4turbo",
                "claude37", "claude3opus", 
                "gemini15", "llama3"
            ],
            "errors": {}
        }
    
    @staticmethod
    async def analyze_prompt(prompt, models, ultra_model, pattern):
        """Return mock analysis data"""
        # Add slight delay to simulate API call
        await asyncio.sleep(1)
        
        results = {}
        for model in models:
            # Random timing between 2-5 seconds
            time_taken = round(random.uniform(2.0, 5.0), 2)
            results[model] = {
                "response": MOCK_RESPONSES.get(model, f"Mock response from {model}"),
                "time_taken": time_taken
            }
        
        # Mock ultra analysis
        ultra_response = f"ULTRA ANALYSIS using {ultra_model} as the base model:\n\nThis is a synthesized view of all model responses for your prompt: '{prompt[:50]}...'"
        
        # Add more realistic delay for Ultra processing
        await asyncio.sleep(2)
        
        return {
            "results": results,
            "ultra_response": ultra_response,
            "pattern": pattern
        }
EOF
        echo "Created mock_llm_service.py"
    else
        echo "mock_llm_service.py exists."
    fi
else
    echo "Starting server in NORMAL mode..."
fi

# Start the server
cd backend && python main.py --port $PORT $MOCK_FLAG

echo "Server stopped." 