#\!/bin/bash

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Define usage function
usage() {
    echo -e "${YELLOW}Usage:${NC} $0 [environment]"
    echo ""
    echo "Toggles between development and production environments for Ultra framework."
    echo ""
    echo -e "${YELLOW}Available environments:${NC}"
    echo "  development - Use mock LLM services (for development and testing)"
    echo "  production  - Use real LLM API services (for production use)"
    echo "  status      - Show current environment settings"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 development  # Switch to development environment"
    echo "  $0 production   # Switch to production environment"
    echo "  $0 status       # Display current environment"
    echo ""
}

# Function to update environment file
update_env_file() {
    ENV_FILE="$1"
    ENVIRONMENT="$2"

    if [ \! -f "$ENV_FILE" ]; then
        echo -e "${RED}Error: Environment file $ENV_FILE does not exist.${NC}"
        echo "Please run ./scripts/set-env.sh [environment] first."
        exit 1
    fi

    if [ "$ENVIRONMENT" = "development" ]; then
        # Update to development environment
        sed -i.bak 's/^USE_MOCK=.*$/USE_MOCK=true/' "$ENV_FILE"
        sed -i.bak 's/^MOCK_MODE=.*$/MOCK_MODE=true/' "$ENV_FILE"
        sed -i.bak 's/^ENVIRONMENT=.*$/ENVIRONMENT=development/' "$ENV_FILE"
        echo -e "${GREEN}Updated $ENV_FILE to development environment${NC}"
    elif [ "$ENVIRONMENT" = "production" ]; then
        # Update to production environment
        sed -i.bak 's/^USE_MOCK=.*$/USE_MOCK=false/' "$ENV_FILE"
        sed -i.bak 's/^MOCK_MODE=.*$/MOCK_MODE=false/' "$ENV_FILE"
        sed -i.bak 's/^ENVIRONMENT=.*$/ENVIRONMENT=production/' "$ENV_FILE"
        echo -e "${GREEN}Updated $ENV_FILE to production environment${NC}"
    fi

    # Clean up backup file
    rm -f "${ENV_FILE}.bak"
}

# Function to check API keys for production environment
check_api_keys() {
    ENV_FILE="$1"

    local has_keys=false

    # Check for API keys in the environment file
    if grep -q "OPENAI_API_KEY=" "$ENV_FILE" && grep -v "OPENAI_API_KEY=\"\"" "$ENV_FILE" | grep -q "OPENAI_API_KEY="; then
        has_keys=true
    fi

    if grep -q "ANTHROPIC_API_KEY=" "$ENV_FILE" && grep -v "ANTHROPIC_API_KEY=\"\"" "$ENV_FILE" | grep -q "ANTHROPIC_API_KEY="; then
        has_keys=true
    fi

    if grep -q "GOOGLE_API_KEY=" "$ENV_FILE" && grep -v "GOOGLE_API_KEY=\"\"" "$ENV_FILE" | grep -q "GOOGLE_API_KEY="; then
        has_keys=true
    fi

    if [ "$has_keys" = false ]; then
        echo -e "${YELLOW}Warning: No API keys found in environment file.${NC}"
        echo -e "${YELLOW}For production environment operation, you need to add at least one API key to $ENV_FILE:${NC}"
        echo "  - OPENAI_API_KEY"
        echo "  - ANTHROPIC_API_KEY"
        echo "  - GOOGLE_API_KEY"
        return 1
    fi

    return 0
}

