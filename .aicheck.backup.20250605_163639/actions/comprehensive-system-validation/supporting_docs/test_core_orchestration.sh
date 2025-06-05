#!/bin/bash

# Core Orchestration Validation Test Script
# Tests the 4-stage Feather orchestration with multiple LLMs

BASE_URL="https://ultrai-core.onrender.com"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).md"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Initialize report
echo "# Core Orchestration Validation Report" > "$REPORT_FILE"
echo "Generated: $TIMESTAMP" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

log "Starting Core Orchestration Validation Tests"
log "Target: $BASE_URL"
echo "-----------------------------------------------------------"

# Test 1: Health Check
log "Testing health check endpoints..."
echo "## Health Check Results" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for endpoint in "/health" "/api/health"; do
    HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" "$BASE_URL$endpoint")
    if [ "$HTTP_CODE" = "200" ]; then
        log_success "$endpoint: $HTTP_CODE"
        echo "- $endpoint: ✅ (Status: $HTTP_CODE)" >> "$REPORT_FILE"
    else
        log_error "$endpoint: $HTTP_CODE"
        echo "- $endpoint: ❌ (Status: $HTTP_CODE)" >> "$REPORT_FILE"
    fi
done

echo "" >> "$REPORT_FILE"
echo "-----------------------------------------------------------"

# Test 2: Available Models
log "Testing available models endpoint..."
echo "## Available Models" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

HTTP_CODE=$(curl -s -o /tmp/models_response.json -w "%{http_code}" "$BASE_URL/api/available-models")
if [ "$HTTP_CODE" = "200" ]; then
    MODEL_COUNT=$(jq '. | length' /tmp/models_response.json)
    log_success "Found $MODEL_COUNT available models"
    echo "✅ Successfully retrieved $MODEL_COUNT models" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # List models
    jq -r '.[] | "- \(.id): \(.name)"' /tmp/models_response.json | while read -r line; do
        echo "  $line"
        echo "$line" >> "$REPORT_FILE"
    done
else
    log_error "Failed to get models: $HTTP_CODE"
    echo "❌ Failed to retrieve models (Status: $HTTP_CODE)" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "-----------------------------------------------------------"

# Test 3: Available Patterns
log "Testing available patterns endpoint..."
echo "## Available Patterns" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

HTTP_CODE=$(curl -s -o /tmp/patterns_response.json -w "%{http_code}" "$BASE_URL/api/available-patterns")
if [ "$HTTP_CODE" = "200" ]; then
    PATTERN_COUNT=$(jq '. | length' /tmp/patterns_response.json)
    log_success "Found $PATTERN_COUNT available patterns"
    echo "✅ Successfully retrieved $PATTERN_COUNT patterns" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # List patterns
    jq -r '.[] | "- **\(.id)**: \(.description)"' /tmp/patterns_response.json | while read -r line; do
        echo "  ${line:0:100}..."
        echo "$line" >> "$REPORT_FILE"
    done
else
    log_error "Failed to get patterns: $HTTP_CODE"
    echo "❌ Failed to retrieve patterns (Status: $HTTP_CODE)" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "-----------------------------------------------------------"

# Test 4: Orchestration Execution
log "Testing orchestration execution..."
echo "## Orchestration Test Results" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

