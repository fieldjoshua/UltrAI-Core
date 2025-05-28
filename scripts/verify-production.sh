#!/bin/bash

# Production Verification Script
# Tests that sophisticated orchestrator code is actually running in production

set -e  # Exit on any error

# Configuration
PRODUCTION_URL="https://ultrai-core-4lut.onrender.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 UltraAI Production Verification${NC}"
echo "=================================="

# Function to print status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
CRITICAL_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local is_critical="${3:-false}"
    
    print_status "Testing: $test_name"
    
    if eval "$test_command"; then
        print_success "✅ $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        if [ "$is_critical" = "true" ]; then
            print_error "❌ $test_name (CRITICAL)"
            ((CRITICAL_FAILED++))
        else
            print_error "❌ $test_name"
        fi
        ((TESTS_FAILED++))
        return 1
    fi
}

# Basic connectivity test
print_status "Testing basic connectivity..."
run_test "Production URL accessible" \
    "curl -s --max-time 10 '$PRODUCTION_URL' > /dev/null" \
    true

# Health endpoint test
print_status "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/health" 2>/dev/null || echo "failed")
if [ "$HEALTH_RESPONSE" != "failed" ]; then
    print_success "✅ Health endpoint responding"
    echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
    ((TESTS_PASSED++))
else
    print_error "❌ Health endpoint failed (CRITICAL)"
    ((TESTS_FAILED++))
    ((CRITICAL_FAILED++))
fi

# OpenAPI documentation test
print_status "Testing OpenAPI documentation..."
OPENAPI_PATHS=$(curl -s --max-time 10 "$PRODUCTION_URL/openapi.json" | jq -r '.paths | keys[]' 2>/dev/null || echo "failed")
if [ "$OPENAPI_PATHS" != "failed" ]; then
    print_success "✅ OpenAPI documentation available"
    ENDPOINT_COUNT=$(echo "$OPENAPI_PATHS" | wc -l | tr -d ' ')
    print_status "Available endpoints: $ENDPOINT_COUNT"
    ((TESTS_PASSED++))
else
    print_error "❌ OpenAPI documentation failed"
    ((TESTS_FAILED++))
fi

# Sophisticated orchestrator endpoints test
print_status "Testing sophisticated orchestrator endpoints..."

# Test /api/orchestrator/models
MODELS_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/api/orchestrator/models" 2>/dev/null || echo "failed")
if [ "$MODELS_RESPONSE" != "failed" ] && [ "$MODELS_RESPONSE" != '{"detail":"Not Found"}' ]; then
    print_success "✅ Orchestrator models endpoint found"
    ((TESTS_PASSED++))
else
    print_error "❌ Orchestrator models endpoint missing (CRITICAL)"
    print_error "    This indicates antiquated code is running"
    ((TESTS_FAILED++))
    ((CRITICAL_FAILED++))
fi

# Test /api/orchestrator/patterns
PATTERNS_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/api/orchestrator/patterns" 2>/dev/null || echo "failed")
if [ "$PATTERNS_RESPONSE" != "failed" ] && [ "$PATTERNS_RESPONSE" != '{"detail":"Not Found"}' ]; then
    print_success "✅ Orchestrator patterns endpoint found"
    if [ "$PATTERNS_RESPONSE" != "failed" ]; then
        PATTERN_COUNT=$(echo "$PATTERNS_RESPONSE" | jq 'length' 2>/dev/null || echo "unknown")
        print_status "Available patterns: $PATTERN_COUNT"
    fi
    ((TESTS_PASSED++))
else
    print_error "❌ Orchestrator patterns endpoint missing (CRITICAL)"
    print_error "    This indicates antiquated code is running"
    ((TESTS_FAILED++))
    ((CRITICAL_FAILED++))
fi

# Test /api/orchestrator/feather
FEATHER_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/api/orchestrator/feather" 2>/dev/null || echo "failed")
if [ "$FEATHER_RESPONSE" != "failed" ] && [ "$FEATHER_RESPONSE" != '{"detail":"Not Found"}' ]; then
    print_success "✅ Feather orchestration endpoint found"
    ((TESTS_PASSED++))
else
    print_error "❌ Feather orchestration endpoint missing (CRITICAL)"
    print_error "    This indicates 4-stage Feather analysis is not available"
    ((TESTS_FAILED++))
    ((CRITICAL_FAILED++))
fi

# Test for antiquated endpoints
print_status "Checking for antiquated endpoints..."
ANTIQUATED_RESPONSE=$(curl -s --max-time 10 "$PRODUCTION_URL/api/orchestrator/execute" 2>/dev/null || echo "failed")
if [ "$ANTIQUATED_RESPONSE" != "failed" ] && [ "$ANTIQUATED_RESPONSE" != '{"detail":"Not Found"}' ]; then
    # If this exists but sophisticated endpoints don't, it's likely antiquated
    if [ "$MODELS_RESPONSE" = "failed" ] || [ "$MODELS_RESPONSE" = '{"detail":"Not Found"}' ]; then
        print_warning "⚠️  Found /api/orchestrator/execute but missing sophisticated endpoints"
        print_warning "    This suggests antiquated orchestrator code is running"
    else
        print_status "Both antiquated and sophisticated endpoints present"
    fi
else
    print_status "No antiquated endpoints detected"
fi

# Performance test
print_status "Testing response times..."
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$PRODUCTION_URL/health" 2>/dev/null || echo "failed")
if [ "$RESPONSE_TIME" != "failed" ]; then
    print_success "✅ Response time: ${RESPONSE_TIME}s"
    # Check if response time is reasonable (under 5 seconds)
    if (( $(echo "$RESPONSE_TIME < 5.0" | bc -l) )); then
        print_success "✅ Response time acceptable"
        ((TESTS_PASSED++))
    else
        print_warning "⚠️  Response time slow (>${RESPONSE_TIME}s)"
    fi
else
    print_error "❌ Response time test failed"
    ((TESTS_FAILED++))
fi

# Summary
echo ""
print_status "Verification Summary"
echo "===================="
echo "Production URL: $PRODUCTION_URL"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Critical Failures: $CRITICAL_FAILED"
echo "Timestamp: $(date)"
echo ""

if [ $CRITICAL_FAILED -eq 0 ]; then
    if [ $TESTS_FAILED -eq 0 ]; then
        print_success "🎉 ALL TESTS PASSED - Sophisticated orchestrator confirmed running"
    else
        print_warning "⚠️  MOSTLY SUCCESSFUL - Some non-critical issues found"
    fi
    echo ""
    print_success "✅ Production deployment verified"
    print_success "✅ Sophisticated UltraAI orchestrator is running"
    print_success "✅ 4-stage Feather analysis available"
    exit 0
else
    print_error "💥 CRITICAL FAILURES DETECTED"
    echo ""
    print_error "❌ Production deployment has issues"
    print_error "❌ Sophisticated orchestrator may not be running"
    print_error "❌ Possible antiquated code deployment"
    echo ""
    print_error "Recommended actions:"
    print_error "1. Check deployment logs"
    print_error "2. Verify latest code was deployed"
    print_error "3. Clear build cache and redeploy"
    print_error "4. Check environment variables"
    exit 1
fi