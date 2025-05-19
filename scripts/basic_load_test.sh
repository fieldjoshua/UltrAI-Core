#!/bin/bash

# Basic Load Test for Phase 2 Deployment
echo "Starting Basic Load Test"
echo "======================"
echo ""

BASE_URL="https://ultra-backend.onrender.com"
CONCURRENT=10
REQUESTS=50

echo "Testing $BASE_URL with $CONCURRENT concurrent requests ($REQUESTS total)"
echo ""

# Test root endpoint
echo "1. Testing root endpoint (/)"
ab -n $REQUESTS -c $CONCURRENT -k "$BASE_URL/" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Percentage|50%|90%|99%)"
echo ""

# Test health endpoint  
echo "2. Testing health endpoint (/health)"
ab -n $REQUESTS -c $CONCURRENT -k "$BASE_URL/health" 2>/dev/null | grep -E "(Requests per second|Time per request|Failed requests|Percentage|50%|90%|99%)"
echo ""

# Simple concurrent test with curl
echo "3. Concurrent curl test (10 requests)"
for i in {1..10}; do
  (time curl -s -o /dev/null "$BASE_URL/") &
done
wait
echo ""

echo "Load test complete!"