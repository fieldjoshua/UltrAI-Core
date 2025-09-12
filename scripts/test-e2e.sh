#!/bin/bash
#
# E2E Test Runner Script for UltrAI
# This script starts the necessary services and runs end-to-end tests
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3009
BACKEND_PORT=8000
FRONTEND_LOG="/tmp/ultra-frontend-test.log"
BACKEND_LOG="/tmp/ultra-backend-test.log"
TEST_LOG="/tmp/ultra-test-results.log"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[STATUS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=0
    
    print_status "Waiting for $url to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_status "$url is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 2
    done
    
    print_error "$url did not become ready in time"
    return 1
}

# Function to cleanup background processes
cleanup() {
    print_status "Cleaning up..."
    
    # Kill frontend if running
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill backend if running
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill any orphaned processes
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "python app.py" 2>/dev/null || true
    
    print_status "Cleanup complete"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Main script
print_status "Starting UltrAI E2E Test Runner"

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
    print_warning "API keys not found in environment, loading from .env file..."
    if [ -f ".env" ]; then
        export $(grep -E "(OPENAI|ANTHROPIC|GOOGLE)_API_KEY" .env | xargs)
    else
        print_error ".env file not found. Please set OPENAI_API_KEY and ANTHROPIC_API_KEY"
        exit 1
    fi
fi

# Check if ports are already in use
if check_port $FRONTEND_PORT; then
    print_error "Frontend port $FRONTEND_PORT is already in use"
    print_status "You can kill it with: lsof -ti :$FRONTEND_PORT | xargs kill -9"
    exit 1
fi

if check_port $BACKEND_PORT; then
    print_error "Backend port $BACKEND_PORT is already in use"
    print_status "You can kill it with: lsof -ti :$BACKEND_PORT | xargs kill -9"
    exit 1
fi

# Configure frontend for local testing if needed
if [ "$1" != "--skip-setup" ]; then
    print_status "Configuring frontend for local backend..."
    ./scripts/setup-local-test.sh
fi

# Start backend
print_status "Starting backend server on port $BACKEND_PORT..."
cd "$(dirname "$0")/.."  # Go to project root

# Activate virtual environment and start backend
source venv/bin/activate
python app_production.py > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
print_status "Backend started with PID $BACKEND_PID (log: $BACKEND_LOG)"

# Start frontend
print_status "Starting frontend server on port $FRONTEND_PORT..."
cd frontend
npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
cd ..
print_status "Frontend started with PID $FRONTEND_PID (log: $FRONTEND_LOG)"

# Wait for services to be ready
wait_for_service "http://localhost:$BACKEND_PORT/health" || {
    print_error "Backend failed to start. Check logs at $BACKEND_LOG"
    tail -20 "$BACKEND_LOG"
    exit 1
}

wait_for_service "http://localhost:$FRONTEND_PORT" || {
    print_error "Frontend failed to start. Check logs at $FRONTEND_LOG"
    tail -20 "$FRONTEND_LOG"
    exit 1
}

print_status "All services are ready!"

# Run the tests
print_status "Running E2E tests..."

export TEST_MODE=live
export WEB_APP_URL="http://localhost:$FRONTEND_PORT"

# Run browser tests
if [ "$1" == "--headed" ]; then
    print_status "Running tests in headed mode (browser visible)..."
    ./venv/bin/pytest tests/live/test_live_online_ui.py -v --headed | tee "$TEST_LOG"
else
    ./venv/bin/pytest tests/live/test_live_online_ui.py -v | tee "$TEST_LOG"
fi

TEST_EXIT_CODE=${PIPESTATUS[0]}

# Run other live tests
print_status "Running additional live provider tests..."
./venv/bin/pytest tests/live/test_live_providers.py -v

# Print summary
echo ""
print_status "Test run complete!"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "✅ All tests passed!"
else
    print_error "❌ Some tests failed. Check the logs:"
    echo "  - Test results: $TEST_LOG"
    echo "  - Backend log: $BACKEND_LOG"
    echo "  - Frontend log: $FRONTEND_LOG"
fi

echo ""
print_status "Services are still running. Press Ctrl+C to stop them."
print_status "Or run in another terminal:"
echo "  - Frontend: http://localhost:$FRONTEND_PORT"
echo "  - Backend: http://localhost:$BACKEND_PORT"
echo "  - Backend API docs: http://localhost:$BACKEND_PORT/docs"

# Keep script running to maintain services
wait