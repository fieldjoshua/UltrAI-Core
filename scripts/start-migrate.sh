#!/bin/bash
# Database migration and application startup script
# This script handles database migrations before starting the application

set -e

# Create necessary directories
mkdir -p logs
mkdir -p document_storage
mkdir -p temp
mkdir -p temp_uploads
mkdir -p backups

# Default values
APPLY_MIGRATIONS=${APPLY_MIGRATIONS:-true}
BACKUP_BEFORE_MIGRATE=${BACKUP_BEFORE_MIGRATE:-true}
ALLOW_PENDING_MIGRATIONS=${ALLOW_PENDING_MIGRATIONS:-false}
DB_CONNECTION_RETRIES=${DB_CONNECTION_RETRIES:-30}
DB_CONNECTION_RETRY_INTERVAL=${DB_CONNECTION_RETRY_INTERVAL:-2}

# Print banner
echo "====================================="
echo "  Ultra Backend Startup"
echo "====================================="

# Wait for database to be ready
echo "Waiting for database to be ready..."
python3 -m backend.utils.wait_for_db

# Check migration status
echo "Checking database migration status..."
migration_status=$(python3 -m backend.database.migrations.db_migrate status 2>/dev/null || echo "Error checking migration status")

# Check if there are pending migrations
pending_migrations=$(echo "$migration_status" | grep -i "pending migrations" | sed 's/[^0-9]*//g')

if [ -z "$pending_migrations" ]; then
  pending_migrations=0
fi

echo "Found $pending_migrations pending migrations"

# Backup database if requested
if [ "$BACKUP_BEFORE_MIGRATE" = "true" ] && [ "$pending_migrations" -gt 0 ] && [ "$APPLY_MIGRATIONS" = "true" ]; then
  timestamp=$(date +%Y%m%d_%H%M%S)
  backup_file="backups/pre_migration_${timestamp}.sql"
  echo "Creating database backup at $backup_file..."
  python3 -m backend.database.migrations.db_migrate backup --output "$backup_file"
fi

# Apply migrations if requested
if [ "$APPLY_MIGRATIONS" = "true" ] && [ "$pending_migrations" -gt 0 ]; then
  echo "Applying database migrations..."
  python3 -m backend.database.migrations.db_migrate upgrade
elif [ "$pending_migrations" -gt 0 ]; then
  echo "Warning: $pending_migrations pending migrations are not being applied"
  if [ "$ALLOW_PENDING_MIGRATIONS" != "true" ]; then
    echo "Error: Pending migrations must be applied before starting the application"
    echo "Set ALLOW_PENDING_MIGRATIONS=true to bypass this check (not recommended)"
    exit 1
  fi
  echo "ALLOW_PENDING_MIGRATIONS=true, continuing with pending migrations..."
fi

# Register migration health check
echo "Registering migration health check..."
python3 -c 'from backend.database.migrations.migration_health import register_migration_health_check; register_migration_health_check()'

# Start the FastAPI application with auto-reload for development
echo "Starting Ultra backend in development mode..."
python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload