#!/bin/bash

# Phase 2 Deployment Verification Script
# Tests all endpoints and tracks deployment metrics

echo "Phase 2 Deployment Verification"
echo "=============================="
echo ""

# Set the base URL (update this with your actual Render URL)
BASE_URL="${1:-https://ultra-backend.onrender.com}"
echo "Testing URL: $BASE_URL"
echo ""

# Test root endpoint
echo "1. Testing root endpoint..."
curl -s "$BASE_URL/" | jq '.'
echo ""

# Test health endpoint
echo "2. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.'
echo ""

# Test database health endpoint
echo "3. Testing database health endpoint..."
curl -s "$BASE_URL/health/database" | jq '.'
echo ""

# Performance metrics
echo "4. Performance Metrics"
echo "====================="
echo ""

# Test response time
echo "Response time test (5 requests):"
for i in {1..5}; do
  time=$(curl -o /dev/null -s -w '%{time_total}' "$BASE_URL/health")
  echo "Request $i: ${time}s"
done
echo ""

# Test memory usage (if available through an endpoint)
echo "5. System Status"
echo "==============="
echo "Check Render dashboard for:"
echo "- Memory usage"
echo "- CPU usage"
echo "- Startup time"
echo "- Error logs"
echo ""

echo "Deployment verification complete!"
echo "================================"
