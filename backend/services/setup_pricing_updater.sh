#!/bin/bash
# UltraAI Pricing Updater Setup Script
# This script installs all required dependencies for the pricing updater
# and fixes common dependency issues

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up UltraAI Pricing Updater...${NC}"

# Check if running in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo -e "${YELLOW}Warning: It's recommended to run this in a Python virtual environment${NC}"
  echo -e "If you want to create one, run: ${GREEN}python -m venv .venv && source .venv/bin/activate${NC}"
  echo ""
  read -p "Continue without virtual environment? (y/n) " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Setup aborted${NC}"
    exit 1
  fi
fi

# Create the pricing_history directory if it doesn't exist
echo -e "\nCreating pricing history directory..."
mkdir -p backend/pricing_history

# Install core dependencies first
echo -e "\n${GREEN}Installing core dependencies...${NC}"
pip install six python-dateutil pytz requests
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to install core dependencies${NC}"
  exit 1
fi

# Install all requirements
echo -e "\n${GREEN}Installing all dependencies from requirements file...${NC}"
pip install -r backend/pricing_updater_requirements.txt --upgrade
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to install dependencies from requirements file${NC}"

  # Try fixing specific six.moves error
  echo -e "\n${YELLOW}Attempting to fix 'six.moves' dependency issue...${NC}"
  pip install six --upgrade
  pip install python-dateutil --upgrade
  pip install pandas --upgrade

  # Try again with requirements
  echo -e "\n${GREEN}Retrying installation...${NC}"
  pip install -r backend/pricing_updater_requirements.txt --upgrade
  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Please try manually:${NC}"
    echo "pip install six python-dateutil pytz pandas requests beautifulsoup4 lxml email-validator"
    exit 1
  fi
fi

# Test imports
echo -e "\n${GREEN}Testing imports...${NC}"
python -c "
try:
    import pandas as pd
    from bs4 import BeautifulSoup
    import requests
    import six.moves
    print('All imports successful!')
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
  echo -e "${RED}Import test failed. Some dependencies may still be missing.${NC}"
  exit 1
fi

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "You can now run the pricing updater with: ${YELLOW}python backend/pricing_updater.py${NC}"
echo -e "For a dry run (no changes): ${YELLOW}python backend/pricing_updater.py --dry-run${NC}"
echo ""
echo -e "${GREEN}See documentation/logic/backend_README_PRICING_UPDATER.md for more information.${NC}"