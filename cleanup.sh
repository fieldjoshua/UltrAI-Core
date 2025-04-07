#!/bin/bash

# Create archive structure if it doesn't exist
mkdir -p archive/tests
mkdir -p archive/backups
mkdir -p archive/deprecated
mkdir -p archive/logs
mkdir -p archive/tmp
mkdir -p archive/data

# Kill all running Vite servers
echo "Stopping all Vite dev servers..."
pkill -f "vite"

# Move test files to tests directory
echo "Moving test files to archive/tests..."
find . -maxdepth 1 -name "test_*.py" -exec mv {} archive/tests/ \;
find . -maxdepth 1 -name "*_test.py" -exec mv {} archive/tests/ \;
find . -maxdepth 1 -name "test*.py" -not -name "test_document_upload.py" -exec mv {} archive/tests/ \;

# Move backup files to backups directory
echo "Moving backup files to archive/backups..."
mv ultra_backup.py archive/backups/ 2>/dev/null || true
mv ultra_hyper_backup.py archive/backups/ 2>/dev/null || true
mv Ultra_Base_Backup.zip archive/backups/ 2>/dev/null || true
find . -name "*.bak" -exec mv {} archive/backups/ \;

# Move deprecated React files to deprecated directory
echo "Moving deprecated React files to archive/deprecated..."
mv src/basic-app.jsx archive/deprecated/ 2>/dev/null || true
mv src/simplified-main.jsx archive/deprecated/ 2>/dev/null || true
mv src/test-pricing.jsx archive/deprecated/ 2>/dev/null || true
mv src/main.tsx archive/deprecated/ 2>/dev/null || true

# Move logs and output files to logs directory
echo "Moving logs and output files to archive/logs..."
find . -maxdepth 1 -name "*.log" -exec mv {} archive/logs/ \;
find . -maxdepth 1 -name "*.txt" -not -name "requirements.txt" -not -name "performance_test_requirements.txt" -exec mv {} archive/logs/ \;

# Move timestamped directories to tmp
echo "Moving timestamped directories to archive/tmp..."
find . -maxdepth 1 -type d -name "20*" -exec mv {} archive/tmp/ \;

# Move JSON analysis files to data directory
echo "Moving JSON analysis files to archive/data..."
find . -maxdepth 1 -name "llm_analysis_results_*.json" -exec mv {} archive/data/ \;

# Remove .DS_Store files
echo "Removing .DS_Store files..."
find . -name ".DS_Store" -delete

# Fix path resolution in vite.config.ts
echo "Checking vite.config.ts path alias configuration..."
if ! grep -q "'@': path.resolve(__dirname, './src')" vite.config.ts; then
  echo "Updating vite.config.ts with correct path alias..."
  sed -i '' 's/resolve: {/resolve: {\n    alias: {\n      '\''@'\'': path.resolve(__dirname, '\''\.\/src'\''),\n    },/g' vite.config.ts
fi

# Create utils.ts if it doesn't exist
if [ ! -f src/lib/utils.ts ]; then
  echo "Creating missing utils.ts file..."
  mkdir -p src/lib
  cat > src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF
fi

echo "Cleaning node_modules/.vite directory..."
rm -rf node_modules/.vite/deps_temp_* 2>/dev/null || true

echo "Cleanup complete! You should now restart your development server with 'npm run dev'"
echo "Consider running 'git status' to see what files have been moved" 