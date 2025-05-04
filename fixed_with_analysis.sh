#!/bin/bash
# Ultra CLI Launcher with Analysis Fix

# Setup
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Display cool purple banner
echo -e "\033[38;5;93m"  # Purple color
cat << "EOF"
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

 Enhanced CLI with Analysis Fix
EOF
echo -e "\033[0m"  # Reset color

# Source environment from .env file
if [ -f "$DIR/.env" ]; then
  echo -e "\033[1;36mLoading API keys from .env file\033[0m"
  set -a
  source "$DIR/.env"
  set +a
else
  echo -e "\033[1;33mWARNING: No .env file found. Using mock mode.\033[0m"
  export USE_MOCK=true
fi

# Available models based on environment
MODELS=()
if [ -n "$OPENAI_API_KEY" ] || [ "$USE_MOCK" = "true" ]; then
  MODELS+=("openai-gpt4o")
fi
if [ -n "$ANTHROPIC_API_KEY" ] || [ "$USE_MOCK" = "true" ]; then
  MODELS+=("anthropic-claude")
fi
if [ -n "$GOOGLE_API_KEY" ] || [ "$USE_MOCK" = "true" ]; then
  MODELS+=("google-gemini")
fi
if [ -n "$DEEPSEEK_API_KEY" ] || [ "$USE_MOCK" = "true" ]; then
  MODELS+=("deepseek-chat")
fi

