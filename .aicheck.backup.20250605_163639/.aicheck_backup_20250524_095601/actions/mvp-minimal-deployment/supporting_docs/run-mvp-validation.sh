#!/bin/bash

# MVP Validation Test Runner
# Runs all tests to validate minimal deployment has ALL MVP features

echo "==================================="
echo "MVP MINIMAL DEPLOYMENT VALIDATION"
echo "==================================="
echo "Started at: $(date)"

# Set test environment
export ENV=testing
export USE_MOCK=true
export DATABASE_URL=sqlite:///./test_mvp.db
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=mvp-test-key
export JWT_SECRET_KEY=mvp-jwt-test

# Default URLs (can be overridden)
BACKEND_URL=${1:-http://localhost:8000}
FRONTEND_URL=${2:-http://localhost:3000}

echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Function to run a test and check result
run_test() {
    local test_name=$1
    local test_command=$2

    echo "Running: $test_name"
    echo "----------------------------------------"

    if $test_command; then
        echo "✓ $test_name PASSED"
        return 0
    else
        echo "✗ $test_name FAILED"
        return 1
    fi
    echo ""
}

# Track test results
PASSED=0
FAILED=0

# 1. Basic connectivity tests
echo "=== CONNECTIVITY TESTS ==="
run_test "Backend Health Check" "curl -s $BACKEND_URL/api/health | grep -q '\"status\"'"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

run_test "Frontend Load Test" "curl -s $FRONTEND_URL | grep -q '<html'"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

# 2. Run Python MVP tests
echo -e "\n=== MVP FEATURE TESTS ==="
run_test "MVPMinimal Tests" "python mvp-minimal-tests.py"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

# 3. Run resource monitoring tests
echo -e "\n=== RESOURCE MONITORING TESTS ==="
run_test "Resource Monitoring" "python resource-monitoring-test.py"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

# 4. Run frontend tests (if Selenium is available)
echo -e "\n=== FRONTEND TESTS ==="
if command -v chromedriver &> /dev/null; then
    run_test "Frontend UI Tests" "python frontend-tests.py"
    if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi
else
    echo "⚠️  Skipping frontend tests (chromedriver not found)"
fi

# 5. Run complete MVP validation
echo -e "\n=== COMPLETE MVP VALIDATION ==="
run_test "Complete MVP Validation" "python complete-mvp-validation-test.py $BACKEND_URL $FRONTEND_URL"
if [ $? -eq 0 ]; then PASSED=$((PASSED+1)); else FAILED=$((FAILED+1)); fi

# 6. Performance checks
echo -e "\n=== PERFORMANCE CHECKS ==="

# Memory usage check
echo "Checking memory usage..."
MEMORY_MB=$(ps aux | grep -E "(python|node)" | grep -v grep | awk '{sum += $6} END {print sum/1024}')
echo "Total memory usage: ${MEMORY_MB}MB"
if (( $(echo "$MEMORY_MB < 512" | bc -l) )); then
    echo "✓ Memory usage under 512MB limit"
    PASSED=$((PASSED+1))
else
    echo "✗ Memory usage exceeds 512MB limit"
    FAILED=$((FAILED+1))
fi

# Response time check
echo -e "\nChecking response times..."
START_TIME=$(date +%s.%N)
curl -s $BACKEND_URL/api/health > /dev/null
END_TIME=$(date +%s.%N)
RESPONSE_TIME=$(echo "$END_TIME - $START_TIME" | bc)

echo "Health check response time: ${RESPONSE_TIME}s"
if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
    echo "✓ Response time acceptable"
    PASSED=$((PASSED+1))
else
    echo "✗ Response time too slow"
    FAILED=$((FAILED+1))
fi

# 7. Critical endpoint checks
echo -e "\n=== CRITICAL ENDPOINT CHECKS ==="

# Check each critical endpoint
ENDPOINTS=(
    "/api/auth/login:POST"
    "/api/available-models:GET"
    "/api/orchestrator/patterns:GET"
    "/api/analyze:POST"
    "/analyze:GET"
    "/documents:GET"
)

for endpoint_method in "${ENDPOINTS[@]}"; do
    endpoint="${endpoint_method%:*}"
    method="${endpoint_method#*:}"

    if [[ "$endpoint" == /api/* ]]; then
        url="$BACKEND_URL$endpoint"
    else
        url="$FRONTEND_URL$endpoint"
    fi

    echo "Testing $method $endpoint..."

    if [ "$method" == "GET" ]; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" $url)
    else
        # For POST endpoints, send minimal data
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"test": true}' $url)
    fi

    if [[ "$STATUS" -eq 200 || "$STATUS" -eq 201 || "$STATUS" -eq 401 || "$STATUS" -eq 422 ]]; then
        echo "✓ $endpoint returned $STATUS"
        PASSED=$((PASSED+1))
    else
        echo "✗ $endpoint returned $STATUS"
        FAILED=$((FAILED+1))
    fi
done

# Summary
echo -e "\n==================================="
echo "TEST SUMMARY"
echo "==================================="
echo "Total Tests: $((PASSED + FAILED))"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Success Rate: $(( PASSED * 100 / (PASSED + FAILED) ))%"
echo ""
echo "Completed at: $(date)"

# Exit with appropriate code
if [ $FAILED -eq 0 ]; then
    echo -e "\n✓ ALL MVP FEATURES VALIDATED SUCCESSFULLY!"
    exit 0
else
    echo -e "\n✗ Some MVP features are not working properly"
    exit 1
fi
