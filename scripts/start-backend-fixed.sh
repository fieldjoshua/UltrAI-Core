#!/bin/bash

# Simple script to run the Ultra backend with proper path configuration
echo "Starting UltraAI Backend with proper path configuration..."

# Go to the backend directory
cd backend

# Set PYTHONPATH to include both the current directory and parent
export PYTHONPATH="$(pwd):$(pwd)/.."

# Check if port 8085 is in use
PORT=8085
if lsof -i :$PORT > /dev/null 2>&1; then
    # Port is in use, try an alternative
    PORT=8086
    echo "Port 8085 is in use, trying port $PORT instead"
    if lsof -i :$PORT > /dev/null 2>&1; then
        # Try one more port
        PORT=8087
        echo "Port 8086 is in use, trying port $PORT instead"
    fi
fi

# Check if we should run in mock mode
MOCK_FLAG=""
if [[ "$*" == *"--mock"* ]]; then
    MOCK_FLAG="--mock"
    echo "*** Running in MOCK MODE - using simulated responses ***"
fi

# Try to run the server with python3
python3 start.py $MOCK_FLAG --port $PORT

# If the server exits with an error, show a message
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start the backend server."
    echo "Please check the logs above for details."
    exit 1
fi