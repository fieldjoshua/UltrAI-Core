#!/bin/bash

# watch_and_update.sh
# Script to watch for changes in the actions directory and automatically update the index

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTIONS_DIR="$SCRIPT_DIR"
INDEX_GENERATOR="$SCRIPT_DIR/update_index.py"

# Make the Python script executable
chmod +x "$INDEX_GENERATOR"

# First, generate the index initially
echo "Generating initial index..."
python3 "$INDEX_GENERATOR"

# Function to update index when files change
update_index() {
    echo "Detected changes. Updating index..."
    python3 "$INDEX_GENERATOR"
    echo "Index updated at $(date)"
}

# Check if fswatch is available (macOS)
if command -v fswatch >/dev/null 2>&1; then
    echo "Starting file watcher using fswatch..."
    fswatch -o "$ACTIONS_DIR" | while read f; do
        if [[ "$f" == *".md" || "$f" == *"PLAN"* || "$f" == *"COMPLETED"* || "$f" == *"supporting_docs"* ]]; then
            update_index
        fi
    done
# Check if inotifywait is available (Linux)
elif command -v inotifywait >/dev/null 2>&1; then
    echo "Starting file watcher using inotify..."
    while true; do
        inotifywait -r -e modify,create,delete "$ACTIONS_DIR"
        update_index
    done
else
    # Fall back to polling method
    echo "fswatch and inotifywait not found. Using polling method..."

    # Function to get a hash of all relevant files
    get_files_hash() {
        find "$ACTIONS_DIR" -type f -name "*.md" -o -name "*PLAN*" -o -name "*COMPLETED*" | xargs cat 2>/dev/null | md5sum
    }

    LAST_HASH=$(get_files_hash)

    while true; do
        sleep 10
        CURRENT_HASH=$(get_files_hash)

        if [ "$LAST_HASH" != "$CURRENT_HASH" ]; then
            update_index
            LAST_HASH=$CURRENT_HASH
        fi
    done
fi
