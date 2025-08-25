#!/bin/bash
# Test script for P1 enhancements

echo "=== Testing P1 Enhancements ==="
echo

# Test 1: Auth endpoints protection
echo "1. Testing Auth Protection (Issue #33)"
echo "   Testing unprotected endpoint..."
curl -s http://localhost:8000/api/health | jq -r '.status' || echo "FAIL"

echo "   Testing protected endpoint without auth..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/admin/test)
if [ "$RESPONSE" = "401" ] || [ "$RESPONSE" = "403" ]; then
    echo "   ✅ Protected endpoint correctly requires auth"
else
    echo "   ❌ Protected endpoint returned: $RESPONSE"
fi

# Test 2: Rate limiting
echo
echo "2. Testing Rate Limiting (Issue #33)"
echo "   Sending 5 rapid requests..."
for i in {1..5}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/orchestrator/health)
    echo "   Request $i: $STATUS"
done

# Test 3: Circuit breaker simulation
echo
echo "3. Testing Circuit Breaker (Issue #35)"
echo "   Testing with invalid API key to trigger circuit breaker..."
export OPENAI_API_KEY="invalid-key"
curl -s -X POST http://localhost:8000/api/orchestrator/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "selected_models": ["gpt-4"]}' | jq -r '.status' || echo "Should handle gracefully"

# Test 4: Metrics endpoint
echo
echo "4. Testing Metrics Endpoint (Issue #37)"
curl -s http://localhost:8000/api/metrics | head -20 || echo "Metrics endpoint not available"

# Test 5: Secret scanning pre-commit
echo
echo "5. Testing Secret Scanning (Issue #34)"
echo "   Creating test file with fake secret..."
echo "aws_access_key_id=AKIAIOSFODNN7EXAMPLE" > test_secret.tmp
git add test_secret.tmp 2>/dev/null
if git commit -m "test" 2>&1 | grep -q "secret\|detect\|leak"; then
    echo "   ✅ Pre-commit hook detected secret"
else
    echo "   ❌ Pre-commit hook might not be installed"
fi
rm -f test_secret.tmp
git reset HEAD test_secret.tmp 2>/dev/null

echo
echo "=== P1 Enhancement Testing Complete ==="