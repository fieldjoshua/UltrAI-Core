#!/bin/bash
# Ultra MVP Setup Script
# This script prepares the environment for running Ultra MVP

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Print header
echo -e "\n${BOLD}====== Ultra MVP Setup ======${RESET}\n"

# Check for required commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is required but not installed.${RESET}"
        echo "Please install $1 and try again."
        exit 1
    fi
}

echo -e "${BOLD}Checking requirements...${RESET}"
check_command python3
check_command pip
check_command npm
echo -e "${GREEN}All required commands are available.${RESET}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\n${BOLD}Creating .env file from template...${RESET}"
    if [ -f env.example ]; then
        cp env.example .env
        echo -e "${GREEN}Created .env file. Please edit it with your API keys.${RESET}"
    else
        echo -e "${RED}Error: env.example file not found.${RESET}"
        exit 1
    fi
else
    echo -e "\n${YELLOW}.env file already exists. Keeping existing file.${RESET}"
    echo "If you need to reset your environment variables, delete .env and run this script again."
fi

# Create Python virtual environment
echo -e "\n${BOLD}Setting up Python virtual environment...${RESET}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}Created virtual environment at .venv${RESET}"
else
    echo -e "${YELLOW}Virtual environment already exists at .venv${RESET}"
fi

# Activate virtual environment
echo -e "\n${BOLD}Activating virtual environment...${RESET}"
source .venv/bin/activate

# Install backend dependencies
echo -e "\n${BOLD}Installing backend dependencies...${RESET}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}Backend dependencies installed successfully.${RESET}"
else
    echo -e "${RED}Warning: requirements.txt not found.${RESET}"
    echo "Creating minimal requirements.txt"
    cat > requirements.txt << EOF
fastapi>=0.95.0
uvicorn>=0.21.1
python-dotenv>=1.0.0
httpx>=0.24.0
pydantic>=2.0.0
tenacity>=8.2.2
openai>=1.1.0
google-generativeai>=0.3.0
requests>=2.28.2
EOF
    pip install -r requirements.txt
    echo -e "${GREEN}Created and installed minimal requirements.${RESET}"
fi

# Install frontend dependencies
if [ -d "frontend" ]; then
    echo -e "\n${BOLD}Installing frontend dependencies...${RESET}"
    cd frontend
    npm install
    echo -e "${GREEN}Frontend dependencies installed successfully.${RESET}"
    cd ..
else
    echo -e "\n${YELLOW}Warning: frontend directory not found.${RESET}"
    echo "Frontend dependencies will not be installed."
fi

# Create necessary directories
echo -e "\n${BOLD}Creating necessary directories...${RESET}"
mkdir -p src/core
mkdir -p src/models
mkdir -p src/utils
mkdir -p logs

# Complete
echo -e "\n${BOLD}${GREEN}Setup complete!${RESET}\n"
echo -e "To start working with Ultra MVP:"
echo -e "1. Edit the ${BOLD}.env${RESET} file and add your API keys"
echo -e "2. Activate the virtual environment: ${BOLD}source .venv/bin/activate${RESET}"
echo -e "3. Run the test script: ${BOLD}python scripts/test_llm_connections.py${RESET}"
echo -e "4. Start the application: ${BOLD}./scripts/run.sh${RESET} (when available)\n"

# Make the script executable
chmod +x scripts/setup.sh
