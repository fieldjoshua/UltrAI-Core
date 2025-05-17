#!/bin/bash
# Database Migration Wrapper Script
# This script provides a convenient way to run database migration commands

set -e

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Print usage information
usage() {
  echo "Database Migration Utility"
  echo "Usage: $0 <command> [options]"
  echo ""
  echo "Commands:"
  echo "  status              Check migration status"
  echo "  upgrade [revision]  Apply migrations (default: head)"
  echo "  downgrade <rev>     Revert to previous migration"
  echo "  generate <msg>      Generate new migration"
  echo "  auto <msg>          Generate auto migration"
  echo "  history             Show migration history"
  echo "  verify              Verify migration integrity"
  echo "  init [msg]          Initialize migrations"
  echo "  backup [file]       Backup database"
  echo "  restore <file>      Restore database from backup"
  echo "  help                Show this help message"
  echo ""
  echo "Options:"
  echo "  -v, --verbose       Enable verbose output"
  echo "  -n, --dry-run       Show commands without executing"
  echo "  --sql               Show SQL instead of executing"
  echo ""
  echo "Examples:"
  echo "  $0 status           Show current migration status"
  echo "  $0 upgrade          Apply all pending migrations"
  echo "  $0 generate \"Add user roles\""
  echo "                      Create new migration"
  echo "  $0 auto \"Add user roles\""
  echo "                      Create auto-generated migration"
  echo "  $0 backup           Backup the database"
  echo ""
}

# Check if Python command exists
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 command not found"
  exit 1
fi

# Parse arguments
COMMAND=""
ARGS=()

# Process command
if [ $# -ge 1 ]; then
  COMMAND="$1"
  shift
fi

# Prepare options based on command
case "$COMMAND" in
  "status")
    ARGS=("status")
    ;;
  "upgrade")
    ARGS=("upgrade")
    if [ $# -ge 1 ]; then
      # Check if it's an option
      if [[ "$1" != -* ]]; then
        ARGS+=("$1")
        shift
      fi
    fi
    ;;
  "downgrade")
    if [ $# -ge 1 ]; then
      ARGS=("downgrade" "$1")
      shift
    else
      echo "Error: downgrade requires a revision argument"
      usage
      exit 1
    fi
    ;;
  "generate")
    if [ $# -ge 1 ]; then
      ARGS=("generate" "$1")
      shift
    else
      echo "Error: generate requires a message"
      usage
      exit 1
    fi
    ;;
  "auto")
    if [ $# -ge 1 ]; then
      ARGS=("generate" "$1" "--autogenerate")
      shift
    else
      echo "Error: auto requires a message"
      usage
      exit 1
    fi
    ;;
  "history")
    ARGS=("history")
    ;;
  "verify")
    ARGS=("verify")
    ;;
  "init")
    if [ $# -ge 1 ] && [[ "$1" != -* ]]; then
      python3 -m backend.database.migrations.init_migrations --message "$1" "$@"
    else
      python3 -m backend.database.migrations.init_migrations "$@"
    fi
    exit $?
    ;;
  "backup")
    ARGS=("backup")
    if [ $# -ge 1 ] && [[ "$1" != -* ]]; then
      ARGS+=("--output" "$1")
      shift
    fi
    ;;
  "restore")
    if [ $# -ge 1 ] && [[ "$1" != -* ]]; then
      ARGS=("restore" "$1")
      shift
    else
      echo "Error: restore requires a backup file path"
      usage
      exit 1
    fi
    ;;
  "help"|"--help"|"-h")
    usage
    exit 0
    ;;
  *)
    echo "Error: Unknown command '$COMMAND'"
    usage
    exit 1
    ;;
esac

# Add remaining arguments
while [ $# -gt 0 ]; do
  case "$1" in
    "--verbose"|"-v")
      ARGS+=("--verbose")
      ;;
    "--dry-run"|"-n")
      ARGS+=("--dry-run")
      ;;
    "--sql")
      ARGS+=("--sql")
      ;;
    "--backup")
      ARGS+=("--backup")
      ;;
    *)
      # Unknown option
      ARGS+=("$1")
      ;;
  esac
  shift
done

# Run the migration command
python3 -m backend.database.migrations.db_migrate "${ARGS[@]}"