# Check if any models are available
if [ ${#MODELS[@]} -eq 0 ]; then
  echo -e "\033[1;31mERROR: No API keys found and mock mode not enabled.\033[0m"
  exit 1
fi

echo -e "\033[1;32mAvailable models: ${MODELS[*]}\033[0m"
echo

# Menu 1: Choose models
echo -e "\033[1;35m=== STEP 1: MODEL SELECTION ===\033[0m"
echo -e "Which models do you want to use? (enter numbers separated by space)"
for i in "${!MODELS[@]}"; do
  echo -e "\033[1;37m  $((i+1)). ${MODELS[$i]}\033[0m"
done
echo -e "\033[1;33mEnter selection (e.g. '1 2 3') or 'all':\033[0m"
read -r selection

# Process model selection
if [ "$selection" = "all" ]; then
  SELECTED_MODELS=("${MODELS[@]}")
else
  SELECTED_MODELS=()
  for num in $selection; do
    if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#MODELS[@]}" ]; then
      SELECTED_MODELS+=("${MODELS[$((num-1))]}")
    fi
  done

  # Default to all if no valid selection
  if [ ${#SELECTED_MODELS[@]} -eq 0 ]; then
    SELECTED_MODELS=("${MODELS[@]}")
    echo -e "\033[1;33mNo valid selection, using all models.\033[0m"
  fi
fi

echo -e "\033[1;32mUsing models: ${SELECTED_MODELS[*]}\033[0m"
echo

# Menu 2: Analysis type
echo -e "\033[1;35m=== STEP 2: ANALYSIS TYPE ===\033[0m"
echo -e "Select analysis type:"
echo -e "\033[1;37m  1. comparative\033[0m"
echo -e "\033[1;37m  2. factual\033[0m"
echo -e "\033[1;33mEnter selection (1 or 2):\033[0m"
read -r analysis_num

if [ "$analysis_num" = "2" ]; then
  ANALYSIS_TYPE="factual"
else
  ANALYSIS_TYPE="comparative"
fi
echo -e "\033[1;32mUsing analysis type: $ANALYSIS_TYPE\033[0m"
echo

# Menu 3: Lead model selection
echo -e "\033[1;35m=== STEP 3: LEAD MODEL ===\033[0m"
echo -e "Select lead model for synthesis and analysis:"
echo -e "\033[1;37m  0. Use highest priority model (default)\033[0m"
for i in "${!SELECTED_MODELS[@]}"; do
  echo -e "\033[1;37m  $((i+1)). ${SELECTED_MODELS[$i]}\033[0m"
done
echo -e "\033[1;33mEnter selection (0-${#SELECTED_MODELS[@]}):\033[0m"
read -r lead_model_num

LEAD_MODEL=""
if [[ "$lead_model_num" =~ ^[0-9]+$ ]] && [ "$lead_model_num" -ge 1 ] && [ "$lead_model_num" -le "${#SELECTED_MODELS[@]}" ]; then
  LEAD_MODEL="${SELECTED_MODELS[$((lead_model_num-1))]}"
  echo -e "\033[1;32mUsing lead model: $LEAD_MODEL\033[0m"
else
  # Use the first selected model as lead if none specified
  if [ ${#SELECTED_MODELS[@]} -gt 0 ]; then
    LEAD_MODEL="${SELECTED_MODELS[0]}"
    echo -e "\033[1;33mUsing highest priority model: $LEAD_MODEL\033[0m"
  else
    echo -e "\033[1;32mUsing highest priority model as lead.\033[0m"
  fi
fi
echo

# Menu 4: Show analysis
echo -e "\033[1;35m=== STEP 4: SHOW ANALYSIS ===\033[0m"
echo -e "Show detailed analysis results? (y/n):"
echo -e "\033[1;33mEnter y or n:\033[0m"
read -r show_analysis
if [ "$show_analysis" = "y" ]; then
  SHOW_ANALYSIS="--show-analysis"
  echo -e "\033[1;32mWill show analysis results.\033[0m"
else
  SHOW_ANALYSIS=""
  echo -e "\033[1;32mWill not show analysis results.\033[0m"
fi
echo

# Menu 5: Show all responses
echo -e "\033[1;35m=== STEP 5: SHOW ALL RESPONSES ===\033[0m"
echo -e "Show all individual model responses? (y/n):"
echo -e "\033[1;33mEnter y or n:\033[0m"
read -r show_responses
if [ "$show_responses" = "y" ]; then
  SHOW_RESPONSES="--show-all-responses"
  echo -e "\033[1;32mWill show all model responses.\033[0m"
else
  SHOW_RESPONSES=""
  echo -e "\033[1;32mWill not show all model responses.\033[0m"
fi

# Summary of selections
echo
echo -e "\033[1;35m=== CONFIGURATION SUMMARY ===\033[0m"
echo -e "\033[1;37mAnalysis type:   \033[1;32m$ANALYSIS_TYPE\033[0m"
echo -e "\033[1;37mLead model:      \033[1;32m${LEAD_MODEL:-"(highest priority)"}\033[0m"
echo -e "\033[1;37mShow analysis:   \033[1;32m${show_analysis:-"n"}\033[0m"
echo -e "\033[1;37mShow responses:  \033[1;32m${show_responses:-"n"}\033[0m"
echo -e "\033[1;37mSelected models: \033[1;32m${SELECTED_MODELS[*]}\033[0m"
echo

# Create a Python script to apply the analysis fix
PATCH_SCRIPT="$DIR/patch_analysis.py"
cat > "$PATCH_SCRIPT" << 'EOF'
"""Patch script to apply the analysis fix."""
import sys
import os
import importlib.util

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Import our analysis fix
try:
    from src.simple_core.analysis_fix import patch_modular_orchestrator
    success = patch_modular_orchestrator()
    if success:
        print("Successfully applied analysis fix patch")
    else:
        print("Failed to apply analysis fix patch")
except Exception as e:
    print(f"Error importing analysis fix: {e}")

# Exit with success status
sys.exit(0)
EOF

# Apply the analysis fix before launching the CLI
echo -e "\033[1;35m=== APPLYING ANALYSIS FIX ===\033[0m"
python3 "$PATCH_SCRIPT"

# Build command
COMMAND="python3 $DIR/ultra_cli.py --analysis $ANALYSIS_TYPE $SHOW_ANALYSIS $SHOW_RESPONSES"

# Add lead model if selected
if [ -n "$LEAD_MODEL" ]; then
  COMMAND="$COMMAND --lead-model $LEAD_MODEL"
fi

# Add models (each as a separate argument)
if [ ${#SELECTED_MODELS[@]} -gt 0 ]; then
  COMMAND="$COMMAND --models"
  for model in "${SELECTED_MODELS[@]}"; do
    COMMAND="$COMMAND $model"
  done
fi

echo -e "\033[1;35m=== LAUNCHING ULTRA CLI ===\033[0m"
echo -e "\033[1;36mExecuting: $COMMAND\033[0m"
echo -e "\033[1;35m==========================\033[0m"
echo

# Execute the command directly
$COMMAND
