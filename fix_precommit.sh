#!/bin/bash
# Script to fix common pre-commit hook issues

# Remove trailing whitespace
find . -name "*.md" -type f -exec sed -i '' -e 's/[[:space:]]*$//' {} \;
find . -name "*.sh" -type f -exec sed -i '' -e 's/[[:space:]]*$//' {} \;
find . -name "*.py" -type f -exec sed -i '' -e 's/[[:space:]]*$//' {} \;

# Ensure files end with a newline
find . -name "*.md" -type f -exec sed -i '' -e '$a\' {} \;
find . -name "*.sh" -type f -exec sed -i '' -e '$a\' {} \;
find . -name "*.py" -type f -exec sed -i '' -e '$a\' {} \;

# Run black formatter on Python files
black tests/deployment/test_deployment.py

# Run prettier on markdown files
npx prettier --write ".aicheck/actions/MVPDeploymentPipeline/MVPDeploymentPipeline-COMPLETED.md"
npx prettier --write ".aicheck/docs/actions_index.md"
npx prettier --write "documentation/deployment/release_process.md"
npx prettier --write "documentation/deployment/troubleshooting.md"

echo "Preprocessing completed"
