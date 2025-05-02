#!/bin/bash
# Script to fix Base imports in all model files

cd "$(dirname "$0")"
MODELS_DIR="models"

# Loop through all Python files in the models directory
for model_file in "$MODELS_DIR"/*.py; do
    # Skip the base.py file
    if [[ "$model_file" == "$MODELS_DIR/base.py" || "$model_file" == "$MODELS_DIR/__init__.py" ]]; then
        continue
    fi
    
    echo "Fixing imports in $model_file"
    
    # Replace the import statement
    sed -i '' 's/from backend.database.connection import Base/from backend.database.models.base import Base/g' "$model_file"
done

echo "All model files updated"