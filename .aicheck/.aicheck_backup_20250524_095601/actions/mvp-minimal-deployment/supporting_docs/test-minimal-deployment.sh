#!/bin/bash

# Test script for MVP minimal deployment
# Tests all MVP functionality with minimal resources

echo "=== MVP Minimal Deployment Test ==="
echo "Starting test at $(date)"

# Set test environment
export ENV=development
export USE_MOCK=true
export DATABASE_URL=sqlite:///./test_ultra.db
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=test-secret-key
export JWT_SECRET_KEY=test-jwt-secret
export LOG_LEVEL=INFO

# Use minimal requirements
echo "Installing minimal requirements..."
pip install -r requirements-minimal.txt

# Start the minimal app
echo "Starting minimal app..."
cd /Users/joshuafield/Documents/Ultra
python -m backend.app_minimal &
APP_PID=$!

# Wait for startup
echo "Waiting for app to start..."
sleep 5

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4

    echo "Testing $method $endpoint..."

    if [ -z "$data" ]; then
        response=$(curl -s -X $method -w "\n%{http_code}" http://localhost:8000$endpoint)
    else
        response=$(curl -s -X $method -H "Content-Type: application/json" -d "$data" -w "\n%{http_code}" http://localhost:8000$endpoint)
    fi

    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "$expected_status" ]; then
        echo "✓ $endpoint returned $status_code"
    else
        echo "✗ $endpoint returned $status_code (expected $expected_status)"
        echo "Response: $response_body"
    fi

    echo ""
}

echo "=== Testing Health Check ==="
test_endpoint GET "/api/health" "" "200"

echo "=== Testing Root Endpoint ==="
test_endpoint GET "/" "" "200"

echo "=== Testing Authentication Endpoints ==="
# Test registration
register_data='{"email":"test@example.com","password":"SecurePass123!","name":"Test User"}'
test_endpoint POST "/api/auth/register" "$register_data" "200"

# Test login
login_data='{"email":"test@example.com","password":"SecurePass123!"}'
response=$(curl -s -X POST -H "Content-Type: application/json" -d "$login_data" http://localhost:8000/api/auth/login)
token=$(echo $response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$token" ]; then
    echo "✓ Login successful, got token"
else
    echo "✗ Login failed"
fi

echo "=== Testing LLM Endpoints ==="
test_endpoint GET "/api/available-models" "" "200"
test_endpoint GET "/api/llm/status" "" "200"
test_endpoint GET "/api/orchestrator/patterns" "" "200"

echo "=== Testing Analysis Endpoints ==="
analysis_data='{"prompt":"Test analysis","models":["mock"],"pattern":"summarize"}'
test_endpoint POST "/analyze" "$analysis_data" "200"

echo "=== Testing Document Upload ==="
# Create test file
echo "Test content" > test_doc.txt
# Test document upload with auth header
curl -s -X POST -H "Authorization: Bearer $token" -F "file=@test_doc.txt" http://localhost:8000/api/upload-document
rm test_doc.txt

echo "=== Testing Resource Usage ==="
test_endpoint GET "/api/internal/resources" "" "200"

echo "=== Testing Error Handling ==="
test_endpoint GET "/nonexistent" "" "404"
test_endpoint POST "/api/auth/login" '{"email":"wrong@example.com","password":"wrong"}' "401"

echo "=== Checking Resource Constraints ==="
# Check memory usage
ps aux | grep "python -m backend.app_minimal" | grep -v grep | awk '{print $6}'

# Kill the app
echo "Stopping app..."
kill $APP_PID

echo "=== Test Complete ==="
echo "Finished at $(date)"
