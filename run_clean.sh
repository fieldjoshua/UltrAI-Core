#!/bin/bash
# Clean launcher for Ultra CLI

# Current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source env if it exists
if [ -f "$DIR/.env" ]; then
  # Source quietly
  set -a
  source "$DIR/.env" >/dev/null 2>&1
  set +a
fi

# Run the clean Python interface
python3 "$DIR/ultra_clean.py" "$@"