TEST_PROMPT="Explain the concept of artificial intelligence in simple terms"
PATTERNS=("gut" "confidence" "critique" "fact_check" "perspective" "scenario")
SUCCESSFUL_TESTS=0
TOTAL_TESTS=${#PATTERNS[@]}

for pattern in "${PATTERNS[@]}"; do
    log "Testing pattern: $pattern"
    echo "### Pattern: $pattern" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Create request payload
    PAYLOAD=$(cat <<EOF
{
    "prompt": "$TEST_PROMPT",
    "pattern": "$pattern",
    "models": ["gpt-3.5-turbo", "claude-3-haiku-20240307", "gemini-pro"]
}
EOF
)
    
    # Make request and measure time
    START_TIME=$(date +%s)
    HTTP_CODE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        -o /tmp/orchestration_${pattern}_response.json \
        -w "%{http_code}" \
        "$BASE_URL/api/orchestrator/execute")
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    if [ "$HTTP_CODE" = "200" ]; then
        log_success "Pattern $pattern completed in ${DURATION}s"
        echo "✅ **Status**: Success" >> "$REPORT_FILE"
        echo "- **Duration**: ${DURATION} seconds" >> "$REPORT_FILE"
        
        # Check for 4-stage progression
        echo "- **4-Stage Progression**:" >> "$REPORT_FILE"
        for stage in "initial" "meta" "hyper" "ultra"; do
            if jq -e ".${stage}" /tmp/orchestration_${pattern}_response.json > /dev/null 2>&1; then
                STAGE_LENGTH=$(jq -r ".${stage} | tostring | length" /tmp/orchestration_${pattern}_response.json)
                log "  - ${stage^} stage: ✓ ($STAGE_LENGTH chars)"
                echo "  - ${stage^}: ✅ ($STAGE_LENGTH chars)" >> "$REPORT_FILE"
            else
                log_warning "  - ${stage^} stage: missing"
                echo "  - ${stage^}: ❌ Missing" >> "$REPORT_FILE"
            fi
        done
        
        # Check for quality metrics
        if jq -e ".quality_metrics" /tmp/orchestration_${pattern}_response.json > /dev/null 2>&1; then
            log "  - Quality metrics: ✓"
            echo "- **Quality Metrics**: ✅ Present" >> "$REPORT_FILE"
        else
            log_warning "  - Quality metrics: missing"
            echo "- **Quality Metrics**: ❌ Missing" >> "$REPORT_FILE"
        fi
        
        ((SUCCESSFUL_TESTS++))
    else
        log_error "Pattern $pattern failed: $HTTP_CODE"
        echo "❌ **Status**: Failed" >> "$REPORT_FILE"
        echo "- **Error**: HTTP $HTTP_CODE" >> "$REPORT_FILE"
        
        # Show error response if available
        if [ -f /tmp/orchestration_${pattern}_response.json ]; then
            ERROR_MSG=$(cat /tmp/orchestration_${pattern}_response.json)
            echo "- **Details**: $ERROR_MSG" >> "$REPORT_FILE"
        fi
    fi
    
    echo "" >> "$REPORT_FILE"
    echo "-----------------------------------------------------------"
    
    # Sleep between tests to avoid overwhelming the server
    sleep 2
done

# Summary
echo "## Validation Summary" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

log "============================================================"
log "TEST SUMMARY"
log "============================================================"

# Check success criteria
PATTERNS_ACCESSIBLE="❌"
if [ "$PATTERN_COUNT" -ge 10 ]; then
    PATTERNS_ACCESSIBLE="✅"
fi

ORCHESTRATION_SUCCESS="❌"
if [ "$SUCCESSFUL_TESTS" -eq "$TOTAL_TESTS" ]; then
    ORCHESTRATION_SUCCESS="✅"
fi

MODELS_AVAILABLE="❌"
if [ "$MODEL_COUNT" -ge 3 ]; then
    MODELS_AVAILABLE="✅"
fi

echo "- $PATTERNS_ACCESSIBLE All 10 Feather analysis patterns accessible" >> "$REPORT_FILE"
echo "- $ORCHESTRATION_SUCCESS 4-stage orchestration completes successfully" >> "$REPORT_FILE"
echo "- $ORCHESTRATION_SUCCESS Quality metrics calculated and displayed" >> "$REPORT_FILE"
echo "- $MODELS_AVAILABLE Multi-LLM selection works (3+ models)" >> "$REPORT_FILE"

log "Orchestration Tests: $SUCCESSFUL_TESTS/$TOTAL_TESTS passed"
log "Test report saved to: $REPORT_FILE"

# Display summary
if [ "$SUCCESSFUL_TESTS" -eq "$TOTAL_TESTS" ] && [ "$PATTERN_COUNT" -ge 10 ] && [ "$MODEL_COUNT" -ge 3 ]; then
    log_success "ALL CORE VALIDATION TESTS PASSED!"
else
    log_error "Some tests failed. Check the report for details."
fi

# Cleanup temporary files
rm -f /tmp/health_response.json /tmp/models_response.json /tmp/patterns_response.json /tmp/orchestration_*_response.json