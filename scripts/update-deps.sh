#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting dependency security updates...${NC}"

# Function to update a package and record the result
update_package() {
  local package=$1
  echo -e "${YELLOW}Updating ${package}...${NC}"
  
  npm install --save $package@latest
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully updated ${package}${NC}"
    return 0
  else
    echo -e "${RED}✗ Failed to update ${package}${NC}"
    return 1
  fi
}

# Update dependencies with known vulnerabilities
update_package axios
update_package postcss
update_package react react-dom
update_package eslint
update_package tailwindcss
update_package @vitejs/plugin-react @vitejs/plugin-react-swc
update_package framer-motion
update_package lucide-react

# Additional packages that often have security issues
update_package @testing-library/react @testing-library/jest-dom

# Run npm audit to fix remaining issues
echo -e "\n${YELLOW}Running npm audit fix...${NC}"
npm audit fix

# Check for remaining vulnerabilities
echo -e "\n${YELLOW}Checking for remaining vulnerabilities...${NC}"
npm audit

echo -e "\n${GREEN}Dependency updates complete!${NC}"
echo -e "${YELLOW}Please review any remaining vulnerabilities and test your application.${NC}" 