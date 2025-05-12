#\!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo -e "${YELLOW}===================================${NC}"
echo -e "${YELLOW}Ultra Production Environment Testing Script${NC}"
echo -e "${YELLOW}===================================${NC}"

# Function to create a temporary environment file for testing
create_test_env() {
    echo -e "${BLUE}Creating temporary test environment file...${NC}"

    # Read the .env.example file as template
    if [ -f ".env.example" ]; then
        cp .env.example .env.test_production
    else
        echo "ERROR: .env.example file not found\!"
        exit 1
    fi

    # Set critical variables for production environment testing
    cat >> .env.test_production << EOF

# Test production environment settings
ENVIRONMENT=production
TESTING=true
USE_MOCK=false
MOCK_MODE=false

# Required for authentication tests
API_KEY_ENCRYPTION_KEY="SAMPLE_KEY_FOR_TESTING_ONLY_REPLACE_IN_PRODUCTION"
SECRET_KEY="test-secret-key-for-production-testing"
JWT_SECRET="test-jwt-secret-for-production-testing"

# API keys (add actual keys for production testing)
# OPENAI_API_KEY=""
# ANTHROPIC_API_KEY=""
# GOOGLE_API_KEY=""
EOF

    echo -e "${GREEN}Temporary environment file created at .env.test_production${NC}"
    echo -e "${YELLOW}NOTE: For full testing with real LLM APIs, add valid API keys to this file${NC}"
}

# Function to run a specific test suite with production environment
run_test() {
    TEST_NAME=$1
    TEST_COMMAND=$2

    echo -e "\n${BLUE}======= Running $TEST_NAME =======${NC}"

    # Export environment variables for production environment testing
    export ENVIRONMENT=production
    export TESTING=true
    export USE_MOCK=false
    export MOCK_MODE=false
    export API_KEY_ENCRYPTION_KEY="SAMPLE_KEY_FOR_TESTING_ONLY"

    # Load environment variables from the test file
    if [ -f ".env.test_production" ]; then
        export $(grep -v '^#' .env.test_production | xargs)
    fi

    # Execute the test
    eval $TEST_COMMAND

    # Check exit status
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $TEST_NAME passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $TEST_NAME failed${NC}"
        return 1
    fi
}

# Function to check preconditions
check_preconditions() {
    echo -e "${BLUE}Checking test prerequisites...${NC}"
    
    # Check for Python requirements
    if \! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed or not in PATH${NC}"
        exit 1
    fi
    
    # Check for required packages
    python3 -c "import pytest, fastapi" &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}Missing required Python packages. Please install requirements:${NC}"
        echo "pip install -r requirements.txt"
        exit 1
    fi
    
    echo -e "${GREEN}All prerequisites passed${NC}"
}

# Function to clean up after testing
cleanup() {
    echo -e "\n${BLUE}Cleaning up test environment...${NC}"

    # Remove temporary environment file
    if [ -f ".env.test_production" ]; then
        rm .env.test_production
    fi

    # Reset environment variables
    unset ENVIRONMENT
    unset TESTING
    unset USE_MOCK
    unset MOCK_MODE
    unset API_KEY_ENCRYPTION_KEY

    echo -e "${GREEN}Cleanup complete${NC}"
}

# Main test runner
main() {
    # Check prerequisites
    check_preconditions

    # Create test environment
    create_test_env

    # Track overall success
    TESTS_PASSED=true

    # Run tests in production environment

    # 1. Test basic health endpoint
    run_test "Basic Health Endpoint Test" "python -m pytest backend/tests/test_health_endpoint.py::test_health_endpoint_basic -v"
    if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

    # 2. Test JWT utilities
    run_test "JWT Utils Test" "python -m pytest backend/tests/test_jwt_utils.py -v"
    if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

    # 3. Test rate limiting
    run_test "Rate Limit Service Test" "python -m pytest backend/tests/test_rate_limit_service.py -v"
    if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

    # 4. Test authentication endpoints
    run_test "Auth Endpoints Test" "python -m pytest backend/tests/test_auth_endpoints.py -v"
    if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

    # 5. Test full API flow without LLM responses
    # Note: This test won't check actual LLM responses without valid API keys
    run_test "API Health Test" "python test_api.py --base-url http://localhost:8085 --models test_model"
    if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

    # Display summary
    echo -e "\n${YELLOW}===================================${NC}"
    echo -e "${YELLOW}Test Summary${NC}"
    echo -e "${YELLOW}===================================${NC}"

    if $TESTS_PASSED; then
        echo -e "${GREEN}All tests passed in production environment\!${NC}"
        echo -e "${GREEN}The system is ready for production deployment.${NC}"
    else
        echo -e "${RED}Some tests failed in production environment.${NC}"
        echo -e "${RED}Please review the failures before deploying to production.${NC}"
    fi

    # Cleanup
    cleanup

    # Return appropriate exit code
    if $TESTS_PASSED; then
        return 0
    else
        return 1
    fi
}

# Run main function
main
