#!/bin/bash
# Enhanced startup script for UltraAI Cloud System with port management

WORKSPACE_DIR="$(pwd)"
BACKEND_DIR="${WORKSPACE_DIR}/cloud_backend"
FRONTEND_DIR="${WORKSPACE_DIR}/cloud_frontend"
LOG_DIR="${WORKSPACE_DIR}/logs"
BACKEND_PORT=8000
FRONTEND_PORT=8080
MAX_RETRIES=3

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    local message="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$message"
    echo "$message" >> "${LOG_DIR}/cloud_system.log"
}

# Function to check if a port is available
is_port_available() {
    local port=$1
    lsof -i:$port >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to kill process on a port
kill_process_on_port() {
    local port=$1
    local force=$2

    log_message "Attempting to free port $port..."

    # Get process IDs using the port
    local pids=$(lsof -t -i:$port 2>/dev/null)

    if [ -n "$pids" ]; then
        for pid in $pids; do
            local process_name=$(ps -p $pid -o comm= 2>/dev/null)

            if [ "$force" = "force" ]; then
                log_message "Force killing process $pid ($process_name) on port $port"
                kill -9 $pid 2>/dev/null
            else
                log_message "Gracefully stopping process $pid ($process_name) on port $port"
                kill $pid 2>/dev/null

                # Wait up to 5 seconds for the process to terminate
                local count=0
                while kill -0 $pid 2>/dev/null && [ $count -lt 5 ]; do
                    sleep 1
                    count=$((count + 1))
                done

                # If process still exists after waiting, force kill it
                if kill -0 $pid 2>/dev/null; then
                    log_message "Process $pid didn't terminate gracefully, force killing"
                    kill -9 $pid 2>/dev/null
                fi
            fi
        done

        # Verify the port is now available
        sleep 1
        if is_port_available $port; then
            log_message "Successfully freed port $port"
            return 0
        else
            log_message "Failed to free port $port even after killing processes"
            if [ "$force" != "force" ]; then
                kill_process_on_port $port "force"
            fi
            return 1
        fi
    else
        log_message "No process found using port $port"
        return 0
    fi
}

# Function to ensure a port is available
ensure_port_available() {
    local port=$1

    if ! is_port_available $port; then
        log_message "Port $port is in use. Attempting to free it."
        kill_process_on_port $port

        if ! is_port_available $port; then
            log_message "ERROR: Could not free port $port. Please check manually."
            return 1
        fi
    fi

    return 0
}

# Function to start the backend
start_backend() {
    log_message "Starting backend server on port $BACKEND_PORT..."

    # Check if the backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        log_message "ERROR: Backend directory not found at $BACKEND_DIR"
        return 1
    fi

    # Ensure backend port is available
    ensure_port_available $BACKEND_PORT || return 1

    # Navigate to backend directory
    cd "$BACKEND_DIR"

    # Start the backend in the background
    nohup python -m uvicorn main:app --host 127.0.0.1 --port $BACKEND_PORT > "${LOG_DIR}/backend.log" 2>&1 &
    BACKEND_PID=$!

    # Check if the backend started correctly
    sleep 2
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        log_message "ERROR: Backend failed to start. Check ${LOG_DIR}/backend.log for details."
        return 1
    fi

    log_message "Backend server started with PID $BACKEND_PID"
    echo $BACKEND_PID > "${LOG_DIR}/backend.pid"

    # Verify the backend is responding
    local retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/health 2>/dev/null)

        if [ "$status_code" = "200" ]; then
            log_message "Backend is up and responding (HTTP $status_code)"
            return 0
        else
            log_message "Backend not responding correctly yet (HTTP $status_code). Retrying..."
            sleep 2
            retry_count=$((retry_count + 1))
        fi
    done

    log_message "ERROR: Backend is not responding after $MAX_RETRIES attempts."
    kill_process_on_port $BACKEND_PORT
    return 1
}

