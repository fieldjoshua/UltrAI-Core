#!/bin/bash
# Test staging endpoints with correct paths

STAGING_URL="https://ultrai-staging-api.onrender.com"
echo "🧪 Testing Staging Endpoints: $STAGING_URL"
echo "📅 Test Date: $(date)"
echo "=========================================="

# 1. Health Check
echo -e "\n1. Health Check (/api/health)"
curl -s "$STAGING_URL/api/health" | python3 -m json.tool

# 2. Available Models
echo -e "\n2. Available Models (/api/available-models)"
curl -s "$STAGING_URL/api/available-models" | python3 -m json.tool | head -20

# 3. Model Health
echo -e "\n3. Model Health (/api/models/health)"
curl -s "$STAGING_URL/api/models/health" | python3 -m json.tool

# 4. API Keys Status
echo -e "\n4. API Keys Status (/api/models/api-keys-status)"
curl -s "$STAGING_URL/api/models/api-keys-status" | python3 -m json.tool

# 5. Model Providers Summary
echo -e "\n5. Model Providers Summary (/api/models/providers-summary)"
curl -s "$STAGING_URL/api/models/providers-summary" | python3 -m json.tool

# 6. Quick Check Models
echo -e "\n6. Quick Check Models (/api/models/quick-check)"
curl -s --max-time 30 "$STAGING_URL/api/models/quick-check" | python3 -m json.tool

# 7. Orchestrator Status (might timeout)
echo -e "\n7. Orchestrator Status (/api/orchestrator/status)"
curl -s --max-time 10 "$STAGING_URL/api/orchestrator/status" | python3 -m json.tool || echo "Status endpoint timed out"

# 8. Services Health
echo -e "\n8. Services Health (/api/health/services)"
curl -s "$STAGING_URL/api/health/services" | python3 -m json.tool

# 9. Test Auth Login (to get token for orchestrator)
echo -e "\n9. Test Auth Login (/api/auth/login)"
curl -s -X POST "$STAGING_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}' | python3 -m json.tool

echo -e "\n=========================================="
echo "✅ Test complete. Note: Orchestrator requires authentication."