#!/bin/bash

# Ultra AI MVP Deployment Script
# This script handles the deployment of the Ultra AI application
# to both development and production environments.

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
    echo -e " Ultra AI Deployment Pipeline - MVP v1.0"
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
    echo "  -e, --environment ENV   Specify deployment environment (development, production)"
    echo "  -t, --tag TAG           Specify Docker image tag (defaults to timestamp)"
    echo "  -c, --compose FILE      Specify Docker Compose file (defaults to docker-compose.yml)"
    echo "  -s, --skip-tests        Skip running tests"
    echo "  -b, --skip-build        Skip building Docker images"
    echo "  -r, --registry URL      Specify Docker registry URL"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --environment production --tag v1.2.3"
    exit 0
}

# Validate environment
validate_environment() {
    if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
        print_error "Invalid environment. Must be 'development' or 'production'."
        exit 1
    fi
}

# Load environment variables
load_environment_vars() {
    print_section "Loading environment variables for $ENVIRONMENT"

    ENV_FILE=".env.$ENVIRONMENT"
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found!"
        exit 1
    fi

    echo "Loading variables from $ENV_FILE"
    export $(grep -v '^#' $ENV_FILE | xargs)

    # Load API keys if available
    if [ -f ".env.api_keys" ]; then
        echo "Loading API keys from .env.api_keys"
        export $(grep -v '^#' .env.api_keys | xargs)
    fi

    # Set Docker Compose project name
    export COMPOSE_PROJECT_NAME="ultra-$ENVIRONMENT"

    echo "Environment variables loaded successfully."
}

