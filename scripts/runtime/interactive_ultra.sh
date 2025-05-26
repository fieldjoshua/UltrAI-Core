#!/bin/bash
# Interactive launcher for UltrAI CLI

# Current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source the environment variables
source "$DIR/.env"

# Display banner
echo -e "\033[1;36m"
cat << "EOF"
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

Interactive Launcher
EOF
echo -e "\033[0m"

# Get available models
echo "Detecting available LLM providers..."
AVAILABLE_MODELS=""
if [ -n "$OPENAI_API_KEY" ]; then
    AVAILABLE_MODELS="$AVAILABLE_MODELS openai-gpt4o"
fi
if [ -n "$ANTHROPIC_API_KEY" ]; then
    AVAILABLE_MODELS="$AVAILABLE_MODELS anthropic-claude"
fi
if [ -n "$GOOGLE_API_KEY" ]; then
    AVAILABLE_MODELS="$AVAILABLE_MODELS google-gemini"
fi
if [ -n "$DEEPSEEK_API_KEY" ]; then
    AVAILABLE_MODELS="$AVAILABLE_MODELS deepseek-chat"
fi

echo -e "\nAvailable Models:$AVAILABLE_MODELS\n"

# Ask which models to use
echo -e "\033[1;33mSelect models to use (space-separated, leave blank for all):\033[0m"
read -e SELECTED_MODELS

# Ask which analysis to use
echo -e "\033[1;33mSelect analysis type (comparative/factual, default: comparative):\033[0m"
read -e ANALYSIS_TYPE
ANALYSIS_TYPE=${ANALYSIS_TYPE:-comparative}

# Ask which model should be the lead
echo -e "\033[1;33mSelect lead model (leave blank for highest priority):\033[0m"
read -e LEAD_MODEL

# Ask about display options
echo -e "\033[1;33mShow analysis results? (y/n, default: n):\033[0m"
read -e SHOW_ANALYSIS
SHOW_ANALYSIS=${SHOW_ANALYSIS:-n}

echo -e "\033[1;33mShow all model responses? (y/n, default: n):\033[0m"
read -e SHOW_RESPONSES
SHOW_RESPONSES=${SHOW_RESPONSES:-n}

# Build the command
CMD="$DIR/ultra_cli.py --analysis $ANALYSIS_TYPE"

if [ -n "$SELECTED_MODELS" ]; then
    CMD="$CMD --models $SELECTED_MODELS"
fi

if [ -n "$LEAD_MODEL" ]; then
    CMD="$CMD --lead-model $LEAD_MODEL"
fi

if [ "$SHOW_ANALYSIS" = "y" ]; then
    CMD="$CMD --show-analysis"
fi

if [ "$SHOW_RESPONSES" = "y" ]; then
    CMD="$CMD --show-all-responses"
fi

# Launch the CLI with the selected options
echo -e "\n\033[1;32mLaunching UltrAI CLI with your preferences...\033[0m\n"
$CMD
