#!/bin/bash

# AICheck v6.0.0 Claude Integration Activator
# This script sets up MCP server integration for Claude Code

echo "🔌 Activating AICheck v6.0.0 for Claude Code..."

# Detect Claude config location
CLAUDE_CONFIG=""
if [ -f "$HOME/.claude/claude_desktop_config.json" ]; then
    CLAUDE_CONFIG="$HOME/.claude/claude_desktop_config.json"
elif [ -f "$HOME/.config/claude/claude_desktop_config.json" ]; then
    CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"
else
    echo "Claude config not found. Please configure manually."
    echo "Add this to your Claude config:"
    echo "{"
    echo "  \"mcpServers\": {"
    echo "    \"aicheck-ultra\": {"
    echo "      \"command\": \"node\","
    echo "      \"args\": [\"$(pwd)/.mcp/server/index.js\"]"
    echo "    }"
    echo "  }"
    echo "}"
    exit 1
fi

echo "Found Claude config: $CLAUDE_CONFIG"

# Use Python to safely update JSON config
python3 -c "
import json
import sys
import os

config_file = '$CLAUDE_CONFIG'
project_dir = os.getcwd()
server_name = 'aicheck-ultra'

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# Initialize mcpServers if it doesn't exist
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add or update AICheck server with unique name
config['mcpServers'][server_name] = {
    'command': 'node',
    'args': [os.path.join(project_dir, '.mcp/server/index.js')]
}

# Write back to file
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f'✓ Added {server_name} to Claude MCP configuration')
" || {
    echo "⚠️  Python JSON update failed. Please configure manually."
    exit 1
}

echo "✅ AICheck v6.0.0 activated for Claude Code!"
echo "🔄 Please restart Claude Code to load the new MCP server."
echo ""
echo "🆕 New in v6.0.0: Auto-Iterate Mode"
echo "   Try: ./aicheck auto-iterate --help"
