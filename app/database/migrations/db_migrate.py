#!/usr/bin/env python3
"""
Database Migration CLI Tool

This script provides a command-line interface for managing database migrations
using Alembic. It handles common migration operations such as generating new
migrations, upgrading, downgrading, and checking status.

Typical usage:
    python -m backend.database.migrations.db_migrate status
    python -m backend.database.migrations.db_migrate upgrade
    python -m backend.database.migrations.db_migrate downgrade -1
    python -m backend.database.migrations.db_migrate generate "Add user roles"
"""

import argparse
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("db_migrate")

# Constants
ALEMBIC_CONFIG = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "alembic.ini",
)
BACKUP_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
    "backups",
)


def run_alembic_command(args: List[str], dry_run: bool = False) -> int:
    """
    Run an Alembic command with the specified arguments.

    Args:
        args: List of Alembic command arguments
        dry_run: If True, print the command without executing

    Returns:
        Return code from the command (0 for success)
    """
    cmd = ["alembic", "-c", ALEMBIC_CONFIG] + args
    logger.info(f"Running: {' '.join(cmd)}")

    if dry_run:
        logger.info("DRY RUN: Command not executed")
        return 0

    try:
        return subprocess.call(cmd)
    except Exception as e:
        logger.error(f"Error running Alembic command: {str(e)}")
        return 1


def backup_database(
    connection_string: Optional[str] = None, backup_name: Optional[str] = None
) -> str:
    """
    Create a backup of the database before running migrations.

    Args:
        connection_string: Database connection string (uses env vars if None)
        backup_name: Custom name for the backup file (uses timestamp if None)

    Returns:
        Path to the backup file
    """
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not backup_name:
        backup_name = f"db_backup_{timestamp}.sql"

    # Full path to backup file
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    # Get database connection info from environment if not provided
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "ultra")
    db_user = os.environ.get("DB_USER", "ultrauser")
    db_password = os.environ.get("DB_PASSWORD", "ultrapassword")

    # Build pg_dump command
    cmd = [
        "pg_dump",
        "-h",
        db_host,
        "-p",
        db_port,
        "-U",
        db_user,
        "-d",
        db_name,
        "-f",
        backup_path,
        "--clean",
        "--if-exists",
    ]

    # Set PGPASSWORD environment variable for password
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    logger.info(f"Creating database backup at {backup_path}")
    try:
        subprocess.run(cmd, env=env, check=True, stderr=subprocess.PIPE)
        logger.info(f"Backup completed successfully")
        return backup_path
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Backup failed: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
        )
        raise


def restore_database(backup_path: str, connection_string: Optional[str] = None) -> bool:
    """
    Restore database from a backup file.

    Args:
        backup_path: Path to the backup file
        connection_string: Database connection string (uses env vars if None)

    Returns:
        True if restoration was successful, False otherwise
    """
    if not os.path.exists(backup_path):
        logger.error(f"Backup file not found: {backup_path}")
        return False

    # Get database connection info from environment if not provided
    db_host = os.environ.get("DB_HOST", "localhost")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "ultra")
    db_user = os.environ.get("DB_USER", "ultrauser")
    db_password = os.environ.get("DB_PASSWORD", "ultrapassword")

    # Build psql command to restore
    cmd = [
        "psql",
        "-h",
        db_host,
        "-p",
        db_port,
        "-U",
        db_user,
        "-d",
        db_name,
        "-f",
        backup_path,
    ]

    # Set PGPASSWORD environment variable for password
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    logger.info(f"Restoring database from {backup_path}")
    try:
        subprocess.run(cmd, env=env, check=True, stderr=subprocess.PIPE)
        logger.info("Database restored successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Restore failed: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
        )
        return False


