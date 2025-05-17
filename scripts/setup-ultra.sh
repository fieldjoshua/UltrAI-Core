#!/bin/bash
# Ultra Quick Setup Script
# This script sets up Ultra for development with mock LLM providers

# Print colorful messages
print_step() {
  echo -e "\033[1;34m==>\033[0m \033[1m$1\033[0m"
}

print_success() {
  echo -e "\033[1;32m✓\033[0m $1"
}

print_error() {
  echo -e "\033[1;31m✗\033[0m $1"
}

print_info() {
  echo -e "\033[1;33mℹ\033[0m $1"
}

# Check for script dependencies
check_dependencies() {
  print_step "Checking dependencies..."

  local missing=0
  for cmd in python3 pip3 npm node; do
    if ! command -v $cmd &> /dev/null; then
      print_error "$cmd is required but not installed"
      missing=1
    fi
  done

  if [ $missing -eq 1 ]; then
    print_error "Please install missing dependencies and try again"
    exit 1
  fi

  print_success "All dependencies found"
}

# Set up environment variables
setup_env() {
  print_step "Setting up environment..."

  if [ ! -f .env ]; then
    cp env.example .env
    print_success "Created .env file from env.example"

    # Set default values for mock mode
    sed -i.bak 's/USE_MOCK=.*/USE_MOCK=true/' .env
    sed -i.bak 's/AUTO_REGISTER_PROVIDERS=.*/AUTO_REGISTER_PROVIDERS=true/' .env
    rm -f .env.bak

    print_success "Configured environment for mock mode"
  else
    print_info ".env file already exists. Skipping."
  fi
}

# Install backend dependencies
install_backend_deps() {
  print_step "Installing backend dependencies..."

  pip3 install -r requirements.txt
  if [ $? -ne 0 ]; then
    print_error "Failed to install backend dependencies"
    exit 1
  fi

  print_success "Backend dependencies installed"
}

# Install frontend dependencies
install_frontend_deps() {
  print_step "Installing frontend dependencies..."

  cd frontend
  npm install
  if [ $? -ne 0 ]; then
    print_error "Failed to install frontend dependencies"
    exit 1
  fi
  cd ..

  print_success "Frontend dependencies installed"
}

# Start backend in development mode
start_backend() {
  print_step "Starting backend server..."

  cd "$(dirname "$0")"
  cd ..

  # Export needed environment variables
  export USE_MOCK=true
  export AUTO_REGISTER_PROVIDERS=true

  # Start the backend server
  python3 backend/app.py &
  BACKEND_PID=$!

  # Wait for backend to start
  sleep 3

  # Check if backend started successfully
  if kill -0 $BACKEND_PID 2>/dev/null; then
    print_success "Backend server started successfully on http://localhost:8000"
  else
    print_error "Failed to start backend server"
    exit 1
  fi
}

# Start frontend in development mode
start_frontend() {
  print_step "Starting frontend server..."

  cd frontend

  # Start frontend in background
  npm run dev &
  FRONTEND_PID=$!

  # Wait for frontend to start
  sleep 5

  # Check if frontend started successfully
  if kill -0 $FRONTEND_PID 2>/dev/null; then
    print_success "Frontend server started successfully"
    FRONTEND_URL=$(grep -o "http://[^ ]*" <(ps aux | grep "vite" | grep -v grep) | head -1)
    print_info "Frontend available at $FRONTEND_URL"
  else
    print_error "Failed to start frontend server"
    exit 1
  fi

  cd ..
}

# Show final instructions
show_instructions() {
  echo ""
  echo "┌─────────────────────────────────────────────────────────┐"
  echo "│                 ULTRA SETUP COMPLETE!                   │"
  echo "├─────────────────────────────────────────────────────────┤"
  echo "│ 🚀 Ultra is now running with mock LLM providers.        │"
  echo "│                                                         │"
  echo "│ 🔍 Backend API: http://localhost:8000                   │"
  echo "│ 🖥️ Frontend UI: $FRONTEND_URL                     │"
  echo "│                                                         │"
  echo "│ 📝 To use real LLM providers:                           │"
  echo "│   1. Edit .env and add your API keys                    │"
  echo "│   2. Set USE_MOCK=false                                 │"
  echo "│   3. Restart the servers                                │"
  echo "│                                                         │"
  echo "│ 📚 For more information, see:                           │"
  echo "│   documentation/technical/integrations/llm_providers.md │"
  echo "└─────────────────────────────────────────────────────────┘"
  echo ""
  echo "Press Ctrl+C to stop the servers when done"

  # Keep script running to maintain the background processes
  wait $BACKEND_PID $FRONTEND_PID
}

# Main script
main() {
  echo "╔════════════════════════════════════╗"
  echo "║         ULTRA QUICK SETUP          ║"
  echo "╚════════════════════════════════════╝"
  echo ""

  check_dependencies
  setup_env
  install_backend_deps
  install_frontend_deps
  start_backend
  start_frontend
  show_instructions
}

# Run main function
main
