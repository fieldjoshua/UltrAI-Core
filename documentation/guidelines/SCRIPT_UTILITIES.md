# UltraAI Script Utilities

This document describes utility scripts and tools for the UltraAI Framework.

## IMPORTANT: Documentation First Approach

**BEFORE CREATING ANY NEW FEATURES OR MAKING CHANGES:**

1. **ALWAYS consult the documentation directory first**
2. **Check if the feature or pattern already exists**
3. **Review the consolidated documentation in `documentation/`**

## Available Scripts

The `scripts/` directory contains:

- `cleanup.py`: Code cleanup and maintenance utility
- `api.py`: API client and testing utility
- `organize_files.sh`: Organization script for project structure
- `cleanup_organize.sh`: Combined cleanup and organization script
- `verify_structure.sh`: Verifies the project structure is correct
- `deploy-to-cloud.sh`: Handles cloud deployment
- `update-deps.sh`: Updates project dependencies
- `start-backend.sh`: Starts the backend server
- `start-frontend.sh`: Starts the frontend server
- `run_app.sh`: Runs both frontend and backend
- `run_tests.sh`: Runs project tests
- `deploy.sh`: Deployment script
- `cleanup.sh`: Shell-based cleanup utility

## Usage

### Cleanup Script

The cleanup script helps maintain code quality by:

- Removing unused imports
- Formatting code according to project standards
- Removing debug prints and commented-out code

```bash
python scripts/cleanup.py [--path /path/to/clean]
```

### API Script

The API script provides a command-line interface for testing API endpoints:

```bash
python scripts/api.py [endpoint] [--method POST] [--data '{"key": "value"}']
```

### Start Scripts

To start the backend:

```bash
./scripts/start-backend.sh
```

To start the frontend:

```bash
./scripts/start-frontend.sh
```

To run both:

```bash
./scripts/run_app.sh
```

### Organization Scripts

To organize project files:

```bash
./scripts/organize_files.sh
```

To verify project structure:

```bash
./scripts/verify_structure.sh
```

## Adding New Scripts

When adding new scripts:

1. **First check if similar functionality already exists**
2. Add the script to the `scripts/` directory
3. Update this documentation with information about the script
4. Ensure the script has proper documentation and help text
5. Make the script executable (`chmod +x scriptname.py` or `chmod +x scriptname.sh`)

## Script Documentation Standards

Each script should:

1. Have a clear header comment explaining its purpose
2. Include usage instructions when run with `--help`
3. Provide meaningful error messages
4. Be well-commented for future maintenance

## Requirements

Scripts may have additional dependencies beyond the core project requirements.
If a script requires special dependencies, include a comment at the top of the
script file indicating what's needed.

## Script Categories

- **Cleanup & Organization**: cleanup.py, organize_files.sh, cleanup_organize.sh
- **Development Helpers**: start-backend.sh, start-frontend.sh, run_app.sh
- **Testing Utilities**: run_tests.sh, api.py
- **Deployment Tools**: deploy.sh, deploy-to-cloud.sh
- **Maintenance**: update-deps.sh, cleanup.sh
