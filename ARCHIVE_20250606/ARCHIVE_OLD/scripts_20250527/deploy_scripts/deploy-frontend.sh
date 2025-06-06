#!/bin/bash

# Deploy frontend to Render

echo "=== Deploying UltraAI Frontend to Render ==="
echo

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Error: Render CLI not found. Please install it first:"
    echo "brew tap render-oss/render && brew install render"
    exit 1
fi

# Check if logged in
if ! render account -q &> /dev/null; then
    echo "Please login to Render first:"
    echo "Run: render login"
    exit 1
fi

# Ensure we're in the project root
if [ ! -f "render-frontend.yaml" ]; then
    echo "Error: render-frontend.yaml not found. Please run from project root."
    exit 1
fi

# Deploy using the frontend configuration
echo "Deploying frontend using render-frontend.yaml..."
render deploy -m render-frontend.yaml

echo
echo "=== Deployment Complete ==="
echo "Your frontend will be available at: https://ultrai-frontend.onrender.com"
echo "Backend API: https://ultrai-core.onrender.com"
echo
echo "Next steps:"
echo "1. Wait for deployment to complete (3-5 minutes)"
echo "2. Update backend CORS settings to allow frontend URL"
echo "3. Test the full application"