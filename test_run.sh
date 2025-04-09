#!/bin/bash

# Script to run both the test frontend and backend

# Kill any existing processes on port 8085
kill_port_process() {
  local port=$1
  local pid=$(lsof -ti:$port)
  if [ ! -z "$pid" ]; then
    echo "Killing process $pid on port $port"
    kill -9 $pid 2>/dev/null
  fi
}

# Kill any existing server on port 8085
kill_port_process 8085

# Get project root directory
ROOT_DIR=$(pwd)
echo "Working directory: $ROOT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
  echo "Python3 not found. Using 'python' command instead."
  PYTHON_CMD="python"
else
  PYTHON_CMD="python3"
fi

# Check if required packages are installed
$PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Installing required packages..."
  $PYTHON_CMD -m pip install fastapi uvicorn
fi

# Start the test backend server
echo "Starting test backend server on port 8085..."
$PYTHON_CMD test_backend.py &
BACKEND_PID=$!

# Wait a second for the server to start
sleep 1

# Check if the server is running
if ! lsof -i:8085 > /dev/null; then
  echo "Failed to start backend server. Please check test_backend.py for errors."
  exit 1
fi

# Serve the test frontend using Python's HTTP server
echo "Starting frontend server on port 3000..."
cd "$ROOT_DIR/test_frontend"
if [ "$(uname)" == "Darwin" ]; then  # macOS
  open http://localhost:3000
else  # Linux or other
  xdg-open http://localhost:3000 &>/dev/null || echo "Please open http://localhost:3000 in your browser"
fi
python -m http.server 3000

# When Python server stops, kill the backend
kill $BACKEND_PID 2>/dev/null