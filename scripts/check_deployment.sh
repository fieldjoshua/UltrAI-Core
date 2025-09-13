#!/bin/bash
# Check deployment status

echo "=== Checking UltraAI Deployment Status ==="
echo

# Check dev environment
echo "1. Checking DEV environment..."
echo "   URL: https://ultrai-core.onrender.com"
echo

echo "   Health check:"
curl -s https://ultrai-core.onrender.com/health | jq . || echo "Failed to connect"
echo

echo "   Orchestrator status:"
curl -s https://ultrai-core.onrender.com/api/orchestrator/status | jq . || echo "Failed to get status"
echo

echo "   Available models:"
curl -s https://ultrai-core.onrender.com/api/models | jq . || echo "Failed to get models"
echo

# Test orchestration
echo "2. Testing orchestration endpoint..."
curl -X POST https://ultrai-core.onrender.com/api/orchestrator/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"query": "What is 2+2?"}' \
  -s | jq . || echo "Orchestration test failed"
echo

echo "=== Deployment Check Complete ==="