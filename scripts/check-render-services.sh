#!/bin/bash

echo "=== Checking Render Services ==="
echo ""

# Services to check
services=(
    "ultrai-core.onrender.com"
    "ultrai-staging-api.onrender.com"
    "ultrai-prod-api.onrender.com"
)

for service in "${services[@]}"; do
    echo "Checking: https://$service"
    
    # Check if service exists
    response=$(curl -s -o /dev/null -w "%{http_code}" -I "https://$service/api/health" 2>/dev/null)
    
    if [ "$response" != "000" ]; then
        echo "  Status Code: $response"
        
        # Get actual health check
        health=$(curl -s "https://$service/api/health" 2>/dev/null | jq -r '.status' 2>/dev/null || echo "N/A")
        echo "  Health Status: $health"
        
        # Get environment
        env=$(curl -s "https://$service/api/health" 2>/dev/null | jq -r '.environment' 2>/dev/null || echo "N/A")
        echo "  Environment: $env"
    else
        echo "  Status: NOT FOUND or NOT ACCESSIBLE"
    fi
    echo ""
done

echo "=== CSP Header Analysis ==="
echo ""
csp=$(curl -sI "https://ultrai-core.onrender.com/" | grep -i "content-security-policy" | cut -d' ' -f2-)
echo "Current CSP allows connections to:"
echo "$csp" | grep -o 'https://[^ ;]*' | sort | uniq