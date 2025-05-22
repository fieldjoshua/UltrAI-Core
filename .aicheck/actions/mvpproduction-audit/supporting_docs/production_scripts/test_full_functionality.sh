#!/bin/bash
# Full MVP Functionality Test Script
# Tests all core features of the Ultra MVP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${BASE_URL:-"http://localhost:8000"}
TEST_USER=${TEST_USER:-"test@example.com"}
TEST_PASS=${TEST_PASS:-"testpass123"}

# Test results
TEST_RESULTS=()
TEST_COUNT=0
PASS_COUNT=0

function print_header() {
    echo -e "\n${YELLOW}=== $1 ===${NC}\n"
}

function test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected_status=$5

    TEST_COUNT=$((TEST_COUNT + 1))
    print_header "Testing: $name"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
                  -H "Content-Type: application/json" \
                  -d "$data" "$url")
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $name (Status: $status_code)"
        PASS_COUNT=$((PASS_COUNT + 1))
        TEST_RESULTS+=("PASS: $name")
    else
        echo -e "${RED}❌ FAIL${NC}: $name (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        TEST_RESULTS+=("FAIL: $name")
    fi
}

# Start testing
echo -e "${YELLOW}Ultra MVP Functionality Test${NC}"
echo "Base URL: $BASE_URL"
echo "Starting tests..."

# 1. Health Check
test_endpoint "Health Check" "GET" "$BASE_URL/api/health" "" "200"

# 2. Available Models
test_endpoint "Available Models" "GET" "$BASE_URL/api/available-models" "" "200"

# 3. Authentication Tests
test_endpoint "Login" "POST" "$BASE_URL/api/auth/login" \
    '{"email": "'$TEST_USER'", "password": "'$TEST_PASS'"}' "200"

# Store token if login successful
if [ $? -eq 0 ]; then
    TOKEN=$(echo "$body" | jq -r '.access_token')
    AUTH_HEADER="Authorization: Bearer $TOKEN"
fi

# 4. Analysis Endpoint
test_endpoint "Analysis" "POST" "$BASE_URL/api/analyze" \
    '{"prompt": "Test prompt",
      "selected_models": ["gpt-4", "claude-3"],
      "pattern": "gut",
      "ultra_model": "gpt-4"}' "200"

# 5. Mock Mode Test
export USE_MOCK=true
test_endpoint "Mock Analysis" "POST" "$BASE_URL/api/analyze" \
    '{"prompt": "Mock test",
      "selected_models": ["gpt-4-mock"],
      "pattern": "gut"}' "200"

# 6. Error Handling
test_endpoint "Invalid Request" "POST" "$BASE_URL/api/analyze" \
    '{"invalid": "data"}' "422"

# 7. Rate Limiting Test
print_header "Rate Limiting Test"
for i in {1..10}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/health")
    if [ "$response" = "429" ]; then
        echo -e "${GREEN}✅ PASS${NC}: Rate limiting working"
        PASS_COUNT=$((PASS_COUNT + 1))
        break
    fi
done
TEST_COUNT=$((TEST_COUNT + 1))

# 8. Frontend Static Files
test_endpoint "Frontend Index" "GET" "http://localhost:3009" "" "200"

# Print Summary
print_header "Test Summary"
echo "Total Tests: $TEST_COUNT"
echo "Passed: $PASS_COUNT"
echo "Failed: $((TEST_COUNT - PASS_COUNT))"

# Print detailed results
print_header "Detailed Results"
for result in "${TEST_RESULTS[@]}"; do
    if [[ $result == "PASS:"* ]]; then
        echo -e "${GREEN}$result${NC}"
    else
        echo -e "${RED}$result${NC}"
    fi
done

# Overall result
if [ $PASS_COUNT -eq $TEST_COUNT ]; then
    echo -e "\n${GREEN}✅ ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "\n${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi
