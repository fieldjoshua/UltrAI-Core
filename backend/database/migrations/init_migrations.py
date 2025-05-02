#!/usr/bin/env python3
"""
Database migration initialization tool.

This script initializes the database migration system with the current database schema.
It creates a baseline migration containing the current database schema as a starting point.
"""

import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('init_migrations')

# Constants
ALEMBIC_CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), 'alembic.ini')


def run_alembic_command(args, dry_run=False):
    """
    Run an Alembic command with the specified arguments.
    
    Args:
        args: List of Alembic command arguments
        dry_run: If True, print the command without executing
        
    Returns:
        Return code from the command
    """
    cmd = ['alembic', '-c', ALEMBIC_CONFIG] + args
    logger.info(f"Running: {' '.join(cmd)}")
    
    if dry_run:
        logger.info("DRY RUN: Command not executed")
        return 0
    
    try:
        return subprocess.call(cmd)
    except Exception as e:
        logger.error(f"Error running Alembic command: {str(e)}")
        return 1


def create_baseline_migration(message: str = "Initial database schema", dry_run: bool = False) -> int:
    """
    Create a baseline migration representing the current database schema.
    
    Args:
        message: Message to use for the migration
        dry_run: If True, print commands without executing
        
    Returns:
        Return code (0 for success)
    """
    logger.info("Creating baseline migration...")
    
    # Create a revision with the current schema
    return run_alembic_command(['revision', '--autogenerate', '--message', message], dry_run=dry_run)


def stamp_database(revision: str = "head", dry_run: bool = False) -> int:
    """
    Stamp the database with the specified revision without running migrations.
    
    Args:
        revision: Revision to stamp (default: head)
        dry_run: If True, print commands without executing
        
    Returns:
        Return code (0 for success)
    """
    logger.info(f"Stamping database with revision: {revision}")
    
    # Stamp the database with the specified revision
    return run_alembic_command(['stamp', revision], dry_run=dry_run)


def init_migrations(message: str = "Initial database schema", stamp: bool = True, 
                   dry_run: bool = False) -> int:
    """
    Initialize the migration system with the current database schema.
    
    Args:
        message: Message to use for the baseline migration
        stamp: Whether to stamp the database with the baseline revision
        dry_run: If True, print commands without executing
        
    Returns:
        Return code (0 for success)
    """
    logger.info("Initializing database migrations...")
    
    # Create baseline migration
    result = create_baseline_migration(message, dry_run)
    if result != 0:
        logger.error("Failed to create baseline migration")
        return result
    
    # If requested, stamp the database with the baseline revision
    if stamp:
        result = stamp_database("head", dry_run)
        if result != 0:
            logger.error("Failed to stamp database")
            return result
    
    logger.info("Migration initialization complete!")
    return 0


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Initialize database migrations with the current schema'
    )
    parser.add_argument(
        '--message', '-m',
        default="Initial database schema",
        help='Message for the baseline migration'
    )
    parser.add_argument(
        '--no-stamp', 
        action='store_true',
        help='Do not stamp the database with the baseline revision'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Print commands without executing them'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        return init_migrations(
            message=args.message,
            stamp=not args.no_stamp,
            dry_run=args.dry_run
        )
    except KeyboardInterrupt:
        logger.info("Operation cancelled")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())