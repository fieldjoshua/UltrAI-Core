#!/bin/bash
# Port clearing utility for Ultra server scripts

clear_port() {
    local PORT=$1

    echo "Checking if port $PORT is in use..."
    if lsof -i :"$PORT" > /dev/null 2>&1; then
        echo "Port $PORT is in use. Killing process..."
        lsof_output=$(lsof -i :"$PORT")
        echo "Process details: "
        echo "$lsof_output"

        # Get PIDs and kill them
        pids=$(lsof -t -i :"$PORT" 2>/dev/null)
        for pid in $pids; do
            echo "Killing process with PID $pid"
            kill -9 "$pid" 2>/dev/null
        done

        # Verify the port is free
        sleep 1
        if ! lsof -i :"$PORT" > /dev/null 2>&1; then
            echo "✅ Successfully freed port $PORT"
        else
            echo "❌ Failed to free port $PORT. You may need to manually kill the process."
            return 1
        fi
    else
        echo "✅ Port $PORT is available"
    fi

    return 0
}

# Allow using this script directly with a port number
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        echo "Usage: $0 PORT_NUMBER"
        exit 1
    fi

    clear_port "$1"
fi
