#!/bin/bash

# Script to start the Ultra App (both frontend and backend)
echo "Starting UltraAI Application..."

# Check if we should run in mock mode
MOCK_FLAG=""
if [[ "$*" == *"--mock"* ]]; then
    MOCK_FLAG="--mock"
    echo "*** Running in MOCK MODE - using simulated responses ***"
fi

# Start the backend in the background
echo "Starting backend..."
chmod +x start-backend-fixed.sh
./start-backend-fixed.sh $MOCK_FLAG &
BACKEND_PID=$!

# Wait a second for the backend to initialize
sleep 1

# Start the frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Function to handle signals and clean up processes
cleanup() {
    echo "Shutting down..."
    kill $FRONTEND_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handling
trap cleanup INT TERM

echo ""
echo "🚀 UltraAI is running!"
echo "- Frontend: http://localhost:3009"
echo "- Backend API: http://localhost:8085"
echo "- API Docs: http://localhost:8085/api/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for signals
wait
