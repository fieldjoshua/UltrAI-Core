#!/bin/bash
# Code location check script
# Ensures that code files are properly placed in action directories

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Security functions
validate_path() {
    local path="$1"
    if [[ "$path" != .aicheck/* && "$path" != ./* ]]; then
        echo -e "${RED}Error: Invalid path access attempt${NC}"
        exit 1
    fi
}

# Check code files to ensure they're in the right location
check_code_location() {
    # Get files being committed
    local files=$(git diff --cached --name-only)
    local warnings=0
    
    # Define code file extensions to check
    local code_extensions=("py" "js" "ts" "go" "rb" "php" "java" "cpp" "c" "h" "cs" "sh" "pl" "swift" "kt" "rs")
    
    for file in $files; do
        # Skip files in .aicheck/scripts and root scripts
        if [[ "$file" == ".aicheck/scripts/"* || "$file" == *.sh && $(dirname "$file") == "." ]]; then
            continue
        fi
        
        # Check if this is a code file based on extension
        local ext="${file##*.}"
        for code_ext in "${code_extensions[@]}"; do
            if [[ "$ext" == "$code_ext" ]]; then
                # This is a code file - check if it's in an action directory
                if [[ "$file" != ".aicheck/actions/"*"/code/"* && "$file" != ".aicheck/actions/"*"/src/"* ]]; then
                    echo -e "${YELLOW}WARNING: Code file $file may be misplaced${NC}"
                    echo -e "${YELLOW}According to best practices, code files should be in:${NC}"
                    echo -e "${YELLOW}- .aicheck/actions/<ActionName>/code/ or${NC}"
                    echo -e "${YELLOW}- .aicheck/actions/<ActionName>/src/${NC}"
                    warnings=$((warnings+1))
                fi
                break
            fi
        done
    done
    
    if [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}Found $warnings potentially misplaced code files.${NC}"
        echo -e "${YELLOW}Use ./ai create-code to ensure proper code placement.${NC}"
        echo -e "${YELLOW}Continue with commit? (y/n)${NC}"
        read -r response
        if [[ "$response" != "y" ]]; then
            echo "Commit aborted. Please fix code file locations."
            exit 1
        fi
    fi
    
    return 0
}

# Run the check
check_code_location 