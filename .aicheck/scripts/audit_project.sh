#!/bin/bash
# Ultra project audit script with performance optimizations

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AUDIT_ENGINE="$PROJECT_ROOT/AuditEngine"

echo -e "${BLUE}Ultra Project Audit - High Performance Edition${NC}"
echo "================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

# Parse command line arguments
VERBOSE=""
WORKERS=""
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -w|--workers)
            WORKERS="--workers $2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="--output $2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [REPOSITORY_PATH]"
            echo "Options:"
            echo "  -v, --verbose        Enable verbose output"
            echo "  -w, --workers NUM    Number of parallel workers"
            echo "  -o, --output DIR     Output directory"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            REPO_PATH="$1"
            shift
            ;;
    esac
done

# Default to project root if no path specified
REPO_PATH="${REPO_PATH:-$PROJECT_ROOT}"

# Check if AuditEngine is available
if [ ! -d "$AUDIT_ENGINE" ]; then
    echo -e "${RED}Error: AuditEngine not found at $AUDIT_ENGINE${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -f "$AUDIT_ENGINE/.deps_installed" ]; then
    echo -e "${YELLOW}Installing AuditEngine dependencies...${NC}"
    cd "$AUDIT_ENGINE"
    pip install -r requirements.txt
    touch .deps_installed
fi

# Run the audit
echo -e "${GREEN}Starting project audit...${NC}"
echo "Repository: $REPO_PATH"
echo

cd "$AUDIT_ENGINE"
python -m AuditEngine "$REPO_PATH" $VERBOSE $WORKERS $OUTPUT_DIR

echo -e "${GREEN}Audit complete!${NC}"
