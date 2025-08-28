#!/bin/bash
# Test script to verify environment variable in Render

echo "Testing environment variable detection..."
echo ""

# Test 1: Direct curl to check if HF is configured
echo "1. Checking API keys status:"
curl -s https://ultrai-core.onrender.com/api/models/api-keys-status | python3 -m json.tool | grep -A5 huggingface

echo ""
echo "2. Checking available models count (should be 26 if HF is working):"
curl -s https://ultrai-core.onrender.com/api/available-models | python3 -m json.tool | grep '"total_count"'

echo ""
echo "3. Checking if any HuggingFace models are available:"
curl -s https://ultrai-core.onrender.com/api/available-models | python3 -m json.tool | grep -c "huggingface" || echo "0 HuggingFace models found"

echo ""
echo "4. Testing providers summary:"
curl -s https://ultrai-core.onrender.com/api/models/providers-summary | python3 -m json.tool | grep -A2 huggingface | grep configured