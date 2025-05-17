#!/bin/bash
# Script to set the environment for Ultra

# Define usage function
usage() {
    echo "Usage: $0 [environment]"
    echo "Available environments: development, testing, production"
    echo "Examples:"
    echo "  $0 development  # Set up development environment"
    echo "  $0 testing      # Set up testing environment"
    echo "  $0 production   # Set up production environment"
    exit 1
}

# Check if an environment argument was provided
if [ -z "$1" ]; then
    usage
fi

ENVIRONMENT="$1"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_TEMPLATE="$PROJECT_ROOT/.env.$ENVIRONMENT"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"

# Check if the environment template exists
if [ ! -f "$ENV_TEMPLATE" ]; then
    echo "Error: Environment template for '$ENVIRONMENT' not found."
    echo "Expected file: $ENV_TEMPLATE"

    # Check if the example file exists
    if [ -f "$ENV_EXAMPLE" ]; then
        echo
        echo "Would you like to create a new environment file from the example? [y/N]"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "Creating $ENV_TEMPLATE from $ENV_EXAMPLE..."
            cp "$ENV_EXAMPLE" "$ENV_TEMPLATE"
            echo "Please edit $ENV_TEMPLATE to set appropriate values for your $ENVIRONMENT environment."
        else
            exit 1
        fi
    else
        exit 1
    fi
fi

# Create symlink to the environment file
if [ -f "$ENV_FILE" ]; then
    # If the file exists and is a symlink, remove it
    if [ -L "$ENV_FILE" ]; then
        rm "$ENV_FILE"
    else
        # If it's a regular file, backup it
        echo "Backing up existing .env file to .env.backup"
        mv "$ENV_FILE" "$ENV_FILE.backup"
    fi
fi

# Create symlink
ln -s "$ENV_TEMPLATE" "$ENV_FILE"

echo "Environment set to $ENVIRONMENT"
echo "Using environment file: $ENV_TEMPLATE"
echo

# Print some info about the environment
echo "Environment Settings:"
grep "^ENVIRONMENT=" "$ENV_FILE" || echo "ENVIRONMENT setting not found"
grep "^DEBUG=" "$ENV_FILE" || echo "DEBUG setting not found"
grep "^USE_MOCK=" "$ENV_FILE" || echo "USE_MOCK setting not found"

echo
echo "To run the application with this environment, use:"
echo "cd $PROJECT_ROOT && python -m backend.app"
