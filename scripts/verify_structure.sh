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
  "src/business"
  "src/pricing"
  "frontend/components"
  "frontend/pages"
  "frontend/styles"
  "frontend/api"
  "frontend/cloud"
  "backend/api"
  "backend/services"
  "backend/middleware"
  "backend/cloud"
  "backend/db"
  "backend/db/migrations"
  "backend/db/schemas"
  "data/embeddings"
  "data/cache"
  "data/results"
  "src/deployment"
  "src/deployment/docker"
  "src/deployment/kubernetes"
  "src/deployment/ci_cd"
  "src/deployment/environments"
  "tests/performance/benchmarks/models"
  "tests/performance/benchmarks/performance"
  "tests/performance/benchmarks/load_testing"
  "tests/frontend"
  "tests/e2e"
  "tests/unit"
  "src/api/mocks"
  "src/api/mocks/uploads"
  "src/api/public"
  "src/api/public/docs"
  "src/api/public/spec"
  "src/api/public/sdks"
  "src/monitoring"
  "src/data"
  "src/data/cache"
  "src/data/embeddings"
  "src/data/results"
  "scripts"
  "src/examples"
  "src/examples/llm_clients"
  "src/examples/pdf"
  ".aicheck/actions"
  ".aicheck/docs"
  ".aicheck/sessions"
  "documentation/development"
  "documentation/guides"
)

# Array of important README files
readme_files=(
  "README.md"
  "src/README.md"
  "frontend/README.md"
  "backend/README.md"
  "data/README.md"
  "src/deployment/README.md"
  "src/monitoring/README.md"
  "tests/performance/benchmarks/README.md"
  "tests/README.md"
  "src/api/README.md"
  "src/api/mocks/README.md"
  "src/api/public/README.md"
  "frontend/cloud/README.md"
  "backend/cloud/README.md"
  "src/examples/debug.py"
  ".aicheck/docs/README.md"
  ".aicheck/docs/actions_index.md"
  ".aicheck/docs/RULES.md"
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

check_required_directories() {
  local required_dirs=(
    "src"
    "frontend"
    "backend"
    "documentation"
    "frontend/cloud"
    "backend/cloud"
    "tests"
    "tests/performance/benchmarks/models"
    "tests/performance/benchmarks/performance"
    "tests/performance/benchmarks/load_testing"
    "tests/frontend"
    "tests/e2e"
    "tests/unit"
    "src/examples"
    "src/examples/llm_clients"
    "src/examples/pdf"
    "src/api/mocks"
    "src/api/public"
    "src/deployment"
    "src/monitoring"
    "src/data"
    "src/data/cache"
    "src/data/embeddings"
    "src/data/results"
    "src/business"
    "src/pricing"
    "data/results"
    ".aicheck/actions"
    ".aicheck/docs"
    ".aicheck/sessions"
    "documentation/development"
    "documentation/guides"
  )

  for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
      echo "Missing required directory: $dir"
      exit 1
    fi
  done
}

check_required_files() {
  local required_files=(
    ".aicheck/docs/README.md"
    ".aicheck/docs/actions_index.md"
    ".aicheck/docs/RULES.md"
    "tests/performance/benchmarks/README.md"
    "src/examples/debug.py"
  )

  for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
      echo "❌ Missing required file: $file"
      exit 1
    else
      echo "✅ Found required file: $file"
    fi
  done
}
