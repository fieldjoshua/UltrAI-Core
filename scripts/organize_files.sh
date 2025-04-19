#!/bin/bash

# Script to organize all remaining files into the proper directories
echo "Organizing Ultra Framework files..."

# Create all necessary directories if they don't exist
mkdir -p src/core
mkdir -p config/examples
mkdir -p docs/guides
mkdir -p scripts/debug
mkdir -p scripts/cleanup
mkdir -p tests/examples
mkdir -p tests/data
mkdir -p monitoring/performance
mkdir -p frontend/public
mkdir -p data/logs
mkdir -p examples/pdf
mkdir -p backend/api

# Move core Python files
echo "Moving core Python files..."
mv ultra_*.py src/core/

# Move documentation files
echo "Moving documentation files..."
mv *.md documentation/ 2>/dev/null || true

# Move test files
echo "Moving test files..."
mv jest*.cjs tests/
mv standard*.js tests/
mv standard*.cjs tests/
mv test-body.json tests/data/
mv headers.txt tests/data/

# Move configuration files
echo "Moving configuration files..."
mv *.json config/ 2>/dev/null || true
mv *.toml config/ 2>/dev/null || true
mv *.cfg config/ 2>/dev/null || true
mv *.yaml config/ 2>/dev/null || true

# Skip README.md
mv config/README.md ./ 2>/dev/null || true

# Move build config files
mv config/tsconfig*.json frontend/ 2>/dev/null || true
mv config/jsconfig.json frontend/ 2>/dev/null || true
mv config/postcss.config.cjs frontend/ 2>/dev/null || true
mv config/tailwind.config.cjs frontend/ 2>/dev/null || true
mv config/components.json frontend/ 2>/dev/null || true
mv config/vercel.json frontend/ 2>/dev/null || true
mv config/sentry.config.js frontend/ 2>/dev/null || true

# Move scripts
echo "Moving scripts..."
mv *.sh scripts/ 2>/dev/null || true

# Move frontend files
echo "Moving frontend files..."
mv index.html frontend/public/
mv config/package*.json frontend/ 2>/dev/null || true
mv config/vite.config.ts frontend/ 2>/dev/null || true

# Move API files
echo "Moving API files..."
mv api.js frontend/api/
mv api.py backend/api/

# Move utility Python scripts
echo "Moving utility Python scripts..."
mv debug*.py scripts/debug/
mv cleanup.py scripts/cleanup/
mv search_pypi.py scripts/
mv rename.py scripts/
mv claude_test_new.py tests/

# Move Python package configuration files
echo "Moving Python package files..."
mv config/setup.py backend/ 2>/dev/null || true
mv config/setup.cfg backend/ 2>/dev/null || true
mv config/pyproject.toml backend/ 2>/dev/null || true
mv requirements.txt backend/

# Move sample files
echo "Moving sample files..."
mv *.pdf examples/pdf/ 2>/dev/null || true

# Move data files
echo "Moving data files..."
mv user_accounts.json data/
mv analysis_patterns_prompts.csv data/
mv response.json data/

# Move log files
echo "Moving log files..."
mv *.log data/logs/ 2>/dev/null || true

# Move Docker files to deployment
mkdir -p deployment/docker
mv Dockerfile* deployment/docker/ 2>/dev/null || true
mv docker-compose.yml deployment/docker/ 2>/dev/null || true

echo "File organization complete!"