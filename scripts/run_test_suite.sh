#!/bin/bash

# Ultra Test Suite Runner
# This script runs all tests and generates coverage reports

# Set environment variables for testing
export MOCK_MODE=true
export ENVIRONMENT=testing
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

# Default parameters
REPORT_DIR="test_reports"
HTML_REPORT=false
ONLY_CATEGORY=""
FAIL_FAST=false
PARALLEL=false

# Parse command line arguments
while (( "$#" )); do
  case "$1" in
    --report-dir)
      REPORT_DIR="$2"
      shift 2
      ;;
    --html)
      HTML_REPORT=true
      shift
      ;;
    --category)
      ONLY_CATEGORY="$2"
      shift 2
      ;;
    --fail-fast)
      FAIL_FAST=true
      shift
      ;;
    --parallel)
      PARALLEL=true
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --report-dir DIR   Directory to save test reports (default: test_reports)"
      echo "  --html             Generate HTML coverage report"
      echo "  --category NAME    Run only specific category (api, auth, rate-limit, document, integration)"
      echo "  --fail-fast        Stop on first failure"
      echo "  --parallel         Run tests in parallel"
      echo "  --help             Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Prepare directory structure
mkdir -p "$REPORT_DIR"
mkdir -p "$REPORT_DIR/json"
mkdir -p logs
mkdir -p document_storage
mkdir -p temp_uploads

# Initialize tracking file
TRACKING_FILE="$REPORT_DIR/test_progress.json"
python scripts/track_test_progress.py --output "$TRACKING_FILE"

# Define test categories
declare -A TEST_CATEGORIES
TEST_CATEGORIES["api"]="backend/tests/test_analyze_endpoint.py backend/tests/test_available_models_endpoint.py backend/tests/test_llm_request_endpoint.py backend/tests/test_health_endpoint.py backend/tests/test_api.py"
TEST_CATEGORIES["auth"]="backend/tests/test_auth_endpoints.py backend/tests/test_jwt_utils.py backend/tests/test_auth_edge_cases.py backend/tests/test_e2e_auth_workflow.py"
TEST_CATEGORIES["rate-limit"]="backend/tests/test_rate_limit_service.py backend/tests/test_rate_limit_middleware.py"
TEST_CATEGORIES["document"]="backend/tests/test_e2e_analysis_flow.py backend/tests/test_document_upload.py"
TEST_CATEGORIES["integration"]="test_orchestrator.py test_basic_orchestrator.py"
TEST_CATEGORIES["e2e"]="test_api.py"

# Determine which categories to run
CATEGORIES=("api" "auth" "rate-limit" "document" "integration" "e2e")
if [ -n "$ONLY_CATEGORY" ]; then
  if [[ -v "TEST_CATEGORIES[$ONLY_CATEGORY]" ]]; then
    CATEGORIES=("$ONLY_CATEGORY")
  else
    echo -e "${RED}Error: Unknown category '$ONLY_CATEGORY'${NC}"
    exit 1
  fi
fi

# Function to run a test category
run_test_category() {
  local category="$1"
  local test_pattern="${TEST_CATEGORIES[$category]}"
  local result_file="$REPORT_DIR/json/$category-results.json"
  local coverage_file="$REPORT_DIR/coverage-$category.xml"

  echo -e "\n${BOLD}${BLUE}Running $category tests...${NC}"

  # Update tracking file - mark category as running
  python scripts/track_test_progress.py --output "$TRACKING_FILE" --category "$category" --status "running"

  # Prepare pytest arguments
  local pytest_args="-v --cov=. --cov-report=xml:$coverage_file --json-report --json-report-file=$result_file"

  if [ "$FAIL_FAST" = true ]; then
    pytest_args="$pytest_args -x"
  fi

  if [ "$PARALLEL" = true ]; then
    pytest_args="$pytest_args -n auto"
  fi

  # Run the tests
  PYTHONPATH=. pytest $test_pattern $pytest_args
  local test_exit_code=$?

  # Update tracking file with results
  python scripts/track_test_progress.py --output "$TRACKING_FILE" --import-results "$result_file" --category "$category"

  if [ $test_exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ $category tests completed successfully${NC}"
    return 0
  else
    echo -e "${RED}✗ $category tests failed${NC}"
    return 1
  fi
}

# Run all specified test categories
ALL_PASSED=true

for category in "${CATEGORIES[@]}"; do
  run_test_category "$category"
  if [ $? -ne 0 ]; then
    ALL_PASSED=false
    if [ "$FAIL_FAST" = true ]; then
      echo -e "${RED}${BOLD}Stopping due to test failures (fail-fast mode)${NC}"
      break
    fi
  fi
done

# Generate combined coverage report
echo -e "\n${BLUE}${BOLD}Generating combined coverage report...${NC}"
coverage combine "$REPORT_DIR/coverage-"*.xml
coverage xml -o "$REPORT_DIR/coverage.xml"
coverage report

if [ "$HTML_REPORT" = true ]; then
  echo -e "\n${BLUE}${BOLD}Generating HTML coverage report...${NC}"
  coverage html -d "$REPORT_DIR/html"
  echo -e "${GREEN}HTML report generated in $REPORT_DIR/html/index.html${NC}"
fi

# Print final summary
python scripts/track_test_progress.py --output "$TRACKING_FILE"

# Exit with appropriate status
if [ "$ALL_PASSED" = true ]; then
  echo -e "\n${GREEN}${BOLD}All tests passed!${NC}"
  exit 0
else
  echo -e "\n${RED}${BOLD}Some tests failed!${NC}"
  exit 1
fi
