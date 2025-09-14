#!/bin/bash

echo "Setting up Claude Desktop config for Render MCP..."

# Create .claude directory if it doesn't exist
mkdir -p ~/.claude

# Copy the config file
cp /Users/joshuafield/Documents/Ultra/claude_desktop_config_example.json ~/.claude/claude_desktop_config.json

echo "✅ Config file copied to ~/.claude/claude_desktop_config.json"
echo ""
echo "Next steps:"
echo "1. Quit Claude Desktop completely (Cmd+Q)"
echo "2. Reopen Claude Desktop"
echo "3. Return to your chat"
echo "4. Render MCP tools should be available!"