#!/bin/bash

# Verify Ultra Framework Project Structure
# This script checks if all required directories and files are present

echo "Verifying Ultra Framework Directory Structure"
echo "============================================="

# Array of required directories
required_dirs=(
  "src/models"
  "src/patterns"
  "src/document_processing"
  "src/utils"
  "src/config"
  "frontend/components"
  "frontend/pages"
  "frontend/styles"
  "frontend/api"
  "backend/api"
  "backend/services"
  "backend/middleware"
  "backend/db"
  "backend/db/migrations"
  "backend/db/schemas"
  "data/embeddings"
  "data/cache"
  "data/results"
  "deployment/docker"
  "deployment/kubernetes"
  "deployment/ci_cd"
  "deployment/environments"
  "benchmarks/models"
  "benchmarks/performance"
  "benchmarks/load_testing"
  "public_api/docs"
  "public_api/spec"
  "public_api/sdks"
  "examples"
  "scripts"
  "monitoring"
  "docs/development"
  "tests"
)

# Array of important README files
readme_files=(
  "README.md"
  "src/README.md"
  "frontend/README.md"
  "backend/README.md"
  "data/README.md"
  "deployment/README.md"
  "benchmarks/README.md"
  "public_api/README.md"
  "examples/README.md"
  "scripts/README.md"
  "monitoring/README.md"
  "docs/README.md"
  "docs/development/README.md"
  "tests/README.md"
)

# Check if directories exist
echo "Checking directories..."
missing_dirs=0
for dir in "${required_dirs[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "❌ Missing directory: $dir"
    missing_dirs=$((missing_dirs+1))
  else
    echo "✅ Found directory: $dir"
  fi
done

# Check if README files exist
echo -e "\nChecking README files..."
missing_readmes=0
for file in "${readme_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "❌ Missing README: $file"
    missing_readmes=$((missing_readmes+1))
  else
    echo "✅ Found README: $file"
  fi
done

# Report summary
echo -e "\nSummary:"
echo "---------------------"
echo "Total directories checked: ${#required_dirs[@]}"
echo "Missing directories: $missing_dirs"
echo "Total README files checked: ${#readme_files[@]}"
echo "Missing README files: $missing_readmes"

if [ $missing_dirs -eq 0 ] && [ $missing_readmes -eq 0 ]; then
  echo -e "\n✅ Project structure is complete!"
  exit 0
else
  echo -e "\n❌ Project structure has issues. Please fix the missing items."
  exit 1
fi