# Function to start the frontend
start_frontend() {
    log_message "Starting frontend server on port $FRONTEND_PORT..."

    # Check if the frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_message "ERROR: Frontend directory not found at $FRONTEND_DIR"
        return 1
    fi

    # Ensure frontend port is available
    ensure_port_available $FRONTEND_PORT || return 1

    # Navigate to frontend directory
    cd "$FRONTEND_DIR"

    # Start the frontend in the background
    nohup python3 -m http.server $FRONTEND_PORT > "${LOG_DIR}/frontend.log" 2>&1 &
    FRONTEND_PID=$!

    # Check if the frontend started correctly
    sleep 2
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        log_message "ERROR: Frontend failed to start. Check ${LOG_DIR}/frontend.log for details."
        return 1
    fi

    log_message "Frontend server started with PID $FRONTEND_PID"
    echo $FRONTEND_PID > "${LOG_DIR}/frontend.pid"

    # Verify the frontend is responding
    local retry_count=0
    while [ $retry_count -lt $MAX_RETRIES ]; do
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT 2>/dev/null)

        if [ "$status_code" = "200" ]; then
            log_message "Frontend is up and responding (HTTP $status_code)"
            return 0
        else
            log_message "Frontend not responding correctly yet (HTTP $status_code). Retrying..."
            sleep 2
            retry_count=$((retry_count + 1))
        fi
    done

    log_message "ERROR: Frontend is not responding after $MAX_RETRIES attempts."
    kill_process_on_port $FRONTEND_PORT
    return 1
}

# Function to stop the cloud system
stop_cloud_system() {
    log_message "Stopping UltraAI Cloud System..."

    # Stop backend
    if [ -f "${LOG_DIR}/backend.pid" ]; then
        local backend_pid=$(cat "${LOG_DIR}/backend.pid")
        if kill -0 $backend_pid 2>/dev/null; then
            log_message "Stopping backend (PID $backend_pid)"
            kill $backend_pid 2>/dev/null
        else
            log_message "Backend process (PID $backend_pid) is not running"
        fi
        rm "${LOG_DIR}/backend.pid"
    fi

    # Stop frontend
    if [ -f "${LOG_DIR}/frontend.pid" ]; then
        local frontend_pid=$(cat "${LOG_DIR}/frontend.pid")
        if kill -0 $frontend_pid 2>/dev/null; then
            log_message "Stopping frontend (PID $frontend_pid)"
            kill $frontend_pid 2>/dev/null
        else
            log_message "Frontend process (PID $frontend_pid) is not running"
        fi
        rm "${LOG_DIR}/frontend.pid"
    fi

    # Make sure all ports are freed
    ensure_port_available $BACKEND_PORT
    ensure_port_available $FRONTEND_PORT

    log_message "UltraAI Cloud System stopped"
}

# Handle script termination
trap stop_cloud_system EXIT

# Main function to start the cloud system
start_cloud_system() {
    log_message "Starting UltraAI Cloud System..."

    # Install required dependencies if needed
    if ! command -v curl &>/dev/null; then
        log_message "curl is required but not installed. Please install it first."
        exit 1
    fi

    if ! command -v lsof &>/dev/null; then
        log_message "lsof is required but not installed. Please install it first."
        exit 1
    fi

    # Start backend
    if ! start_backend; then
        log_message "Failed to start backend. Aborting."
        exit 1
    fi

    # Start frontend
    if ! start_frontend; then
        log_message "Failed to start frontend. Stopping backend and aborting."
        stop_cloud_system
        exit 1
    fi

    log_message "UltraAI Cloud System is now running"
    log_message "- Backend: http://localhost:$BACKEND_PORT"
    log_message "- Frontend: http://localhost:$FRONTEND_PORT"
    log_message "Press Ctrl+C to stop all servers"

    # Keep the script running until user interrupts
    while true; do
        sleep 1
    done
}

# Start the cloud system
start_cloud_system
