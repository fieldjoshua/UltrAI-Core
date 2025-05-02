#!/usr/bin/env python3
"""
Database Migration Status Check

This script checks if there are pending database migrations. It is designed to be used
in CI/CD pipelines to prevent deployments if migrations need to be applied.

Exit codes:
- 0: No pending migrations
- 1: Pending migrations exist
- 2: Error checking migration status
"""

import os
import sys
import json
import argparse
import subprocess
from typing import Dict, Any, Tuple, Optional

def check_migration_status() -> Tuple[int, Optional[Dict[str, Any]]]:
    """
    Check for pending database migrations.
    
    Returns:
        Tuple of (exit_code, status_data)
    """
    try:
        # Run migration status command
        result = subprocess.run(
            ["python", "-m", "backend.database.migrations.db_migrate", "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        # Check for errors
        if result.returncode != 0:
            print(f"Error running migration status: {result.stderr}")
            return 2, None
            
        # Parse output to extract migration status
        output_lines = result.stdout.splitlines()
        status_data = {}
        
        for line in output_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                status_data[key.strip()] = value.strip()
                
        # Check if there are pending migrations
        pending_migrations = int(status_data.get("Pending Migrations", "0"))
        
        if pending_migrations > 0:
            return 1, status_data
        else:
            return 0, status_data
    except Exception as e:
        print(f"Error checking migration status: {str(e)}")
        return 2, None


def main() -> int:
    """
    Main function.
    
    Returns:
        Exit code (0: success, 1: pending migrations, 2: error)
    """
    parser = argparse.ArgumentParser(description="Check for pending database migrations")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--fail-on-pending", action="store_true", 
                      help="Exit with non-zero code if pending migrations exist")
    args = parser.parse_args()
    
    # Check migration status
    exit_code, status_data = check_migration_status()
    
    # Output in JSON format if requested
    if args.json and status_data:
        print(json.dumps(status_data, indent=2))
    elif status_data:
        print("=== Database Migration Status ===")
        for key, value in status_data.items():
            print(f"{key}: {value}")
            
    # Determine exit code
    if args.fail_on_pending and exit_code == 1:
        print("Error: Pending migrations must be applied before deployment")
        return 1
    elif exit_code == 2:
        print("Error checking migration status")
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())