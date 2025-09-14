#!/bin/bash
# Diagnose LLM service issues on staging

STAGING_URL="https://ultrai-staging-api.onrender.com"
echo "🔍 Diagnosing LLM Service Issues"
echo "================================"
echo "Time: $(date)"
echo ""

# 1. Check individual provider availability
echo "1. Checking Provider Availability..."
echo "-----------------------------------"
for provider in openai anthropic google huggingface; do
    echo -n "Provider $provider: "
    curl -s "$STAGING_URL/api/models/check-availability?providers=$provider" \
        --max-time 10 | python3 -m json.tool 2>/dev/null | grep -E "(available|error)" || echo "Failed/Timeout"
done

# 2. Get model recommendations (might reveal issues)
echo -e "\n2. Model Recommendations..."
echo "-----------------------------------"
curl -s "$STAGING_URL/api/models/recommendations" --max-time 10 | python3 -m json.tool 2>/dev/null || echo "Failed"

# 3. Check metrics for cache/performance issues
echo -e "\n3. Performance Metrics..."
echo "-----------------------------------"
curl -s "$STAGING_URL/api/metrics" --max-time 10 | grep -E "(cache|llm|response_time|error|timeout)" | head -20

# 4. Test quick model check with specific models
echo -e "\n4. Testing Specific Models..."
echo "-----------------------------------"
echo "Testing gpt-4o-mini:"
curl -s "$STAGING_URL/api/models/quick-check?models=gpt-4o-mini" --max-time 15 | python3 -m json.tool 2>/dev/null || echo "Failed"

echo -e "\nTesting claude-3-5-haiku-20241022:"
curl -s "$STAGING_URL/api/models/quick-check?models=claude-3-5-haiku-20241022" --max-time 15 | python3 -m json.tool 2>/dev/null || echo "Failed"

# 5. Check orchestrator health specifically
echo -e "\n5. Orchestrator Health..."
echo "-----------------------------------"
curl -s "$STAGING_URL/api/orchestrator/health" --max-time 10 | python3 -m json.tool 2>/dev/null || echo "Failed/Timeout"

# 6. Look for pattern in health check
echo -e "\n6. Detailed Health Analysis..."
echo "-----------------------------------"
health_response=$(curl -s "$STAGING_URL/api/health" --max-time 10)
echo "$health_response" | python3 -m json.tool 2>/dev/null

# Extract degraded services
echo -e "\nDegraded Services:"
echo "$health_response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for service in data.get('degraded_services', []):
        print(f'  - {service}')
    if 'services' in data:
        for svc, status in data['services'].items():
            if status != 'healthy':
                print(f'  - {svc}: {status}')
except: pass
"

echo -e "\n================================"
echo "✅ Diagnosis Complete"
echo ""
echo "Common Issues to Check in Logs:"
echo "1. Rate limiting (429 errors)"
echo "2. Timeout errors (slow provider responses)"
echo "3. Authentication failures (401 errors)"
echo "4. Model initialization failures"
echo "5. Health check threshold too strict"