#!/bin/bash

# Script to organize outdated directories into NEWArchive
echo "Starting cleanup and organization..."

# Create all necessary NEWArchive subdirectories if they don't exist
mkdir -p NEWArchive/virtual_envs      # For Python environments
mkdir -p NEWArchive/temp_files        # For temporary files
mkdir -p NEWArchive/cache             # For cache files
mkdir -p NEWArchive/old_code          # For deprecated code
mkdir -p NEWArchive/data_outputs      # For output data
mkdir -p NEWArchive/build_artifacts   # For build files
mkdir -p NEWArchive/misc              # For miscellaneous files
mkdir -p NEWArchive/docs              # For documentation/non-technical files
mkdir -p data/outputs                 # New location for outputs
mkdir -p data/logs                    # New location for logs
mkdir -p data/responses               # New location for responses
mkdir -p data/temp                    # New location for temp files
mkdir -p data/models                  # New location for models

# 1. Handle Python environments - keep .venv, archive venv and ~/venv
echo "Handling Python environments..."
mv venv NEWArchive/virtual_envs/ 2>/dev/null || true
mv ~/Documents/Ultra/~/.venv NEWArchive/virtual_envs/backup_venv 2>/dev/null || true

# 2. Handle temporary directories
echo "Handling temporary directories..."
if [ -d "temp" ]; then
  if [ "$(ls -A temp)" ]; then
    cp -r temp/* data/temp/ 2>/dev/null || true
  fi
  mv temp NEWArchive/temp_files/
fi

if [ -d "temp_uploads" ]; then
  if [ "$(ls -A temp_uploads)" ]; then
    cp -r temp_uploads/* data/temp/ 2>/dev/null || true
  fi
  mv temp_uploads NEWArchive/temp_files/
fi

# 3. Handle Python cache
echo "Handling cache files..."
mv __pycache__ NEWArchive/cache/ 2>/dev/null || true

# 4. Handle old code
echo "Handling old code..."
mv trillm_orchestrator NEWArchive/old_code/ 2>/dev/null || true
mv trillm_orchestrator.egg-info NEWArchive/old_code/ 2>/dev/null || true
mv UltrAI NEWArchive/old_code/ 2>/dev/null || true
mv ~ NEWArchive/old_code/backup_dir 2>/dev/null || true

# 5. Handle data output directories
echo "Handling data outputs..."
if [ -d "outputs" ]; then
  if [ "$(ls -A outputs)" ]; then
    cp -r outputs/* data/outputs/ 2>/dev/null || true
  fi
  mv outputs NEWArchive/data_outputs/
fi

if [ -d "logs" ]; then
  if [ "$(ls -A logs)" ]; then
    cp -r logs/* data/logs/ 2>/dev/null || true
  fi
  mv logs NEWArchive/data_outputs/
fi

if [ -d "responses" ]; then
  if [ "$(ls -A responses)" ]; then
    cp -r responses/* data/responses/ 2>/dev/null || true
  fi
  mv responses NEWArchive/data_outputs/
fi

# 6. Handle models
echo "Handling models directory..."
if [ -d "models" ]; then
  if [ "$(ls -A models)" ]; then
    cp -r models/* data/models/ 2>/dev/null || true
  fi
  mv models NEWArchive/data_outputs/
fi

# 7. Handle Nontechnical directory
echo "Handling Nontechnical directory..."
if [ -d "Nontechnical" ]; then
  mkdir -p docs/nontechnical
  find Nontechnical -name "*.pdf" -o -name "*.csv" -o -name "*.md" -o -name "*.txt" | while read file; do
    cp "$file" docs/nontechnical/ 2>/dev/null || true
  done
  mv Nontechnical NEWArchive/docs/
fi

# 8. Handle build directories
echo "Handling build artifacts..."
if [ -d "dist" ]; then
  mv dist NEWArchive/build_artifacts/
fi

if [ -d "public" ]; then
  if [ "$(ls -A public)" ]; then
    cp -r public/* frontend/public/ 2>/dev/null || true
  fi
  mv public NEWArchive/build_artifacts/
fi

# 9. Check if we need to keep archive folder
echo "Handling archive directory..."
if [ -d "archive" ]; then
  mv archive NEWArchive/old_code/previous_archive 2>/dev/null || true
fi

echo "Cleanup and organization complete!"
echo "Outdated files have been archived in NEWArchive/"
echo "Important data has been copied to appropriate directories in the new structure"
