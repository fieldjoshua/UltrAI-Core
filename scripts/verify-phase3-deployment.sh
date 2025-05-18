#!/bin/bash

# Phase 3 Deployment Verification Script
# Tests authentication functionality

API_URL="${API_URL:-https://ultra-backend.onrender.com}"
TEST_USER="testuser@example.com"
TEST_PASS="testpassword123"
TEST_USERNAME="testuser"

echo "Phase 3 Deployment Verification"
echo "==============================="
echo "API URL: $API_URL"
echo

# Test root endpoint
echo "Testing root endpoint..."
response=$(curl -s "$API_URL/")
echo "Response: $response"
echo

# Test health endpoint
echo "Testing health endpoint..."
response=$(curl -s "$API_URL/health")
echo "Response: $response"
echo

# Test database health
echo "Testing database health..."
response=$(curl -s "$API_URL/health/database")
echo "Response: $response"
echo

# Test user registration
echo "Testing user registration..."
response=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_USER\",\"password\":\"$TEST_PASS\",\"username\":\"$TEST_USERNAME\"}")
echo "Response: $response"
echo

# Test user login
echo "Testing user login..."
response=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_USER\",\"password\":\"$TEST_PASS\"}")
echo "Response: $response"

# Extract token from response
TOKEN=$(echo $response | grep -o '"access_token":"[^"]*' | grep -o '[^"]*$')
echo "Token extracted: ${TOKEN:0:20}..."
echo

# Test auth verification
echo "Testing auth verification..."
response=$(curl -s -X GET "$API_URL/auth/verify" \
  -H "Authorization: Bearer $TOKEN")
echo "Response: $response"
echo

# Test protected endpoint
echo "Testing protected endpoint..."
response=$(curl -s -X GET "$API_URL/protected" \
  -H "Authorization: Bearer $TOKEN")
echo "Response: $response"
echo

# Test invalid token  # nosec
echo "Testing invalid token..."
INVALID_TOKEN="invalid-token"
response=$(curl -s -X GET "$API_URL/protected" \
  -H "Authorization: Bearer $INVALID_TOKEN")
echo "Response: $response"
echo

echo "Phase 3 verification complete!"
