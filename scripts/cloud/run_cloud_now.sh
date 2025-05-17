#!/bin/bash
# Simple script to run the cloud system with automatic port cleanup

# Kill any processes running on our ports
cleanup_ports() {
  echo "Cleaning up ports..."
  for port in 8000 8080; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
      echo "Killing process $pid on port $port"
      kill -9 $pid 2>/dev/null
    fi
  done
}

# Initial cleanup
cleanup_ports

# Make sure directories exist
if [ ! -d "cloud_backend" ] || [ ! -d "cloud_frontend" ]; then
  echo "Error: cloud_backend or cloud_frontend directory not found."
  exit 1
fi

# Start backend
echo "Starting backend on port 8000..."
cd cloud_backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Check if backend started
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo "ERROR: Backend failed to start."
  exit 1
fi

# Start frontend
echo "Starting frontend on port 8080..."
cd ../cloud_frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "==============================================="
echo "UltraAI Cloud System is running"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: http://localhost:8080"
echo "==============================================="
echo "Press Ctrl+C to stop all servers"

# Trap for clean shutdown
trap 'echo "Shutting down..."; kill $BACKEND_PID $FRONTEND_PID; cleanup_ports; exit 0' INT TERM

# Wait for processes
wait
