#!/bin/bash

# Ultra AI MVP Deployment Verification Script
# This script runs the deployment verification tests to ensure
# that the deployed application is functioning correctly.

set -e

# Define colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print functions
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
    echo "  -e, --environment ENV    Specify environment (development, production)"
    echo "  -u, --url URL            Specify the base URL to test against"
    echo "  -v, --verbose            Show detailed test output"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --environment production --url http://api.ultra.ai"
    exit 0
}

# Process command-line arguments
ENVIRONMENT="development"
BASE_URL="http://localhost:8000"
VERBOSE=false

while [ "$1" != "" ]; do
    case $1 in
        -e | --environment )    shift
                                ENVIRONMENT=$1
                                ;;
        -u | --url )            shift
                                BASE_URL=$1
                                ;;
        -v | --verbose )        VERBOSE=true
                                ;;
        -h | --help )           show_help
                                exit
                                ;;
        * )                     show_help
                                exit 1
    esac
    shift
done

# Load environment variables
ENV_FILE=".env.$ENVIRONMENT"
if [ -f "$ENV_FILE" ]; then
    print_section "Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' $ENV_FILE | xargs)
else
    print_warning "Environment file $ENV_FILE not found. Using default settings."
fi

# Export test variables
export TEST_API_URL="$BASE_URL"

# Run deployment verification tests
print_section "Running deployment verification tests against $BASE_URL"

# Determine pytest verbosity
if [ "$VERBOSE" = true ]; then
    VERBOSITY="-v"
else
    VERBOSITY="-v"  # Always use at least some verbosity for better feedback
fi

# Run the tests
if python -m pytest tests/deployment/test_deployment.py $VERBOSITY; then
    print_success "All deployment verification tests passed!"
else
    print_error "Deployment verification tests failed!"

    # Ask if user wants to see logs
    read -p "Do you want to check the application logs? [y/N] " check_logs
    if [[ "$check_logs" == "y" || "$check_logs" == "Y" ]]; then
        print_section "Checking Docker logs"
        docker-compose logs --tail=100
    fi

    # Ask if user wants to rollback
    read -p "Do you want to rollback the deployment? [y/N] " do_rollback
    if [[ "$do_rollback" == "y" || "$do_rollback" == "Y" ]]; then
        print_section "Initiating rollback"
        ./scripts/rollback-mvp.sh --environment "$ENVIRONMENT" --force
    fi

    exit 1
fi

# Check API response times for performance verification
print_section "Performing basic performance checks"

echo "Testing API response time..."
start_time=$(date +%s.%N)
curl -s "$BASE_URL/health" > /dev/null
end_time=$(date +%s.%N)
response_time=$(echo "$end_time - $start_time" | bc)

echo "Health endpoint response time: ${response_time}s"

if (( $(echo "$response_time > 1.0" | bc -l) )); then
    print_warning "Health endpoint response time is slow (${response_time}s > 1.0s)"
else
    print_success "Health endpoint response time is good (${response_time}s)"
fi

# Final summary
print_section "Deployment Verification Summary"
echo "Environment: $ENVIRONMENT"
echo "Base URL: $BASE_URL"
echo "Verification completed at: $(date)"
print_success "Deployment verification completed successfully!"

exit 0
