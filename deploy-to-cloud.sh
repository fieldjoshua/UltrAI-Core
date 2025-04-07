#!/bin/bash
# Cloud Deployment Script for Ultra AI

# Set colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Ultra AI Cloud Deployment =====${NC}"
echo "This script will deploy your application to Vercel"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}Vercel CLI not found.${NC} Installing..."
    npm install -g vercel
fi

# Build the frontend application
echo -e "${BLUE}Building frontend application...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}Frontend build failed. Aborting deployment.${NC}"
    exit 1
fi
echo -e "${GREEN}Frontend build successful.${NC}"

# Deploy to Vercel
echo -e "${BLUE}Deploying to Vercel...${NC}"

# Check if this is a production deployment
read -p "Is this a production deployment? (y/n): " production
if [[ $production == "y" || $production == "Y" ]]; then
    vercel --prod
else
    vercel
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}Deployment failed. Please check the logs above.${NC}"
    exit 1
fi

echo -e "${GREEN}Deployment successful!${NC}"
echo ""
echo -e "${BLUE}===== Deployment Summary =====${NC}"
echo "Your application is now deployed to Vercel."
echo "You can access it at your Vercel project URL."
echo ""
echo "If you need to make changes to the backend API URL, edit the VITE_API_URL"
echo "environment variable in your Vercel project settings or update the vercel.json file."
echo ""
echo -e "${GREEN}Thank you for using Ultra AI!${NC}"