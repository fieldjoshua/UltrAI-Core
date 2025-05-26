#!/bin/bash
set -e

echo "Testing health endpoint..."
curl -s http://localhost:8086/api/health | jq || echo "Health check failed"

echo "Testing analyze endpoint..."
curl -s -X POST "http://localhost:8086/api/analyze" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Tell me a short story about a curious programmer",
  "selected_models": ["gpt4o"],
  "ultra_model": "gpt4o",
  "pattern": "comprehensive",
  "output_format": "markdown"
}' | cat || echo "Analyze endpoint failed"

echo "Done!"