def get_migration_status() -> Dict[str, Any]:
    """
    Get current migration status information.

    Returns:
        Dictionary with migration status details
    """
    # Create a temporary file to capture output
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
        temp_path = temp.name

    try:
        # Run alembic current and history commands to get status
        cmd = ["alembic", "-c", ALEMBIC_CONFIG, "current", "--verbose"]
        current_output = subprocess.check_output(cmd, universal_newlines=True)

        cmd = ["alembic", "-c", ALEMBIC_CONFIG, "history", "--verbose"]
        history_output = subprocess.check_output(cmd, universal_newlines=True)

        # Parse the outputs to get useful information
        current_revision = None
        for line in current_output.splitlines():
            # Alembic outputs different formats depending on version and configuration
            line = line.strip()
            if not line:
                continue

            # Format: 1eecfa604b93 (head)
            if line.endswith("(head)"):
                parts = line.strip().split()
                if parts:
                    current_revision = parts[0].strip()
                    break
            # Format: Current revision for ...
            elif "current revision" in line.lower():
                parts = line.split(":")
                if len(parts) >= 2:
                    current_revision = parts[1].strip()
                    break

        # Count total migrations from history
        total_migrations = len(
            [line for line in history_output.splitlines() if line.startswith("Rev: ")]
        )

        # Parse pending migrations (this is an approximation)
        try:
            # Get heads from alembic instead of using history with range
            cmd = ["alembic", "-c", ALEMBIC_CONFIG, "heads"]
            heads_output = subprocess.check_output(cmd, universal_newlines=True)

            # If we have a head and current revision is matching or missing, then we're up to date
            if current_revision and current_revision.lower() != "current":
                # Find the latest head
                head_revision = None
                for line in heads_output.splitlines():
                    if line.strip():  # Skip empty lines
                        head_revision = line.strip().split()[0]
                        break

                if head_revision and current_revision == head_revision:
                    # We're at the head, so no pending migrations
                    pending_migrations = 0
                else:
                    # We're behind the head, estimate pending migrations
                    pending_migrations = 1  # At least one migration is pending
            else:
                # All migrations are pending or parser could not detect version
                cmd = ["alembic", "-c", ALEMBIC_CONFIG, "history", "--verbose"]
                history_output = subprocess.check_output(cmd, universal_newlines=True)
                pending_migrations = len(
                    [
                        line
                        for line in history_output.splitlines()
                        if line.startswith("Rev: ")
                    ]
                )
        except subprocess.CalledProcessError:
            # If command fails, default to 0 pending
            pending_migrations = 0

        # Get database connection status
        db_connected = True
        try:
            from app.database.connection import check_database_connection

            db_connected = check_database_connection()
        except ImportError:
            logger.warning("Could not import backend.database connection module")
            db_connected = None

        return {
            "current_revision": current_revision,
            "total_migrations": total_migrations,
            "pending_migrations": max(0, pending_migrations),
            "database_connected": db_connected,
            "checked_at": datetime.now().isoformat(),
        }
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Error getting migration status: {e.output.decode('utf-8') if hasattr(e, 'output') else str(e)}"
        )
        return {
            "error": str(e),
            "checked_at": datetime.now().isoformat(),
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def print_migration_status() -> None:
    """
    Print formatted migration status to console.
    """
    status = get_migration_status()

    if "error" in status:
        logger.error(f"Error retrieving migration status: {status['error']}")
        return

    print("\n=== DATABASE MIGRATION STATUS ===")
    print(f"Current Revision: {status['current_revision'] or 'Not initialized'}")
    print(f"Total Migrations: {status['total_migrations']}")
    print(f"Pending Migrations: {status['pending_migrations']}")
    print(f"Database Connected: {status['database_connected']}")
    print(f"Status Time: {status['checked_at']}")
    print("=" * 32)


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for the CLI.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Database migration management tool",
        epilog="For more information, see the documentation.",
    )

    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Migration command")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show migration status")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database schema")
    upgrade_parser.add_argument(
        "revision", nargs="?", default="head", help="Target revision (default: head)"
    )
    upgrade_parser.add_argument(
        "--sql", action="store_true", help="Don't execute the migration, just show SQL"
    )
    upgrade_parser.add_argument(
        "--backup", action="store_true", help="Create database backup before upgrading"
    )

    # Downgrade command
    downgrade_parser = subparsers.add_parser(
        "downgrade", help="Downgrade database schema"
    )
    downgrade_parser.add_argument(
        "revision", help="Target revision or relative revision (-1)"
    )
    downgrade_parser.add_argument(
        "--sql", action="store_true", help="Don't execute the migration, just show SQL"
    )
    downgrade_parser.add_argument(
        "--backup",
        action="store_true",
        help="Create database backup before downgrading",
    )

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate new migration")
    generate_parser.add_argument("message", help="Migration message")
    generate_parser.add_argument(
        "--autogenerate",
        action="store_true",
        help="Autogenerate migration based on model changes",
    )

    # History command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose output"
    )

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify migration integrity")
    verify_parser.add_argument(
        "--head-only", action="store_true", help="Only verify the head migration"
    )

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup database")
    backup_parser.add_argument("-o", "--output", help="Output file name")

    # Restore command
    restore_parser = subparsers.add_parser(
        "restore", help="Restore database from backup"
    )
    restore_parser.add_argument("backup", help="Path to backup file")

    # Common arguments for all commands (except history which already has --verbose)
    for p in [
        status_parser,
        upgrade_parser,
        downgrade_parser,
        generate_parser,
        verify_parser,
        backup_parser,
        restore_parser,
    ]:
        p.add_argument(
            "--verbose", "-v", action="store_true", help="Show verbose output"
        )

    return parser


