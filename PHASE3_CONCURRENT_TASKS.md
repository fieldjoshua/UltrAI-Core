# Phase 3: Code Consolidation - Concurrent Task Split

## Tasks for Cursor AI

### Cursor Task 1: Consolidate Pricing Services
```
We have 5 different pricing services that need consolidation:
1. Find all pricing-related files: pricing_service.py, pricing_manager.py, pricing_engine.py, pricing.py, pricing_calculator.py
2. Review each implementation to understand their features
3. Keep ONLY pricing_service.py as the main implementation
4. Merge any unique/valuable features from other files into pricing_service.py
5. Delete the redundant files: pricing_manager.py, pricing_engine.py, pricing.py, pricing_calculator.py
6. Update all imports throughout the codebase to use pricing_service.py
```

### Cursor Task 2: Consolidate Parameter Services
```
We have 3 parameter management services:
1. Find: parameter_manager.py, parameter_service.py, parameter_handler.py
2. Review each to understand their functionality
3. Keep ONLY parameter_service.py as the main implementation
4. Merge valuable features from other files if needed
5. Delete parameter_manager.py and parameter_handler.py
6. Update all imports to use parameter_service.py
```

### Cursor Task 3: Clean Up Requirements Files
```
We have 33 requirements*.txt files. Please:
1. List all requirements*.txt files in the project
2. Keep ONLY these two files:
   - requirements.txt (for development)
   - requirements-production.txt (for production)
3. Check if any other requirements files have unique dependencies not in the main two
4. Add any missing dependencies to the appropriate file
5. Delete all other requirements*.txt files
6. Ensure pyproject.toml and poetry.lock remain as the primary dependency source
```

## Tasks for Claude (I'll handle these)

### Claude Task 1: Consolidate Orchestrator Services
- Review orchestration_service.py, orchestrator_v2.py, orchestrator.py
- Keep orchestration_service.py as the main implementation
- Remove redundant implementations

### Claude Task 2: Review Service Layer for Other Duplicates
- Check for other duplicate services not yet identified
- Consolidate any found duplicates

### Claude Task 3: Update Imports and References
- Ensure all imports point to the consolidated services
- Update any documentation references