#!/bin/bash

# Ultra AI MVP Rollback Script
# This script handles rolling back to a previous deployment
# for both development and production environments.

set -e

# Define colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define functions
print_banner() {
    echo -e "${BLUE}========================================"
    echo -e " Ultra AI Deployment Rollback - MVP v1.0"
    echo -e "========================================${NC}"
}

print_section() {
    echo -e "\n${BLUE}>> $1${NC}"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Specify deployment environment (development, production)"
    echo "  -b, --backup ID          Specify backup ID to restore (defaults to latest)"
    echo "  -c, --compose FILE       Specify Docker Compose file (defaults to docker-compose.yml)"
    echo "  -f, --force              Force rollback without confirmation"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --environment production --backup 20250511-120345"
    exit 0
}

# Validate environment
validate_environment() {
    if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
        print_error "Invalid environment. Must be 'development' or 'production'."
        exit 1
    fi
}

# List available backups
list_backups() {
    print_section "Available backups for $ENVIRONMENT environment"

    BACKUP_DIR="backups/$ENVIRONMENT"

    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "No backups directory found at $BACKUP_DIR"
        exit 1
    fi

    BACKUPS=$(ls -t $BACKUP_DIR/backup-*.tar.gz 2>/dev/null)

    if [ -z "$BACKUPS" ]; then
        print_error "No backups found for $ENVIRONMENT environment"
        exit 1
    fi

    echo "Available backups (newest first):"
    for backup in $BACKUPS; do
        # Extract date from filename
        BACKUP_DATE=$(basename $backup | sed 's/backup-\(.*\)\.tar\.gz/\1/')
        echo "  - $BACKUP_DATE ($(date -r $backup '+%Y-%m-%d %H:%M:%S'))"
    done
}

# Load environment variables
load_environment_vars() {
    print_section "Loading environment variables for $ENVIRONMENT"

    ENV_FILE=".env.$ENVIRONMENT"
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found, proceeding without it."
    else
        echo "Loading variables from $ENV_FILE"
        export $(grep -v '^#' $ENV_FILE | xargs)
    fi

    # Set Docker Compose project name
    export COMPOSE_PROJECT_NAME="ultra-$ENVIRONMENT"

    echo "Environment variables loaded successfully."
}

# Find and validate backup
find_backup() {
    BACKUP_DIR="backups/$ENVIRONMENT"

    if [ -z "$BACKUP_ID" ]; then
        echo "No backup ID specified, using latest backup."
        BACKUP_FILE=$(ls -t $BACKUP_DIR/backup-*.tar.gz 2>/dev/null | head -n 1)

        if [ -z "$BACKUP_FILE" ]; then
            print_error "No backups found for $ENVIRONMENT environment"
            exit 1
        fi

        BACKUP_ID=$(basename $BACKUP_FILE | sed 's/backup-\(.*\)\.tar\.gz/\1/')
    else
        BACKUP_FILE="$BACKUP_DIR/backup-$BACKUP_ID.tar.gz"

        if [ ! -f "$BACKUP_FILE" ]; then
            print_error "Backup with ID $BACKUP_ID not found"
            list_backups
            exit 1
        fi
    fi

    echo "Using backup: $BACKUP_ID (file: $BACKUP_FILE)"
    ROLLBACK_DIR="rollbacks/$ENVIRONMENT/$BACKUP_ID"
}

