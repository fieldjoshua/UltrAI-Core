#!/bin/bash
# Backend Cloud Deployment Script for Ultra AI

# Set colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===== Ultra AI Backend Cloud Deployment =====${NC}"
echo "This script will deploy your backend API to Vercel"
echo ""

# Use local Vercel CLI if available, otherwise install locally
if [ ! -f "../node_modules/.bin/vercel" ]; then
    echo -e "${RED}Vercel CLI not found.${NC} Installing locally..."
    cd .. && npm install --save-dev vercel && cd backend
fi

# Define the vercel command using local path
VERCEL="../node_modules/.bin/vercel"

# Generate requirements.txt if it doesn't exist or is empty
if [ ! -s "requirements.txt" ]; then
    echo -e "${BLUE}Generating requirements.txt...${NC}"
    pip freeze > requirements.txt
    echo -e "${GREEN}Generated requirements.txt successfully.${NC}"
fi

# Verify required files
if [ ! -f "main.py" ]; then
    echo -e "${RED}main.py not found. This file is required for deployment.${NC}"
    exit 1
fi

if [ ! -f "vercel.json" ]; then
    echo -e "${RED}vercel.json not found. This file is required for deployment.${NC}"
    exit 1
fi

# Deploy to Vercel
echo -e "${BLUE}Deploying backend to Vercel...${NC}"

# Check if this is a production deployment
read -p "Is this a production deployment? (y/n): " production
if [[ $production == "y" || $production == "Y" ]]; then
    $VERCEL --prod
else
    $VERCEL
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}Backend deployment failed. Please check the logs above.${NC}"
    exit 1
fi

echo -e "${GREEN}Backend deployment successful!${NC}"
echo ""
echo -e "${BLUE}===== Deployment Summary =====${NC}"
echo "Your backend API is now deployed to Vercel."
echo "You can access it at your Vercel project URL."
echo ""
echo "Important notes for backend deployment:"
echo "1. If using document storage, note that Vercel Functions are stateless."
echo "2. For production use with large files or persistent storage,"
echo "   consider integrating with cloud storage services."
echo ""
echo -e "${GREEN}Thank you for using Ultra AI!${NC}"