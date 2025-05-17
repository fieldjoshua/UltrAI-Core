#!/bin/bash
# Script to cleanly restart the UltraAI cloud services

# Kill any existing processes
echo "Killing any existing processes..."
pkill -f "python -m uvicorn" || true
pkill -f "python3 -m http.server" || true
sleep 1

# Start the backend
echo "Starting backend on port 8000..."
cd cloud_backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo "ERROR: Backend failed to start."
  exit 1
fi

# Test backend
echo "Testing backend..."
curl -s http://localhost:8000/api/health
echo ""

# Start the frontend
echo "Starting frontend on port 8080..."
cd ../cloud_frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "UltraAI Cloud System is running!"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle interruptions
trap "echo 'Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for child processes
wait
