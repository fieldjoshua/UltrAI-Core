#!/bin/bash

# Cleanup Script for Orchestration Rebuild
# This script removes unnecessary test files and complex orchestration code

echo "Starting cleanup for orchestration rebuild..."

# Create backup directory
BACKUP_DIR="/Users/joshuafield/Documents/Ultra/.aicheck/actions/clean-rebuild-orchestration/removed_files_backup"
mkdir -p "$BACKUP_DIR"

# Function to safely remove files (move to backup instead of delete)
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup_path="$BACKUP_DIR/$(basename "$file")"
        mv "$file" "$backup_path"
        echo "Removed: $file (backed up)"
    fi
}

# Remove test files from root directory
echo "Removing test files from root..."
safe_remove "/Users/joshuafield/Documents/Ultra/test_deployment_progress.py"
safe_remove "/Users/joshuafield/Documents/Ultra/test_deployment.py"
safe_remove "/Users/joshuafield/Documents/Ultra/test_orchestration_minimal.py"

# Remove test files from tests directory
echo "Removing test files from tests directory..."
safe_remove "/Users/joshuafield/Documents/Ultra/tests/test_claude_debug.py"
safe_remove "/Users/joshuafield/Documents/Ultra/tests/test_claude.py"
safe_remove "/Users/joshuafield/Documents/Ultra/tests/test_document_upload.py"

# Remove complex orchestration files
echo "Removing complex orchestration files..."
safe_remove "/Users/joshuafield/Documents/Ultra/backend/backend/integrations/pattern_orchestrator_integration_fixed.py"
safe_remove "/Users/joshuafield/Documents/Ultra/backend/integrations/pattern_orchestrator.py"

# Remove entire patterns directory
echo "Removing patterns directory..."
if [ -d "/Users/joshuafield/Documents/Ultra/src/patterns" ]; then
    mv "/Users/joshuafield/Documents/Ultra/src/patterns" "$BACKUP_DIR/patterns_backup"
    echo "Removed: patterns directory (backed up)"
fi

# Remove ultra_* files from src/core that are overly complex
echo "Removing complex ultra_* files..."
safe_remove "/Users/joshuafield/Documents/Ultra/src/core/ultra_pattern_orchestrator.py"
safe_remove "/Users/joshuafield/Documents/Ultra/src/core/ultra_analysis_patterns.py"

# Remove resilient files
echo "Removing resilient client files..."
safe_remove "/Users/joshuafield/Documents/Ultra/backend/services/resilient_client.py"
safe_remove "/Users/joshuafield/Documents/Ultra/scripts/test_resilient_api.py"

echo "Cleanup complete! All files have been backed up to: $BACKUP_DIR"
echo ""
echo "Summary of removed items:"
echo "- Test files from root directory"
echo "- Test files from tests directory"
echo "- Complex pattern orchestrator files"
echo "- Patterns directory"
echo "- Resilient client implementations"