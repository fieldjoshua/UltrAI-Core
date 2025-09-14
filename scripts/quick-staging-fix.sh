#!/bin/bash

# Quick fix for staging - create minimal frontend structure
# This is a temporary workaround until proper build is configured

echo "🔧 Creating minimal frontend structure for staging..."

# Create the directories that the app expects
mkdir -p frontend/dist/assets

# Create a minimal index.html
cat > frontend/dist/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>UltraAI Staging API</title>
</head>
<body>
    <h1>UltraAI Staging Environment</h1>
    <p>API is running. Documentation available at:</p>
    <ul>
        <li><a href="/docs">API Documentation</a></li>
        <li><a href="/api/health">Health Check</a></li>
    </ul>
</body>
</html>
EOF

# Create empty assets directory
touch frontend/dist/assets/.gitkeep

# Commit the minimal structure
git add frontend/dist
git commit -m "Add minimal frontend structure for staging deployment"
git push

echo "✅ Minimal frontend structure created and pushed"
echo "🚀 This should allow staging to start while we configure proper builds"