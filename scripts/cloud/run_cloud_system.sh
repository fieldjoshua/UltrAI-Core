#!/bin/bash
# Run both backend and frontend for the UltraAI cloud system

WORKSPACE_DIR="$(pwd)"
BACKEND_DIR="${WORKSPACE_DIR}/cloud_backend"
FRONTEND_DIR="${WORKSPACE_DIR}/cloud_frontend"

echo "Working directory: ${WORKSPACE_DIR}"

# Create a function to kill all child processes when the script exits
function cleanup {
    echo "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
}

# Register the cleanup function to run on exit
trap cleanup EXIT

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo "Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Error: Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

# Start the backend server
echo "Starting backend server on port 8000..."
cd "$BACKEND_DIR"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 2

# Start the frontend server
echo "Starting frontend server on port 8080..."
cd "$FRONTEND_DIR"
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "UltraAI Cloud System is running!"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:8080"
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID