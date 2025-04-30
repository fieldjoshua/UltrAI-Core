#!/bin/bash
# This script moves documentation files from ACTION root directories to their supporting_docs directories

# Set the base directory for actions
ACTIONS_DIR=".aicheck/actions"

# Find all markdown files (excluding PLAN.md files) in action directories that are not in supporting_docs
FILES_TO_MOVE=$(find $ACTIONS_DIR -maxdepth 2 -name "*.md" -not -path "*/supporting_docs/*" | grep -v "PLAN.md")

# Process each file
for file in $FILES_TO_MOVE; do
    # Get the directory containing the file
    dir=$(dirname "$file")

    # Get the filename
    filename=$(basename "$file")

    # Create supporting_docs directory if it doesn't exist
    mkdir -p "$dir/supporting_docs"

    # Move the file to supporting_docs
    echo "Moving $file to $dir/supporting_docs/$filename"
    mv "$file" "$dir/supporting_docs/$filename"
done

echo "Documentation migration complete. $(echo "$FILES_TO_MOVE" | wc -l | tr -d ' ') files processed."
