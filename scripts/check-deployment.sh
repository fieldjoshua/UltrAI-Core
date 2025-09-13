#!/bin/bash

# Check deployment status script
# Usage: ./scripts/check-deployment.sh [staging|production]

environment=${1:-production}

echo "🔍 Checking $environment deployment status..."
echo ""

if [ "$environment" = "staging" ]; then
    url="https://ultrai-staging-api.onrender.com"
elif [ "$environment" = "production" ]; then
    url="https://ultrai-core.onrender.com"
else
    echo "❌ Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Check health endpoint
echo "📡 Checking $url/api/health"
response=$(curl -s -w "\n%{http_code}" "$url/api/health" 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Service is healthy!"
    echo ""
    echo "Response:"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    echo "❌ Service returned status code: $http_code"
    echo "Response: $body"
fi

echo ""
echo "📊 Quick checks:"
echo -n "  Homepage: "
homepage_code=$(curl -s -o /dev/null -w "%{http_code}" "$url/" 2>/dev/null)
[ "$homepage_code" = "200" ] && echo "✅ OK" || echo "❌ Failed ($homepage_code)"

echo -n "  API Docs: "
docs_code=$(curl -s -o /dev/null -w "%{http_code}" "$url/docs" 2>/dev/null)
[ "$docs_code" = "200" ] && echo "✅ OK" || echo "❌ Failed ($docs_code)"

echo -n "  Models:   "
models_code=$(curl -s -o /dev/null -w "%{http_code}" "$url/api/models" 2>/dev/null)
[ "$models_code" = "200" ] && echo "✅ OK" || echo "❌ Failed ($models_code)"

echo ""
echo "🔗 URLs:"
echo "  Service: $url"
echo "  API Docs: $url/docs"
echo "  Health: $url/api/health"