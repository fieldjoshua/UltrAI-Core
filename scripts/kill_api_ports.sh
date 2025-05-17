#!/bin/bash
# Script to kill processes on common API ports
# Usage: ./kill_api_ports.sh [port]

# Default port
DEFAULT_PORT=8085

# Get port from argument or use default
PORT=${1:-$DEFAULT_PORT}

# Function to kill process on port
kill_process_on_port() {
    local port=$1
    local pids=$(lsof -t -i:"$port" 2>/dev/null)

    if [ -n "$pids" ]; then
        echo "Found processes using port $port: $pids"
        echo "Killing processes..."
        for pid in $pids; do
            kill -9 "$pid" 2>/dev/null
            echo "Killed process $pid"
        done

        # Verify the port is free
        sleep 1
        if ! lsof -i:"$port" > /dev/null 2>&1; then
            echo "✅ Successfully freed port $port"
            return 0
        else
            echo "❌ Failed to free port $port"
            return 1
        fi
    else
        echo "ℹ️ No processes found on port $port"
        return 0
    fi
}

# Kill process on the specified port
kill_process_on_port "$PORT"

echo "Done. You can now start your server on port $PORT."
