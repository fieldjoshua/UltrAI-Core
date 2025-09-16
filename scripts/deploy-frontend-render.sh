#!/bin/bash
# Script to deploy frontend services to Render
# Requires Render CLI: brew install render

echo "🚀 UltrAI Frontend Deployment Script"
echo "===================================="
echo ""
echo "This script will help you deploy the frontend services to Render."
echo "Make sure you have:"
echo "1. Render CLI installed (brew install render)"
echo "2. Logged into Render CLI (render login)"
echo ""

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found. Install with: brew install render"
    exit 1
fi

# Function to create a service
create_service() {
    local name=$1
    local branch=$2
    local env=$3
    
    echo "📦 Creating $name service..."
    
    # Create the service using the YAML file
    render up --file "render-frontend-${env}.yaml" --name "$name"
    
    if [ $? -eq 0 ]; then
        echo "✅ $name service created successfully!"
    else
        echo "❌ Failed to create $name service"
        echo "Manual steps:"
        echo "1. Go to https://dashboard.render.com"
        echo "2. Click 'New +' → 'Static Site'"
        echo "3. Connect GitHub repo: fieldjoshua/UltrAI-Core"
        echo "4. Service name: $name"
        echo "5. Branch: $branch"
        echo "6. Build Command: cd frontend && npm ci && npm run build"
        echo "7. Publish Directory: ./frontend/dist"
    fi
}

# Deploy staging frontend
echo "1️⃣ Deploying Staging Frontend"
create_service "ultrai-staging" "main" "staging"

echo ""
echo "2️⃣ To deploy Production Frontend (when ready):"
echo "   create_service 'ultrai-prod' 'production' 'production'"

echo ""
echo "📋 Next Steps:"
echo "1. Check deployment status at https://dashboard.render.com"
echo "2. Once deployed, test at https://staging-ultrai.onrender.com"
echo "3. Verify API connection works"
echo ""
echo "🔍 To check deployment status:"
echo "   render status ultrai-staging"