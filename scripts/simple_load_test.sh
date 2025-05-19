#!/bin/bash

# Simple Load Test for Phase 2 Deployment
echo "Simple Load Test - Phase 2 Deployment"
echo "===================================="
echo ""

BASE_URL="https://ultra-backend.onrender.com"
REQUESTS=10

echo "Testing $BASE_URL with $REQUESTS sequential requests"
echo ""

# Test root endpoint
echo "1. Root endpoint (/) - Sequential requests:"
total_time=0
for i in $(seq 1 $REQUESTS); do
  response_time=$(curl -s -o /dev/null -w '%{time_total}' "$BASE_URL/")
  echo "Request $i: ${response_time}s"
  total_time=$(echo "$total_time + $response_time" | bc)
done
avg_time=$(echo "scale=3; $total_time / $REQUESTS" | bc)
echo "Average response time: ${avg_time}s"
echo ""

# Test concurrent requests
echo "2. Root endpoint (/) - Concurrent requests:"
for i in $(seq 1 $REQUESTS); do
  (
    response_time=$(curl -s -o /dev/null -w '%{time_total}' "$BASE_URL/")
    echo "Concurrent request $i: ${response_time}s"
  ) &
done
wait
echo ""

# Test health endpoint
echo "3. Health endpoint (/health) - Sequential requests:"
total_time=0
for i in $(seq 1 5); do
  response_time=$(curl -s -o /dev/null -w '%{time_total}' "$BASE_URL/health")
  echo "Request $i: ${response_time}s"
  total_time=$(echo "$total_time + $response_time" | bc)
done
avg_time=$(echo "scale=3; $total_time / 5" | bc)
echo "Average response time: ${avg_time}s"
echo ""

echo "Load test complete!"