#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v npm &> /dev/null; then
    echo "Node.js is required but not installed. Please install Node.js and try again."
    exit 1
fi

# Function to handle termination
cleanup() {
    echo "Shutting down services..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal trapping
trap cleanup SIGINT SIGTERM

# Check if backend dependencies are installed
if [ ! -d "venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -r backend/requirements.txt
else
    source venv/bin/activate
fi

# Check if frontend dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start backend server
echo "Starting backend server..."
cd backend
python run.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start up
sleep 2

# Start frontend development server
echo "Starting frontend development server..."
npm run dev &
FRONTEND_PID=$!

echo "Ultra app is running!"
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:8080"
echo "Press Ctrl+C to stop both servers."

# Wait for both processes
wait $FRONTEND_PID $BACKEND_PID 