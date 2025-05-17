#!/bin/bash

# Deploy script for Ultra Framework

echo "Preparing for deployment..."

# Create necessary files for Render
cat > render.yaml << EOL
services:
  - name: ultra-backend
    type: web
    env: python
    buildCommand: pip install -r requirements.txt && pip install -r backend/requirements.txt
    startCommand: cd backend && python main.py
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: GOOGLE_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: PORT
        value: 10000
EOL

# Create vercel.json
cat > vercel.json << EOL
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ],
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "environment": {
    "VITE_API_URL": "RENDER_BACKEND_URL_PLACEHOLDER"
  }
}
EOL

# Create a placeholder .env file for Vercel
cat > .env << EOL
VITE_API_URL=https://RENDER_BACKEND_URL_PLACEHOLDER
EOL

echo "Deployment files created. Next steps:"
echo "1. Create a Render account and deploy the backend"
echo "2. Update VITE_API_URL in .env and vercel.json with your Render URL"
echo "3. Create a Vercel account and deploy the frontend"
echo ""
echo "To deploy the backend to Render, go to render.com and:"
echo "- Select 'New Web Service'"
echo "- Connect your GitHub repository"
echo "- Follow the deployment instructions"
echo ""
echo "To deploy the frontend to Vercel, go to vercel.com and:"
echo "- Import your GitHub repository"
echo "- Configure with the settings in vercel.json"
echo "- Deploy the project"
