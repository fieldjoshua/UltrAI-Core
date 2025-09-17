#!/bin/bash
# Test script for orchestration analysis using curl
# This shows the exact HTTP implementation of the orchestration pipeline

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
AUTH_TOKEN=${AUTH_TOKEN:-""}  # Set if authentication is required

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print steps
print_step() {
    echo -e "\n${BLUE}${"="*80}${NC}"
    echo -e "${GREEN}📍 STEP $1: $2${NC}"
    echo -e "${BLUE}${"="*80}${NC}"
}

# Function to make authenticated request
make_request() {
    local endpoint=$1
    local data=$2
    local auth_header=""
    
    if [ -n "$AUTH_TOKEN" ]; then
        auth_header="-H \"Authorization: Bearer $AUTH_TOKEN\""
    fi
    
    curl -s -X POST \
        -H "Content-Type: application/json" \
        $auth_header \
        -d "$data" \
        "$API_URL$endpoint"
}

# Test queries
echo -e "${GREEN}🚀 UltrAI Orchestration Analysis Test${NC}"
echo "====================================="
echo "Testing endpoint: $API_URL/api/orchestrator/analyze"
echo ""

# Select query
echo "Test queries:"
echo "1. What is 2+2?"
echo "2. Explain quantum entanglement"
echo "3. Write a Python function to sort a list"
echo "4. What are the causes of climate change?"
echo "5. How do I start a small business?"
echo ""
read -p "Select a query (1-5) or enter your own: " choice

case $choice in
    1) USER_INPUT="What is 2+2?" ;;
    2) USER_INPUT="Explain quantum entanglement" ;;
    3) USER_INPUT="Write a Python function to sort a list" ;;
    4) USER_INPUT="What are the causes of climate change?" ;;
    5) USER_INPUT="How do I start a small business?" ;;
    *) USER_INPUT="$choice" ;;
esac

echo -e "\n${YELLOW}Selected query: $USER_INPUT${NC}"

# Step 1.1: Prepare request
print_step "1.1" "Preparing Request"
REQUEST_DATA=$(cat <<EOF
{
    "query": "$USER_INPUT",
    "analysis_type": "general",
    "include_pipeline_details": true,
    "include_initial_responses": true,
    "save_outputs": false
}
EOF
)
echo "Request body:"
echo "$REQUEST_DATA" | jq .

# Step 1.2: Send request
print_step "1.2" "Sending Request to Orchestration Service"
echo "POST $API_URL/api/orchestrator/analyze"

# Make the request and save response
RESPONSE=$(make_request "/api/orchestrator/analyze" "$REQUEST_DATA")

# Check if request succeeded
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Request failed${NC}"
    exit 1
fi

# Parse response
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Analysis failed:${NC}"
    echo "$RESPONSE" | jq .
    exit 1
fi

# Step 1.3-1.5: Show Initial Response Stage
print_step "1.3-1.5" "Initial Response Stage"
echo "$RESPONSE" | jq '.results.initial_response.output | {
    models_attempted: .models_attempted,
    successful_models: .successful_models,
    response_count: .response_count,
    prompt: .prompt
}'

# Show model responses
echo -e "\n${GREEN}Individual Model Responses:${NC}"
echo "$RESPONSE" | jq -r '.results.initial_response.output.responses | to_entries[] | 
    "Model: \(.key)\nResponse: \(.value | .[0:200])...\n"'

# Step 2: Peer Review Stage
print_step "2" "Peer Review Stage"
PEER_SKIPPED=$(echo "$RESPONSE" | jq -r '.results.peer_review_and_revision.output.skipped // false')
if [ "$PEER_SKIPPED" = "true" ]; then
    echo -e "${YELLOW}⚠️  Peer review was skipped${NC}"
    echo "$RESPONSE" | jq '.results.peer_review_and_revision.output.reason'
else
    echo "Peer review completed - models reviewed each other's responses"
fi

# Step 3: Ultra Synthesis
print_step "3" "Ultra Synthesis Result"
echo -e "${GREEN}Synthesis Preview:${NC}"
echo "$RESPONSE" | jq -r '.results.ultra_synthesis | 
    if type == "string" then . else .synthesis // . end | .[0:500]'

# Pipeline Summary
print_step "FINAL" "Pipeline Summary"
echo "$RESPONSE" | jq '{
    processing_time: .processing_time,
    pipeline_info: .pipeline_info
}'

# Save full response for inspection
OUTPUT_FILE="orchestration_response_$(date +%Y%m%d_%H%M%S).json"
echo "$RESPONSE" | jq . > "$OUTPUT_FILE"
echo -e "\n${GREEN}✅ Full response saved to: $OUTPUT_FILE${NC}"

# Show SSE events URL
CORRELATION_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
echo -e "\n${BLUE}📊 For real-time events, use:${NC}"
echo "curl -N $API_URL/api/orchestrator/events?correlation_id=$CORRELATION_ID"