# Create backup of current deployment
create_backup() {
    print_section "Creating backup of current deployment"

    BACKUP_DIR="backups/$ENVIRONMENT"
    BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"

    mkdir -p "$BACKUP_DIR"

    if [ -f "docker-compose.yml" ]; then
        # Create backup tar file with important config files
        tar -czf "$BACKUP_FILE" \
            docker-compose.yml \
            Dockerfile \
            .env.$ENVIRONMENT \
            scripts/*.sh

        echo "Backup created at $BACKUP_FILE"
    else
        print_warning "No docker-compose.yml found, skipping backup."
    fi
}

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        print_warning "Skipping tests as requested."
        return 0
    fi

    print_section "Running tests before deployment"

    if [ "$ENVIRONMENT" = "production" ]; then
        print_section "Running comprehensive test suite for production deployment"

        # Run backend tests
        echo "Running backend tests..."
        python -m pytest backend/tests/ -v || {
            print_error "Backend tests failed. Aborting deployment."
            exit 1
        }

        # Run integration tests if they exist
        if [ -d "tests/integration" ]; then
            echo "Running integration tests..."
            python -m pytest tests/integration/ -v || {
                print_error "Integration tests failed. Aborting deployment."
                exit 1
            }
        fi
    else
        print_section "Running basic test suite for development deployment"

        # Run only critical backend tests
        echo "Running critical backend tests..."
        python -m pytest backend/tests/test_api_endpoints.py backend/tests/test_health_endpoints.py -v || {
            print_error "Critical tests failed. Aborting deployment."
            exit 1
        }
    fi

    print_success "All tests passed successfully!"
}

# Build Docker images
build_docker_images() {
    if [ "$SKIP_BUILD" = true ]; then
        print_warning "Skipping build as requested."
        return 0
    fi

    print_section "Building Docker images"

    # Set build arguments based on environment
    if [ "$ENVIRONMENT" = "production" ]; then
        export BUILD_TARGET="final"
        export NODE_ENV="production"
    else
        export BUILD_TARGET="development"
        export NODE_ENV="development"
    fi

    # Build using Docker Compose
    echo "Building images with tag: $TAG"
    docker-compose -f "$COMPOSE_FILE" build --pull || {
        print_error "Docker build failed. Aborting deployment."
        exit 1
    }

    # Tag images if registry is specified
    if [ ! -z "$REGISTRY" ]; then
        echo "Tagging images for registry: $REGISTRY"
        docker tag ultraai/backend:$TAG $REGISTRY/ultraai/backend:$TAG
        print_success "Images built and tagged successfully!"
    else
        print_success "Images built successfully!"
    fi
}

# Push Docker images to registry
push_docker_images() {
    # Only push if registry is specified
    if [ -z "$REGISTRY" ]; then
        return 0
    fi

    print_section "Pushing Docker images to registry"

    # Login to Docker registry if credentials are provided
    if [ ! -z "$REGISTRY_USERNAME" ] && [ ! -z "$REGISTRY_PASSWORD" ]; then
        echo "Logging in to Docker registry..."
        echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY" -u "$REGISTRY_USERNAME" --password-stdin || {
            print_error "Docker registry login failed. Aborting deployment."
            exit 1
        }
    fi

    # Push the images
    echo "Pushing images to registry..."
    docker push $REGISTRY/ultraai/backend:$TAG || {
        print_error "Failed to push Docker images. Aborting deployment."
        exit 1
    }

    print_success "Images pushed to registry successfully!"
}

# Deploy the application
deploy_application() {
    print_section "Deploying application for $ENVIRONMENT environment"

    # Export the current version tag
    export TAG

    # Bring down existing services gracefully
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        echo "Stopping existing services..."
        docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    fi

    # Start the services
    echo "Starting services..."
    if [ "$ENVIRONMENT" = "production" ]; then
        # Production mode - run all services including workers but without frontend dev server
        docker-compose -f "$COMPOSE_FILE" --profile with-worker up -d || {
            print_error "Deployment failed. Rolling back..."
            rollback_deployment
            exit 1
        }
    else
        # Development mode - run all services including frontend dev server
        docker-compose -f "$COMPOSE_FILE" --profile with-worker --profile with-frontend up -d || {
            print_error "Deployment failed. Rolling back..."
            rollback_deployment
            exit 1
        }
    fi

    # Optional: if using Docker Model Runner
    if [ "$ENABLE_MODEL_RUNNER" = "true" ]; then
        echo "Starting Docker Model Runner..."
        docker-compose -f "$COMPOSE_FILE" --profile with-model-runner up -d || {
            print_warning "Docker Model Runner failed to start, but continuing deployment."
        }
    fi

    print_success "Application deployed successfully!"
}

# Verify deployment
verify_deployment() {
    print_section "Verifying deployment"

    echo "Waiting for services to be ready..."
    sleep 10

    # Check if services are up
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_error "Services failed to start. Rolling back..."
        rollback_deployment
        exit 1
    fi

    # Check backend health endpoint
    echo "Checking backend health..."
    HEALTH_CHECK_RETRIES=30
    HEALTH_CHECK_DELAY=2

    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        echo "Health check attempt $i of $HEALTH_CHECK_RETRIES..."

        HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT:-8000}/health 2>/dev/null || echo "000")

        if [ "$HEALTH_RESPONSE" = "200" ]; then
            echo "Backend is healthy!"
            break
        fi

        if [ $i -eq $HEALTH_CHECK_RETRIES ]; then
            print_error "Backend failed to become healthy. Rolling back..."
            rollback_deployment
            exit 1
        fi

        sleep $HEALTH_CHECK_DELAY
    done

    # Check database connectivity
    echo "Checking database connectivity..."
    HEALTH_RESPONSE=$(curl -s http://localhost:${PORT:-8000}/health/database 2>/dev/null)

    if ! echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        print_error "Database connectivity check failed. Rolling back..."
        rollback_deployment
        exit 1
    fi

    # Run deployment verification tests if they exist
    if [ -f "tests/deployment/test_deployment.py" ]; then
        echo "Running deployment verification tests..."
        python -m pytest tests/deployment/test_deployment.py -v || {
            print_error "Deployment verification tests failed. Rolling back..."
            rollback_deployment
            exit 1
        }
    else
        echo "No deployment verification tests found. Skipping."
    fi

    print_success "Deployment verified successfully!"
}

# Rollback deployment
rollback_deployment() {
    print_section "Rolling back deployment"

    # Get the latest backup
    BACKUP_DIR="backups/$ENVIRONMENT"
    LATEST_BACKUP=$(ls -t $BACKUP_DIR/backup-*.tar.gz 2>/dev/null | head -n 1)

    if [ -z "$LATEST_BACKUP" ]; then
        print_warning "No backup found for rollback. Attempting to stop services."
        docker-compose -f "$COMPOSE_FILE" down
        return 1
    fi

    echo "Rolling back to backup: $LATEST_BACKUP"

    # Extract backup
    ROLLBACK_DIR="$BACKUP_DIR/rollback-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$ROLLBACK_DIR"
    tar -xzf "$LATEST_BACKUP" -C "$ROLLBACK_DIR"

    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans

    # Start services from backup
    cd "$ROLLBACK_DIR"
    docker-compose up -d

    if [ $? -eq 0 ]; then
        print_success "Rollback completed successfully!"
    else
        print_error "Rollback failed. Manual intervention required."
        return 1
    fi
}

# Final report
show_deployment_report() {
    print_section "Deployment Report"

    echo "Environment: $ENVIRONMENT"
    echo "Docker Compose File: $COMPOSE_FILE"
    echo "Version Tag: $TAG"

    # Show running containers
    echo -e "\nRunning Containers:"
    docker-compose -f "$COMPOSE_FILE" ps

    # Show backend health status
    echo -e "\nBackend Health Status:"
    curl -s http://localhost:${PORT:-8000}/health

    echo -e "\nDeployment completed at: $(date)"

    # Save the current deployment info
    echo -e "\nSaving deployment information..."
    mkdir -p "deployments/$ENVIRONMENT"

    cat > "deployments/$ENVIRONMENT/latest.json" << EOL
{
    "version": "$TAG",
    "environment": "$ENVIRONMENT",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "compose_file": "$COMPOSE_FILE"
}
EOL

    print_success "Deployment information saved to deployments/$ENVIRONMENT/latest.json"
    print_success "Deployment completed successfully!"
}

# Main script execution starts here
print_banner

# Process command-line arguments
ENVIRONMENT="development"
TAG=$(date +%Y%m%d-%H%M%S)
COMPOSE_FILE="docker-compose.yml"
SKIP_TESTS=false
SKIP_BUILD=false
REGISTRY=""

while [ "$1" != "" ]; do
    case $1 in
        -e | --environment )    shift
                                ENVIRONMENT=$1
                                ;;
        -t | --tag )            shift
                                TAG=$1
                                ;;
        -c | --compose )        shift
                                COMPOSE_FILE=$1
                                ;;
        -s | --skip-tests )     SKIP_TESTS=true
                                ;;
        -b | --skip-build )     SKIP_BUILD=true
                                ;;
        -r | --registry )       shift
                                REGISTRY=$1
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

print_section "Starting deployment for $ENVIRONMENT environment"
echo "Tag: $TAG"
echo "Compose file: $COMPOSE_FILE"

# Create directories if they don't exist
mkdir -p backups/$ENVIRONMENT
mkdir -p deployments/$ENVIRONMENT

# Execute deployment steps
create_backup
load_environment_vars
run_tests
build_docker_images
push_docker_images
deploy_application
verify_deployment
show_deployment_report

exit 0
