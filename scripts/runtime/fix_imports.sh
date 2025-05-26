#!/bin/bash

# Script to fix imports in the Ultra backend codebase
# This adds "backend." prefix to internal module imports

echo "Fixing imports in backend directory..."

# Find all Python files in the backend directory
BACKEND_FILES=$(find backend -name "*.py")

# Patterns to search for and replace
MODULES=("config" "models" "services" "utils" "decorators" "database" "middleware" "routes")

# Process each file
for file in $BACKEND_FILES; do
    echo "Processing file: $file"

    # For each module, replace the import statements
    for module in "${MODULES[@]}"; do
        # Fix 'from module import' to 'from backend.module import'
        sed -i '' -E "s/from $module import/from backend.$module import/g" "$file"

        # Fix 'import module' to 'import backend.module as module'
        sed -i '' -E "s/import $module$/import backend.$module as $module/g" "$file"
    done
done

echo "Import fixing complete!"
