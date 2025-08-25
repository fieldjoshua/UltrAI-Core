#!/bin/bash
# Test if P1 features are activated

echo "Testing P1 activation..."

# 1. Test protected endpoint
echo -n "Auth protection: "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://ultrai-core.onrender.com/api/admin/test)
if [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ]; then
    echo "✅ Active (returned $STATUS)"
else
    echo "❌ Not active (returned $STATUS)"
fi

# 2. Test metrics
echo -n "Metrics endpoint: "
curl -s https://ultrai-core.onrender.com/api/metrics | grep -q "python_info" && echo "✅ Active" || echo "❌ Not found"

# 3. Check health
echo -n "Server health: "
curl -s https://ultrai-core.onrender.com/health | jq -r '.status'