# Backup current state before rollback
backup_current_state() {
    print_section "Backing up current state before rollback"

    CURRENT_BACKUP_DIR="backups/$ENVIRONMENT"
    CURRENT_BACKUP_FILE="$CURRENT_BACKUP_DIR/pre-rollback-$(date +%Y%m%d-%H%M%S).tar.gz"

    mkdir -p "$CURRENT_BACKUP_DIR"

    if [ -f "docker-compose.yml" ]; then
        # Create backup tar file with important config files
        tar -czf "$CURRENT_BACKUP_FILE" \
            docker-compose.yml \
            Dockerfile \
            .env.$ENVIRONMENT \
            scripts/*.sh

        echo "Current state backed up to $CURRENT_BACKUP_FILE"
    else
        print_warning "No docker-compose.yml found, skipping backup of current state."
    fi
}

# Perform rollback
execute_rollback() {
    print_section "Rolling back to version $BACKUP_ID"

    # Create rollback directory
    mkdir -p "$ROLLBACK_DIR"

    # Extract backup
    echo "Extracting backup to $ROLLBACK_DIR..."
    tar -xzf "$BACKUP_FILE" -C "$ROLLBACK_DIR"

    # Get deployment details
    if [ -f "deployments/$ENVIRONMENT/latest.json" ]; then
        CURRENT_VERSION=$(grep -o '"version": "[^"]*"' deployments/$ENVIRONMENT/latest.json | cut -d '"' -f 4)
        echo "Rolling back from version $CURRENT_VERSION to backup $BACKUP_ID"
    else
        echo "No current deployment details found. Proceeding with rollback."
    fi

    # Stop current services
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        echo "Stopping current services..."
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    fi

    # Copy rollback files to current directory
    echo "Applying rollback files..."
    cp -r "$ROLLBACK_DIR"/* ./

    # If .env.$ENVIRONMENT exists in the backup, apply it
    if [ -f "$ROLLBACK_DIR/.env.$ENVIRONMENT" ]; then
        cp "$ROLLBACK_DIR/.env.$ENVIRONMENT" ./.env.$ENVIRONMENT
    fi

    # Start services from backup configuration
    echo "Starting services from backup configuration..."
    if [ "$ENVIRONMENT" = "production" ]; then
        # Production mode - run all services including workers but without frontend dev server
        docker-compose -f "$COMPOSE_FILE" --profile with-worker up -d || {
            print_error "Rollback failed. Manual intervention required."
            exit 1
        }
    else
        # Development mode - run all services including frontend dev server
        docker-compose -f "$COMPOSE_FILE" --profile with-worker --profile with-frontend up -d || {
            print_error "Rollback failed. Manual intervention required."
            exit 1
        }
    fi

    # Update deployment information
    mkdir -p "deployments/$ENVIRONMENT"

    cat > "deployments/$ENVIRONMENT/latest.json" << EOL
{
    "version": "rollback-to-$BACKUP_ID",
    "environment": "$ENVIRONMENT",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "compose_file": "$COMPOSE_FILE",
    "is_rollback": true,
    "rollback_from": "$CURRENT_VERSION"
}
EOL

    print_success "Rollback to $BACKUP_ID completed successfully!"
}

# Verify rollback
verify_rollback() {
    print_section "Verifying rollback"

    echo "Waiting for services to be ready..."
    sleep 10

    # Check if services are up
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_error "Services failed to start after rollback. Manual intervention required."
        exit 1
    fi

    # Check backend health endpoint
    echo "Checking backend health..."
    HEALTH_CHECK_RETRIES=15
    HEALTH_CHECK_DELAY=2

    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        echo "Health check attempt $i of $HEALTH_CHECK_RETRIES..."

        HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT:-8000}/health 2>/dev/null || echo "000")

        if [ "$HEALTH_RESPONSE" = "200" ]; then
            echo "Backend is healthy!"
            break
        fi

        if [ $i -eq $HEALTH_CHECK_RETRIES ]; then
            print_error "Backend failed to become healthy after rollback. Manual intervention required."
            exit 1
        fi

        sleep $HEALTH_CHECK_DELAY
    done

    print_success "Rollback verified successfully!"
}

# Show rollback report
show_rollback_report() {
    print_section "Rollback Report"

    echo "Environment: $ENVIRONMENT"
    echo "Rolled back to backup: $BACKUP_ID"
    echo "Rollback completed at: $(date)"

    # Show running containers
    echo -e "\nRunning Containers:"
    docker-compose -f "$COMPOSE_FILE" ps

    # Show backend health status
    echo -e "\nBackend Health Status:"
    curl -s http://localhost:${PORT:-8000}/health

    print_success "System successfully rolled back to previous state!"
}

# Main script execution starts here
print_banner

# Process command-line arguments
ENVIRONMENT="development"
BACKUP_ID=""
COMPOSE_FILE="docker-compose.yml"
FORCE=false

while [ "$1" != "" ]; do
    case $1 in
        -e | --environment )    shift
                                ENVIRONMENT=$1
                                ;;
        -b | --backup )         shift
                                BACKUP_ID=$1
                                ;;
        -c | --compose )        shift
                                COMPOSE_FILE=$1
                                ;;
        -f | --force )          FORCE=true
                                ;;
        -h | --help )           show_help
                                exit
                                ;;
        * )                     show_help
                                exit 1
    esac
    shift
done

# Validate environment
validate_environment

print_section "Preparing rollback for $ENVIRONMENT environment"

# If no backup ID specified, show available backups
if [ -z "$BACKUP_ID" ]; then
    list_backups

    # Ask for confirmation
    if [ "$FORCE" != true ]; then
        read -p "Do you want to proceed with rollback to the latest backup? [y/N] " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            echo "Rollback aborted."
            exit 0
        fi
    fi
fi

# Find and validate the backup to use
find_backup

# Ask for confirmation if not forced
if [ "$FORCE" != true ]; then
    read -p "Do you want to proceed with rollback to backup $BACKUP_ID? [y/N] " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Rollback aborted."
        exit 0
    fi
fi

# Create directories if they don't exist
mkdir -p rollbacks/$ENVIRONMENT/$BACKUP_ID

# Execute rollback steps
load_environment_vars
backup_current_state
execute_rollback
verify_rollback
show_rollback_report

exit 0
