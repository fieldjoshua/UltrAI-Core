#!/bin/bash
# Script to activate P1 features in production

echo "=== Activating P1 Features ==="
echo

# 1. Generate secure secrets
echo "1. Generating secure secrets..."
JWT_SECRET=$(openssl rand -base64 32)
JWT_REFRESH_SECRET=$(openssl rand -base64 32)

echo "JWT_SECRET=$JWT_SECRET"
echo "JWT_REFRESH_SECRET=$JWT_REFRESH_SECRET"
echo

# 2. Create render.yaml update
echo "2. Creating render.yaml with environment variables..."
cat > render_env_update.yaml << EOF
# Add these environment variables to your Render service
# Go to: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg/env

envVars:
  # Core Settings
  - key: ENVIRONMENT
    value: production
    
  # Authentication
  - key: ENABLE_AUTH
    value: "true"
  - key: JWT_SECRET
    generateValue: true  # Render will generate a secure value
  - key: JWT_REFRESH_SECRET
    generateValue: true
    
  # Rate Limiting
  - key: ENABLE_RATE_LIMIT
    value: "true"
    
  # OpenTelemetry
  - key: OTEL_ENABLED
    value: "true"
  - key: OTEL_SERVICE_NAME
    value: ultrai-core
    
  # Security
  - key: CORS_ALLOWED_ORIGINS
    value: https://ultrai-core.onrender.com
EOF

echo "3. Steps to activate in Render:"
echo "   a) Go to: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg/env"
echo "   b) Add these environment variables:"
echo "      - ENABLE_AUTH=true"
echo "      - JWT_SECRET=$JWT_SECRET"
echo "      - JWT_REFRESH_SECRET=$JWT_REFRESH_SECRET"
echo "      - ENABLE_RATE_LIMIT=true"
echo "      - OTEL_ENABLED=true"
echo "   c) Click 'Save Changes' - this will trigger a redeploy"
echo

echo "4. For full rate limiting, add Redis:"
echo "   a) Create a Redis instance on Render"
echo "   b) Or use Redis Cloud: https://app.redislabs.com"
echo "   c) Add REDIS_URL to environment variables"
echo

echo "5. Install pre-commit hooks locally:"
pre-commit --version > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   Installing pre-commit hooks..."
    pre-commit install
    echo "   ✅ Pre-commit hooks installed"
else
    echo "   ❌ pre-commit not found. Install with: pip install pre-commit"
fi

echo
echo "=== Next Steps ==="
echo "1. Go to Render dashboard and add the environment variables"
echo "2. Optional: Set up Redis for rate limiting"
echo "3. Optional: Configure OTLP endpoint for telemetry"
echo "4. Test with: curl https://ultrai-core.onrender.com/api/admin/test"
echo "   (Should return 401 Unauthorized after activation)"
echo

# Create a test script
cat > test_activation.sh << 'EOF'
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
EOF
chmod +x test_activation.sh

echo "Created test_activation.sh - run after deployment completes"