# Function to display current environment
show_status() {
    echo -e "${BLUE}Checking current Ultra environment configuration...${NC}"

    if [ -L ".env" ] && [ -f ".env" ]; then
        ENV_TARGET=$(readlink -f .env)
        echo -e "${BLUE}Active environment file: ${NC}$(basename "$ENV_TARGET")"
    elif [ -f ".env" ]; then
        echo -e "${BLUE}Active environment file: ${NC}.env (not a symlink)"
        ENV_TARGET=".env"
    else
        echo -e "${RED}Error: No active environment file found.${NC}"
        echo "Please run ./scripts/set-env.sh [environment] first."
        exit 1
    fi

    # Extract environment settings from the file
    ENV_TYPE=$(grep "^ENVIRONMENT=" "$ENV_TARGET" | cut -d= -f2 | tr -d '"')
    USE_MOCK=$(grep "^USE_MOCK=" "$ENV_TARGET" | cut -d= -f2 | tr -d '"')
    MOCK_MODE=$(grep "^MOCK_MODE=" "$ENV_TARGET" | cut -d= -f2 | tr -d '"')

    echo -e "${BLUE}Current settings:${NC}"
    echo "  ENVIRONMENT: $ENV_TYPE"
    echo "  USE_MOCK: $USE_MOCK"
    echo "  MOCK_MODE: $MOCK_MODE"

    if [ "$USE_MOCK" = "true" ] && [ "$MOCK_MODE" = "true" ]; then
        echo -e "${PURPLE}Ultra is currently configured for ${GREEN}DEVELOPMENT ENVIRONMENT${NC}"
    elif [ "$USE_MOCK" = "false" ] && [ "$MOCK_MODE" = "false" ]; then
        echo -e "${PURPLE}Ultra is currently configured for ${GREEN}PRODUCTION ENVIRONMENT${NC}"

        # Check if we have API keys
        check_api_keys "$ENV_TARGET"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Warning: Production environment is set but API keys may be missing.${NC}"
        fi
    else
        echo -e "${YELLOW}Ultra is in a mixed configuration state.${NC}"
        echo "For consistent behavior, both USE_MOCK and MOCK_MODE should be the same."
    fi
}

# Main logic
ENVIRONMENT="$1"

if [ -z "$ENVIRONMENT" ] || [ "$ENVIRONMENT" = "help" ] || [ "$ENVIRONMENT" = "--help" ]; then
    usage
    exit 0
fi

if [ "$ENVIRONMENT" = "status" ]; then
    show_status
    exit 0
fi

if [ "$ENVIRONMENT" \!= "development" ] && [ "$ENVIRONMENT" \!= "production" ]; then
    echo -e "${RED}Error: Invalid environment '$ENVIRONMENT'.${NC}"
    usage
    exit 1
fi

# Get the active environment file
if [ -L ".env" ] && [ -f ".env" ]; then
    ENV_FILE=$(readlink -f .env)
    echo -e "${BLUE}Found active environment file: ${NC}$(basename "$ENV_FILE")"
elif [ -f ".env" ]; then
    ENV_FILE=".env"
    echo -e "${BLUE}Found environment file: ${NC}.env (not a symlink)"
else
    echo -e "${RED}Error: No environment file found.${NC}"
    echo "Please run ./scripts/set-env.sh [environment] first."
    exit 1
fi

# Update the environment file
update_env_file "$ENV_FILE" "$ENVIRONMENT"

# Additional checks for production environment
if [ "$ENVIRONMENT" = "production" ]; then
    # Check for API keys
    check_api_keys "$ENV_FILE"
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Would you like to edit $ENV_FILE to add API keys? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            # Open the file in the default editor
            if [ -n "$EDITOR" ]; then
                $EDITOR "$ENV_FILE"
            elif command -v nano > /dev/null; then
                nano "$ENV_FILE"
            elif command -v vim > /dev/null; then
                vim "$ENV_FILE"
            else
                echo -e "${RED}No text editor found. Please edit $ENV_FILE manually.${NC}"
            fi

            # Re-check after edit
            check_api_keys "$ENV_FILE"
            if [ $? -ne 0 ]; then
                echo -e "${YELLOW}Warning: API keys still not detected. Ultra may not function correctly in production environment.${NC}"
            else
                echo -e "${GREEN}API keys detected. Ultra should now be ready for production operation.${NC}"
            fi
        fi
    else
        echo -e "${GREEN}API keys detected. Ultra should be ready for production operation.${NC}"
    fi
fi

echo -e "\n${GREEN}Ultra has been configured for ${ENVIRONMENT} environment\!${NC}"
if [ "$ENVIRONMENT" = "development" ]; then
    echo -e "${BLUE}The system will use mock LLM responses for development and testing.${NC}"
else
    echo -e "${BLUE}The system will connect to real LLM providers using configured API keys.${NC}"
fi

# Recommend restart
echo -e "\n${YELLOW}For changes to take effect, please restart any running Ultra services:${NC}"
echo "  1. Stop any running services (Ctrl+C)"
echo "  2. Start the backend: ./scripts/start-backend.sh"
echo "  3. Start the frontend: ./scripts/start-frontend.sh"
echo ""

exit 0
