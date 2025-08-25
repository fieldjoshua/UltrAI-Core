#!/bin/bash
# Monitor P1 feature activation

echo "=== Monitoring P1 Feature Activation ==="
echo "Deployment URL: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg"
echo

# Function to check features
check_features() {
    echo "$(date '+%H:%M:%S') Checking features..."
    
    # 1. Auth protection
    AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://ultrai-core.onrender.com/api/admin/test)
    if [ "$AUTH_STATUS" = "401" ] || [ "$AUTH_STATUS" = "403" ]; then
        echo "  ✅ Auth: ACTIVE (returns $AUTH_STATUS)"
        AUTH_ACTIVE=true
    else
        echo "  ⏳ Auth: Not yet active (returns $AUTH_STATUS)"
        AUTH_ACTIVE=false
    fi
    
    # 2. Metrics endpoint
    if curl -s https://ultrai-core.onrender.com/api/metrics | grep -q "python_info"; then
        echo "  ✅ Metrics: ACTIVE"
        METRICS_ACTIVE=true
    else
        echo "  ⏳ Metrics: Not yet active"
        METRICS_ACTIVE=false
    fi
    
    # 3. Health check
    HEALTH=$(curl -s https://ultrai-core.onrender.com/health | jq -r '.status' 2>/dev/null || echo "error")
    echo "  📊 Health: $HEALTH"
    
    # Check if all features are active
    if [ "$AUTH_ACTIVE" = true ] && [ "$METRICS_ACTIVE" = true ]; then
        return 0
    else
        return 1
    fi
}

# Monitor loop
echo "Monitoring for P1 activation (checking every 30 seconds)..."
echo "Press Ctrl+C to stop"
echo

while true; do
    if check_features; then
        echo
        echo "🎉 P1 FEATURES ARE NOW ACTIVE!"
        echo
        echo "Test commands:"
        echo "  curl https://ultrai-core.onrender.com/api/admin/test"
        echo "  curl https://ultrai-core.onrender.com/api/metrics | head -20"
        echo
        break
    fi
    echo "  ⏳ Waiting 30 seconds before next check..."
    sleep 30
done