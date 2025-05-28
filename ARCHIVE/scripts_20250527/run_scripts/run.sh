#!/bin/bash
# Ultra MVP Run Script
# This script starts both the backend and frontend servers

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Print header
echo -e "\n${BOLD}====== Ultra MVP ======${RESET}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found.${RESET}"
    echo "Please run ./scripts/setup.sh first."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${BOLD}Activating virtual environment...${RESET}"
    source .venv/bin/activate
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
BACKEND_PORT=$(grep "PORT" .env | cut -d= -f2 || echo 8000)
if check_port $BACKEND_PORT; then
    echo -e "${RED}Error: Port $BACKEND_PORT is already in use.${RESET}"
    echo "Please stop the service using that port or change the PORT in .env"
    exit 1
fi

if check_port 3000; then
    echo -e "${RED}Error: Port 3000 is already in use.${RESET}"
    echo "Please stop the service using port 3000 (required for frontend)"
    exit 1
fi

# Store PIDs
BACKEND_PID=""
FRONTEND_PID=""

# Function to clean up on exit
cleanup() {
    echo -e "\n${BOLD}Shutting down servers...${RESET}"
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend server (PID: $BACKEND_PID)"
        kill -9 $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend server (PID: $FRONTEND_PID)"
        kill -9 $FRONTEND_PID 2>/dev/null
    fi
    echo -e "${GREEN}Shutdown complete. Goodbye!${RESET}"
    exit 0
}

# Set up the trap for SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Start backend server
echo -e "${BOLD}Starting backend server...${RESET}"
if [ -f "src/main.py" ]; then
    python src/main.py &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend server started on port $BACKEND_PORT (PID: $BACKEND_PID)${RESET}"
else
    echo -e "${YELLOW}Warning: src/main.py not found.${RESET}"
    echo "Falling back to uvicorn with fastapi app..."
    if [ -f "src/app.py" ]; then
        uvicorn src.app:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
        BACKEND_PID=$!
        echo -e "${GREEN}Backend server started on port $BACKEND_PORT (PID: $BACKEND_PID)${RESET}"
    else
        echo -e "${RED}Error: No backend entry point found.${RESET}"
        echo "Please create either src/main.py or src/app.py"
        exit 1
    fi
fi

# Wait a moment for backend to start
sleep 2

# Start frontend server
if [ -d "frontend" ]; then
    echo -e "\n${BOLD}Starting frontend development server...${RESET}"
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    echo -e "${GREEN}Frontend server started on port 3000 (PID: $FRONTEND_PID)${RESET}"
else
    echo -e "\n${YELLOW}Warning: frontend directory not found.${RESET}"
    echo "Frontend server will not be started."
fi

# Display URLs
echo -e "\n${BOLD}Ultra MVP is running!${RESET}"
echo -e "Backend API: ${GREEN}http://localhost:$BACKEND_PORT/api${RESET}"
if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "Frontend UI: ${GREEN}http://localhost:3000${RESET}"
fi
echo -e "\nPress ${BOLD}Ctrl+C${RESET} to stop both servers.\n"

# Wait for user to stop with Ctrl+C
wait
