#!/bin/bash

# AICheck MCP Server Setup Script

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
MCP_SERVER_DIR="$PROJECT_DIR/.mcp/server"

echo "Setting up AICheck MCP server in $MCP_SERVER_DIR"

# Install dependencies
echo "Installing dependencies..."
cd "$MCP_SERVER_DIR" || exit
npm install

# Make the server executable
echo "Making the server executable..."
chmod +x "$MCP_SERVER_DIR/index.js"

# Check if Claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo "Claude CLI not found. Please ensure Claude Code is installed and available in PATH."
    echo "Visit https://claude.ai/code for installation instructions."
    exit 1
fi

# Register the MCP server with Claude
echo "Registering the MCP server with Claude..."
claude mcp add -s local -t stdio aicheck node "$MCP_SERVER_DIR/index.js"

echo "AICheck MCP server setup complete!"
echo
echo "You can now use AICheck governance tools with Claude."
echo "To verify the setup, run: claude mcp list"
