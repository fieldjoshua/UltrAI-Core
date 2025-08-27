# Cursor AI Task Breakdown for Codebase Reduction

This file contains specific tasks formatted for easy copy-paste into Cursor's AI assistant. Each task includes context and specific instructions.

## Phase 1: Quick Wins (High Priority - 1.8GB+ savings)

### Task 1: Remove Archive Directories
```
Please remove the ARCHIVE_20250606 directory and any other archive directories in the project. These contain 1.8GB of old code and should not be in version control. After removing, add **/ARCHIVE_* to .gitignore to prevent future additions.
```

### Task 2: Clean Up Logs and Temporary Files
```
Find and remove all .log files, .pyc files, and __pycache__ directories throughout the project. Also remove these directories if they exist:
- logs/
- temp/
- tmp/
- .pytest_cache/
- .mypy_cache/
Update .gitignore to include these patterns.
```

### Task 3: Remove Output Directories
```
Remove these output directories that shouldn't be in version control:
- outputs/
- responses/
- pipeline_outputs/
- results/
Add them to .gitignore after removal.
```

## Phase 2: Documentation Cleanup (Medium Priority)

### Task 4: Consolidate Duplicate Documentation
```
We have multiple copies of the same documentation files. Please:
1. Find all duplicate .md files (api_documentation.md, product_vision.md, etc.)
2. Keep only the most recent/complete version
3. Remove duplicates from supporting_docs/, documentation/, and other directories
4. Create a single source of truth for each document
```

### Task 5: Clean UI/UX Assets
```
The documentation/ui-ux directory contains 35 HTML mockup files that should be removed or moved to a separate design repository. Please clean up this directory, keeping only essential design documentation.
```

## Phase 3: Code Consolidation (Medium Priority)

### Task 6: Consolidate Orchestrator Services
```
We have 3 different orchestrator implementations:
- orchestration_service.py
- orchestrator_v2.py  
- orchestrator.py

Please review these and consolidate into a single orchestration_service.py, keeping the best features from each. Remove the redundant files and update all imports.
```

### Task 7: Consolidate Service Layer
```
Consolidate these duplicate services:
- Pricing: Choose between pricing_service.py, pricing_manager.py, pricing_engine.py, pricing.py, pricing_calculator.py
- Parameters: Choose between parameter_manager.py, parameter_service.py, parameter_handler.py
- Remove the redundant implementations and update imports
```

### Task 8: Unify Requirements Files
```
We have 33 different requirements*.txt files. Please:
1. Keep only requirements.txt (dev) and requirements-production.txt (prod)
2. Consolidate all dependencies from other files
3. Remove all other requirements*.txt files
4. Ensure Poetry files (pyproject.toml, poetry.lock) are the primary dependency source
```

## Phase 4: Final Cleanup (Low Priority)

### Task 9: Update .gitignore
```
Update .gitignore to include all the patterns we've cleaned up:
- Archive directories
- Virtual environments
- Log files
- Temporary directories
- Output directories
- Python cache files
- Node modules
- Build artifacts
```

### Task 10: Verify Everything Works
```
After all cleanup:
1. Run: make test
2. Run: make dev (verify development server starts)
3. Run: cd frontend && npm run build (verify frontend builds)
4. Check that all imports still resolve correctly
5. Ensure no critical functionality was broken
```

## How to Use This With Cursor

1. Open Cursor in the Ultra project
2. Copy each task one at a time into Cursor's AI assistant
3. Let Cursor execute the task
4. Review the changes before committing
5. Test after each phase to ensure nothing breaks
6. Commit changes after each successful phase

## Expected Results

- Repository size: From ~2GB to ~100MB
- File count: From 5000+ to <1000
- Cleaner project structure
- Faster git operations
- Easier navigation

## Safety Notes

- Always review changes before committing
- Test after each phase
- Keep a backup of the repository before starting
- Some "duplicate" files might have important differences - review carefully