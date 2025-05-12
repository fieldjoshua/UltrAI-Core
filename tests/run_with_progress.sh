#!/bin/bash

# Enhanced test runner with progress monitoring
# Part of the MVPTestCoverage action

# Set environment variables for testing
export MOCK_MODE=true
export ENVIRONMENT=test
export DEBUG=true
export SENTRY_DSN=""
export ALLOWED_EXTERNAL_DOMAINS="api.openai.com,api.anthropic.com,api.mistral.ai"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Default report path
REPORT_PATH="test_report.json"

# Parse command line arguments
while (( "$#" )); do
  case "$1" in
    --report)
      REPORT_PATH="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --report PATH    Path to save test report (default: test_report.json)"
      echo "  --help           Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Error: python3 not found${NC}"; exit 1; }
command -v pytest >/dev/null 2>&1 || { echo -e "${RED}Error: pytest not found${NC}"; exit 1; }

# Check if the progress monitor is available
if [ ! -f "$(dirname "$0")/test_progress.py" ]; then
  echo -e "${YELLOW}Warning: test_progress.py not found, running without progress monitoring${NC}"
  USE_PROGRESS=false
else
  chmod +x "$(dirname "$0")/test_progress.py"
  USE_PROGRESS=true
fi

# Ensure we're in the project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "$0")/.." && pwd)")
cd "$PROJECT_ROOT" || { echo -e "${RED}Error: Could not change to project root directory${NC}"; exit 1; }

# Create or initialize progress monitor
if [ "$USE_PROGRESS" = true ]; then
  # Create a named pipe for progress updates
  FIFO="/tmp/ultra_test_fifo_$$"
  rm -f "$FIFO"
  mkfifo "$FIFO"
  
  # Start the progress monitor in the background
  python3 "$(dirname "$0")/test_progress.py" --report "$REPORT_PATH" < "$FIFO" &
  MONITOR_PID=$!
  
  # Open the pipe for writing
  exec 3>"$FIFO"
  
  # Send initial commands to the monitor
  echo '{"command": "init"}' >&3
fi

# Function to run a test category
run_test_category() {
  local category="$1"
  local description="$2"
  shift 2
  
  echo -e "${BLUE}${BOLD}Running $description...${NC}"
  
  if [ "$USE_PROGRESS" = true ]; then
    echo "{\"command\": \"start_category\", \"category\": \"$category\"}" >&3
  fi
  
  # Run each test in the category
  local all_passed=true
  for test_file in "$@"; do
    test_name=$(basename "$test_file" .py)
    echo -e "${BLUE}Running $test_name...${NC}"
    
    # Run the test and capture output
    TEST_START=$(date +%s.%N)
    output=$(python3 -m pytest "$test_file" -v 2>&1)
    exit_code=$?
    TEST_END=$(date +%s.%N)
    TEST_DURATION=$(echo "$TEST_END - $TEST_START" | bc)
    
    # Determine the result
    if [ $exit_code -eq 0 ]; then
      result="pass"
      echo -e "${GREEN}✓ $test_name passed in ${TEST_DURATION}s${NC}"
    elif [ $exit_code -eq 5 ]; then
      result="skip"
      echo -e "${YELLOW}⚠ $test_name skipped${NC}"
    else
      result="fail"
      all_passed=false
      echo -e "${RED}✗ $test_name failed in ${TEST_DURATION}s${NC}"
      # Extract the error message
      error_message=$(echo "$output" | grep -A 5 "FAILED" | head -n 6 | tr '\n' ' ' | sed 's/\"//g')
    fi
    
    # Send test result to progress monitor
    if [ "$USE_PROGRESS" = true ]; then
      if [ "$result" = "fail" ]; then
        echo "{\"command\": \"test_result\", \"category\": \"$category\", \"test\": \"$test_name\", \"result\": \"$result\", \"duration\": $TEST_DURATION, \"message\": \"$error_message\"}" >&3
      else
        echo "{\"command\": \"test_result\", \"category\": \"$category\", \"test\": \"$test_name\", \"result\": \"$result\", \"duration\": $TEST_DURATION}" >&3
      fi
    fi
  done
  
  if [ "$USE_PROGRESS" = true ]; then
    echo "{\"command\": \"end_category\", \"category\": \"$category\"}" >&3
  fi
  
  if [ "$all_passed" = true ]; then
    echo -e "${GREEN}${BOLD}All $description passed!${NC}"
    return 0
  else
    echo -e "${RED}${BOLD}Some $description failed!${NC}"
    return 1
  fi
}

# Main test execution
echo -e "${BOLD}=======================================================${NC}"
echo -e "${BOLD}     Ultra Test Suite with Progress Monitoring${NC}"
echo -e "${BOLD}=======================================================${NC}"

# Set up test categories
# Format: category name, description, test files...
API_TESTS=("API" "API Endpoint Tests" 
  "backend/tests/test_health_endpoint.py" 
  "backend/tests/test_available_models_endpoint.py"
  "backend/tests/test_analyze_endpoint.py"
  "backend/tests/test_llm_request_endpoint.py"
  "backend/tests/test_api.py"
)

AUTH_TESTS=("AUTH" "Authentication Tests"
  "backend/tests/test_jwt_utils.py"
  "backend/tests/test_auth_edge_cases.py"
  "backend/tests/test_auth_endpoints.py"
  "backend/tests/test_e2e_auth_workflow.py"
)

RATE_TESTS=("RATE" "Rate Limiting Tests"
  "backend/tests/test_rate_limit_service.py"
  "backend/tests/test_rate_limit_middleware.py"
)

ORCH_TESTS=("ORCH" "Orchestrator Tests"
  "test_basic_orchestrator.py"
  "test_orchestrator.py"
)

INTEG_TESTS=("INTEG" "Integration Tests"
  "backend/tests/test_e2e_analysis_flow.py"
  "test_health_check.py"
)

# Run test categories
ALL_PASSED=true

run_test_category "${API_TESTS[@]}" || ALL_PASSED=false
run_test_category "${AUTH_TESTS[@]}" || ALL_PASSED=false
run_test_category "${RATE_TESTS[@]}" || ALL_PASSED=false
run_test_category "${ORCH_TESTS[@]}" || ALL_PASSED=false
run_test_category "${INTEG_TESTS[@]}" || ALL_PASSED=false

# Finalize the progress monitor
if [ "$USE_PROGRESS" = true ]; then
  echo '{"command": "finalize"}' >&3
  exec 3>&-  # Close the pipe
  rm -f "$FIFO"
  wait "$MONITOR_PID"  # Wait for the progress monitor to finish
fi

# Print summary
echo -e "${BOLD}=======================================================${NC}"
if [ "$ALL_PASSED" = true ]; then
  echo -e "${GREEN}${BOLD}All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}${BOLD}Some tests failed!${NC}"
  exit 1
fi