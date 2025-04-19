# Ultra Project Cleanup and Organization

This document explains the file organization strategy and path resolution fixes implemented in the cleanup script.

## File Organization Strategy

The `cleanup.sh` script organizes your files into the following structure:

```
/archive
  /tests        # All test files
  /backups      # Backup files and old versions
  /deprecated   # Old components/versions
  /logs         # Log files and output
  /tmp          # Temporary files
  /data         # Analysis data and results
```

### Files Moved to Archive

1. **Test Files → archive/tests/**
   - All `test_*.py` files (except for test_document_upload.py)
   - Files like `test_apis.py`, `test_claude.py`, etc.

2. **Backup Files → archive/backups/**
   - `ultra_backup.py` and `ultra_hyper_backup.py`
   - `Ultra_Base_Backup.zip`
   - Files with `.bak` extension

3. **Deprecated React Files → archive/deprecated/**
   - `src/basic-app.jsx`
   - `src/simplified-main.jsx`
   - `src/test-pricing.jsx`
   - `src/main.tsx` (since you're using main.jsx now)

4. **Logs and Output → archive/logs/**
   - `.log` files
   - `.txt` files (except requirements files)

5. **Timestamped Directories → archive/tmp/**
   - All `20250401_*` directories

6. **Analysis Data → archive/data/**
   - All `llm_analysis_results_*.json` files

## Path Resolution Issues Fixed

Your main path resolution issue was related to the `@/lib/utils` import that wasn't resolving correctly. The script:

1. Ensures your `vite.config.ts` has the correct path alias configuration:
   ```typescript
   resolve: {
     alias: {
       '@': path.resolve(__dirname, './src'),
     },
   }
   ```

2. Creates a proper `src/lib/utils.ts` file if it doesn't exist, containing the essential `cn()` function used by shadcn-ui components.

3. Cleans the Vite dependencies cache in `node_modules/.vite/deps_temp_*` to force a fresh rebuild.

## Development Server Cleanup

The script kills all running Vite development servers using `pkill -f "vite"`. This addresses the issue where you had multiple servers running on ports 3000-3008.

## How to Use

1. Make the script executable:
   ```bash
   chmod +x cleanup.sh
   ```

2. Run the script:
   ```bash
   ./cleanup.sh
   ```

3. Restart your development server:
   ```bash
   npm run dev
   ```

## Path Resolution Warning Signs

If you see errors like this in the future:
```
Error: The following dependencies are imported but could not be resolved:
  @/lib/utils (imported by /Users/joshuafield/Documents/Ultra/src/components/ui/checkbox.tsx)
```

Check:
1. That your path aliases in `vite.config.ts` match those in `components.json`
2. That the referenced files exist at the expected paths
3. That you don't have multiple competing dev servers running 