#!/bin/bash
# Deploy script with P1 features enabled

echo "=== Deploying with P1 Features Enabled ==="
echo

# Create .env file with P1 features
cat > .env << EOF
# P1 Features Enabled
ENVIRONMENT=production
ENABLE_AUTH=true
JWT_SECRET=VS/taiFzQPT/0b5/blhWyj9L9+W1LnMPdC796zl3ecI=
JWT_REFRESH_SECRET=DSMO8uNXMaY6DXPzSu3f50tmEmY8Jkn/qOXhNpxSSX0=
ENABLE_RATE_LIMIT=true
OTEL_ENABLED=true
CORS_ALLOWED_ORIGINS=https://ultrai-core.onrender.com
EOF

echo "✅ Created .env with P1 features enabled"

# Commit and push
echo
echo "Committing changes..."
git add .env scripts/deploy_with_p1.sh
git commit -m "Enable P1 features: Auth, Rate Limiting, and Telemetry

- Set ENABLE_AUTH=true for JWT/API key authentication
- Set ENABLE_RATE_LIMIT=true for tier-based rate limiting  
- Set OTEL_ENABLED=true for OpenTelemetry metrics
- Added secure JWT secrets
- Circuit breakers already active in resilient adapter

These features will activate when environment variables are set in production."

echo
echo "Pushing to trigger deployment..."
git push origin main

echo
echo "=== Deployment Triggered ==="
echo "Monitor at: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg"
echo
echo "⚠️  IMPORTANT: You still need to add these environment variables in Render:"
echo "1. Go to: https://dashboard.render.com/web/srv-cp2i4nmd3nmc73ceaphg/env"
echo "2. Add:"
echo "   ENABLE_AUTH=true"
echo "   JWT_SECRET=VS/taiFzQPT/0b5/blhWyj9L9+W1LnMPdC796zl3ecI="
echo "   JWT_REFRESH_SECRET=DSMO8uNXMaY6DXPzSu3f50tmEmY8Jkn/qOXhNpxSSX0="
echo "   ENABLE_RATE_LIMIT=true"
echo "   OTEL_ENABLED=true"
echo "3. Click 'Save Changes'"
echo
echo "Without setting these in Render, the features won't activate!"