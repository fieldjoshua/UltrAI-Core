# Ultra Scripts

This directory contains utility scripts and tools for the Ultra AI Framework.

## Scripts

- `cleanup.py`: Code cleanup and maintenance utility
- `api.py`: API client and testing utility

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

## Adding New Scripts

When adding new scripts:

1. Add the script to this directory
2. Update this README with information about the script
3. Ensure the script has proper documentation and help text
4. Make the script executable (`chmod +x scriptname.py`)

## Requirements

Scripts may have additional dependencies beyond the core project requirements.
If a script requires special dependencies, include a comment at the top of the
script file indicating what's needed.
