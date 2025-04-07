#!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Ultra Framework Tests${NC}"
echo "=========================================="

# Environment setup
export TEST_MODE=True
export SENTRY_ENVIRONMENT=test

# Check for Python virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found, using system Python.${NC}"
fi

# Function to run a test and report results
run_test() {
    TEST_TYPE=$1
    TEST_CMD=$2
    
    echo -e "\n${YELLOW}Running $TEST_TYPE Tests...${NC}"
    echo "----------------------------------------"
    
    eval $TEST_CMD
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $TEST_TYPE Tests Passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $TEST_TYPE Tests Failed${NC}"
        return 1
    fi
}

# Track overall success
TESTS_PASSED=true

# 1. Run backend tests
run_test "Backend API" "pytest backend/tests -v"
if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

# 2. Run frontend tests
run_test "Frontend" "npm test"
if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

# 3. Run ESLint
run_test "ESLint" "npm run lint"
if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

# 4. Run Prettier check
run_test "Prettier" "npm run format:check"
if [ $? -ne 0 ]; then TESTS_PASSED=false; fi

# 5. Run Ultra performance tests (if available)
if [ -f "backend/performance_test.py" ]; then
    run_test "Performance" "python backend/performance_test.py --mode quick --output performance_reports/pre_deploy"
    if [ $? -ne 0 ]; then TESTS_PASSED=false; fi
fi

# Output summary
echo -e "\n${YELLOW}Test Summary${NC}"
echo "=========================================="

if $TESTS_PASSED; then
    echo -e "${GREEN}All tests passed! Ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please fix the issues before deploying.${NC}"
    exit 1
fi 