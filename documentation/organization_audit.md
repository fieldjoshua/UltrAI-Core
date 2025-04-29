# Ultra Project Organization Audit

This document provides an assessment of the current project structure and recommendations for reorganization.

## Standalone Files That Should Be Moved

### Scripts to Move to `.aicheck/scripts` Directory

- `ai` - The main AICheck interface script
- `cleanup_aicheck.sh` - Script for cleaning up AICheck installations

### Demo Files to Move to `/frontend/demos`

- `cyberpunk-demo.html` - Cyberpunk theme demo page

### Configuration Files to Organize

These configuration files should remain in the root but could be documented in a `/documentation/configuration/` directory:

1. **Language/Linting Configuration:**
   - `.pylintrc`
   - `.flake8`
   - `.bandit`
   - `.bandit.yaml`
   - `.pre-commit-config.yaml`
   - `.editorconfig`
   - `.prettierrc`
   - `.babelrc`
   - `.cursorrc`
   - `setup.cfg`

2. **Deployment Configuration:**
   - `Dockerfile`
   - `docker-compose.yml`
   - `.dockerignore`
   - `vercel.json`
   - `.vercelignore`
   - `alembic.ini`
   - `Makefile`

3. **Package Management:**
   - `package.json`
   - `package-lock.json`
   - `requirements.txt`

## Directories That Should Be Reorganized

### Result Files

- `result_images/` - Should be moved to `data/images/` or `frontend/assets/images/`

### Potentially Redundant Directories

- `backend/` and `src/` seem to overlap in functionality
  - Consider consolidating these or establishing clearer boundaries

## Implementation Status

### Completed Moves

- ✅ Demo files successfully moved to `frontend/demos/`
- ✅ Result images successfully moved to `data/images/`
- ✅ Configuration documentation created in `documentation/configuration/`

### Pending Moves

- ⚠️ **Scripts**: Attempted to move the ai and cleanup_aicheck.sh scripts to .aicheck/scripts/, but encountered path dependency issues.
  - The scripts reference .aicheck/scripts/ in their paths, which would need to be updated.
  - We copied the scripts to scripts/ as an alternative.
  - Recommendation: Keep original scripts in root for now until a dedicated action can update paths systematically.
- ⬜ Backend/src consolidation (requires a dedicated refactoring action)

## Benefits of Reorganization

1. **Improved Navigation:** Files are organized by function, making it easier to find related resources
2. **Reduced Clutter:** Root directory contains fewer files, focusing attention on essential components
3. **Better Documentation:** Configuration files are still accessible but explained in documentation
4. **Consistent Structure:** Aligns with best practices for project organization

## Next Steps

1. Create a dedicated refactoring action to:
   - Update the script paths to be relative to their location
   - Test the scripts thoroughly after path changes
   - Move the updated scripts to their final location

2. Consider a dedicated action to analyze and consolidate the src/ and backend/ directories

## Notes

- Before reorganizing scripts, ensure thorough testing to prevent breaking existing functionality
- Update any paths in scripts or configuration files that reference moved resources
- Document changes in the project documentation
