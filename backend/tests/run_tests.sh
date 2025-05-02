#!/bin/bash

# Script to run core API tests for Ultra backend
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
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found. Please install it with 'pip install pytest'.${NC}"
    exit 1
fi

# Print header
echo -e "${YELLOW}============================================${NC}"
echo -e "${YELLOW}Running Ultra Core API Test Suite${NC}"
echo -e "${YELLOW}============================================${NC}"
echo

# Run critical endpoint tests first
echo -e "${YELLOW}Running health endpoint tests...${NC}"
pytest -xvs test_health_endpoint.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Health endpoint tests failed!${NC}"
    exit 1
fi
echo -e "${GREEN}Health endpoint tests passed.${NC}"
echo

echo -e "${YELLOW}Running available models endpoint tests...${NC}"
pytest -xvs test_available_models_endpoint.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Available models endpoint tests failed!${NC}"
    exit 1
fi
echo -e "${GREEN}Available models endpoint tests passed.${NC}"
echo

echo -e "${YELLOW}Running analyze endpoint tests...${NC}"
pytest -xvs test_analyze_endpoint.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Analyze endpoint tests failed!${NC}"
    exit 1
fi
echo -e "${GREEN}Analyze endpoint tests passed.${NC}"
echo

echo -e "${YELLOW}Running LLM request endpoint tests...${NC}"
pytest -xvs test_llm_request_endpoint.py
if [ $? -ne 0 ]; then
    echo -e "${RED}LLM request endpoint tests failed!${NC}"
    exit 1
fi
echo -e "${GREEN}LLM request endpoint tests passed.${NC}"
echo

# Run any other tests
echo -e "${YELLOW}Running remaining API tests...${NC}"
pytest -xvs test_api.py test_rate_limit_middleware.py
echo

# Print summary
echo -e "${YELLOW}============================================${NC}"
echo -e "${GREEN}All critical tests completed.${NC}"
echo -e "${YELLOW}============================================${NC}"

exit 0