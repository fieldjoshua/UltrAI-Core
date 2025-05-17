#!/bin/bash
# Auto Port Manager for Cloud System
# This script manages ports by automatically killing processes when specified conditions occur

# Configuration
MONITORED_PORTS=(8000 8001 8080 8085)
MAX_ERROR_COUNT=3
CHECK_INTERVAL=2  # in seconds
LOG_FILE="port_manager.log"

# Initialize counters
declare -A error_counts
for port in "${MONITORED_PORTS[@]}"; do
    error_counts[$port]=0
done

# Function to log messages
log_message() {
    local message="$(date '+%Y-%m-%d %H:%M:%S') - $1"
    echo "$message" | tee -a "$LOG_FILE"
}

# Function to check if a port is available
is_port_available() {
    local port=$1
    nc -z localhost "$port" 2>/dev/null
    if [ $? -eq 0 ]; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to kill process on a port
kill_process_on_port() {
    local port=$1
    local pid=$(lsof -t -i:"$port" 2>/dev/null)

    if [ -n "$pid" ]; then
        log_message "Killing process $pid on port $port"
        kill -9 "$pid" 2>/dev/null

        # Verify the process was killed
        sleep 1
        if is_port_available "$port"; then
            log_message "Successfully freed port $port"
            error_counts[$port]=0
            return 0
        else
            log_message "Failed to free port $port"
            return 1
        fi
    else
        log_message "No process found on port $port"
        return 1
    fi
}

# Function to check port response
check_port_response() {
    local port=$1
    curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/api/health" 2>/dev/null
}

# Function to handle port errors
handle_port_error() {
    local port=$1
    local error_type=$2

    error_counts[$port]=$((error_counts[$port] + 1))

    log_message "Port $port error ($error_type) - Count: ${error_counts[$port]}/$MAX_ERROR_COUNT"

    if [ ${error_counts[$port]} -ge $MAX_ERROR_COUNT ]; then
        log_message "Maximum error count reached for port $port. Auto-killing process."
        kill_process_on_port "$port"
    fi
}

# Print startup message
log_message "Starting Port Manager for ports: ${MONITORED_PORTS[*]}"
log_message "Press Ctrl+C to stop monitoring"

# Main monitoring loop
while true; do
    for port in "${MONITORED_PORTS[@]}"; do
        # Check if the port is in use
        if ! is_port_available "$port"; then
            # Port is in use, check if it's responding properly
            local response=$(check_port_response "$port")

            if [ "$response" != "200" ]; then
                handle_port_error "$port" "Bad response: $response"
            else
                # Reset error count on successful response
                error_counts[$port]=0
            fi
        fi
    done

    # Wait before checking again
    sleep "$CHECK_INTERVAL"
done