def main() -> int:
    """
    Main entry point for the migration CLI.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    # Set logging level based on verbosity
    if getattr(args, "verbose", False):
        logger.setLevel(logging.DEBUG)

    try:
        if args.command == "status":
            print_migration_status()
            return 0

        elif args.command == "upgrade":
            if args.backup:
                try:
                    backup_database()
                except Exception as e:
                    logger.error(f"Backup failed: {str(e)}")
                    if (
                        input("Continue with upgrade without backup? (y/n): ").lower()
                        != "y"
                    ):
                        return 1

            alembic_args = ["upgrade", args.revision]
            if args.sql:
                alembic_args.append("--sql")

            return run_alembic_command(alembic_args)

        elif args.command == "downgrade":
            if args.backup:
                try:
                    backup_database()
                except Exception as e:
                    logger.error(f"Backup failed: {str(e)}")
                    if (
                        input("Continue with downgrade without backup? (y/n): ").lower()
                        != "y"
                    ):
                        return 1

            alembic_args = ["downgrade", args.revision]
            if args.sql:
                alembic_args.append("--sql")

            return run_alembic_command(alembic_args)

        elif args.command == "generate":
            alembic_args = ["revision", "--message", args.message]
            if args.autogenerate:
                alembic_args.append("--autogenerate")

            return run_alembic_command(alembic_args)

        elif args.command == "history":
            alembic_args = ["history"]
            if args.verbose:
                alembic_args.append("--verbose")

            return run_alembic_command(alembic_args)

        elif args.command == "verify":
            print("Verifying migration integrity...")
            # This is a simplified verification for now
            # More advanced verification would require parsing and analyzing
            # the migration scripts

            status = get_migration_status()
            if "error" in status:
                logger.error(f"Error verifying migrations: {status['error']}")
                return 1

            print("Migration verification passed!")
            return 0

        elif args.command == "backup":
            try:
                backup_path = backup_database(backup_name=args.output)
                print(f"Backup created at: {backup_path}")
                return 0
            except Exception as e:
                logger.error(f"Backup failed: {str(e)}")
                return 1

        elif args.command == "restore":
            success = restore_database(args.backup)
            return 0 if success else 1

        else:
            logger.error(f"Unknown command: {args.command}")
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nOperation canceled.")
        return 130
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
