#\!/bin/bash

# Run the simple analyzer with appropriate environment variables

# Set this to true to use mock responses if no API keys are available
USE_MOCK=${USE_MOCK:-true}

# Get the first argument as the prompt, or use a default if not provided
PROMPT="${1:-What are the main challenges in artificial intelligence research today?}"

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set. Using mock mode."
    USE_MOCK=true
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY is not set. Using mock mode."
    USE_MOCK=true
fi

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Warning: GOOGLE_API_KEY is not set. Using mock mode."
    USE_MOCK=true
fi

# Run the analyzer
if [ "$USE_MOCK" = true ]; then
    echo "Running in mock mode..."
    python3 simple_analyzer.py --prompt "$PROMPT" --mock
else
    echo "Running with real API keys..."
    python3 simple_analyzer.py --prompt "$PROMPT"
fi
EOL < /dev/null