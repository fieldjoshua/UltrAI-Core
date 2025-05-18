#!/bin/bash

# Production Deployment Verification Script
# Tests auth, database, cache, and document management

API_URL="${API_URL:-https://ultrai-core.onrender.com}"
TEST_USER="testuser@example.com"
TEST_PASS="testpassword123"
TEST_USERNAME="testuser"

echo "Production Deployment Verification"
echo "================================"
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

# Test document creation
echo "Testing document creation..."
response=$(curl -s -X POST "$API_URL/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"test.txt\",\"content\":\"This is test content for the document.\"}")
echo "Response: $response"

# Extract document ID
DOC_ID=$(echo $response | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
echo "Document ID: $DOC_ID"
echo

# Test document listing
echo "Testing document listing..."
response=$(curl -s -X GET "$API_URL/documents" \
  -H "Authorization: Bearer $TOKEN")
echo "Response: $response"
echo

# Test document retrieval
echo "Testing document retrieval..."
response=$(curl -s -X GET "$API_URL/documents/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "Response: $response"
echo

# Test analysis creation (will test cache)
echo "Testing analysis creation..."
response=$(curl -s -X POST "$API_URL/analyses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":$DOC_ID,\"llm_provider\":\"openai\",\"prompt\":\"Summarize this document\"}")
echo "Response: $response"
echo

# Test analysis creation again (should be cached)
echo "Testing analysis creation (cached)..."
response=$(curl -s -X POST "$API_URL/analyses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":$DOC_ID,\"llm_provider\":\"openai\",\"prompt\":\"Summarize this document\"}")
echo "Response: $response"
echo

# Test analyses listing
echo "Testing analyses listing..."
response=$(curl -s -X GET "$API_URL/analyses/$DOC_ID" \
  -H "Authorization: Bearer $TOKEN")
echo "Response: $response"
echo

echo "Production verification complete!"