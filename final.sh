#!/bin/bash
# Final Ultra CLI Launcher - No Patching

# Current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source env silently
if [ -f "$DIR/.env" ]; then
  # Source environment variables
  set -a
  source "$DIR/.env"
  set +a
  echo "Environment loaded from .env"
else
  # Make sure we run in mock mode
  export USE_MOCK=true
  echo "No .env file found, using mock mode"
fi

# Display banner
cat << "EOF"
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

Ultra CLI Launcher (FINAL)
EOF

# Define models
MODELS=("openai-gpt4o" "anthropic-claude" "google-gemini")

echo
echo "Available models: ${MODELS[*]}"
echo

# Step 1: Choose models
echo "Step 1: Choose models to use (space-separated numbers):"
for i in "${!MODELS[@]}"; do
  echo "  $((i+1)). ${MODELS[$i]}"
done
echo "Enter choice (e.g. '1 2 3') or 'a' for all:"
read model_input

# Process model selection
if [[ "$model_input" == "a" ]]; then
  SELECTED_MODELS=("${MODELS[@]}")
else
  SELECTED_MODELS=()
  for num in $model_input; do
    if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#MODELS[@]}" ]; then
      SELECTED_MODELS+=("${MODELS[$((num-1))]}")
    fi
  done

  # Use all if none selected
  if [ ${#SELECTED_MODELS[@]} -eq 0 ]; then
    SELECTED_MODELS=("${MODELS[@]}")
    echo "No valid selection, using all models"
  fi
fi

echo "Using models: ${SELECTED_MODELS[*]}"
echo

# Step 2: Choose analysis type
echo "Step 2: Choose analysis type:"
echo "  1. comparative (recommended)"
echo "  2. factual"
echo "Enter choice (1 or 2):"
read analysis_choice

if [ "$analysis_choice" = "2" ]; then
  ANALYSIS_TYPE="factual"
else
  ANALYSIS_TYPE="comparative"
fi

echo "Using analysis type: $ANALYSIS_TYPE"
echo

# Build the command
# First the base command
CMD="python3 $DIR/ultra_cli.py --analysis $ANALYSIS_TYPE"

# Add the models (each as a separate argument)
if [ ${#SELECTED_MODELS[@]} -gt 0 ]; then
  CMD="$CMD --models"
  for model in "${SELECTED_MODELS[@]}"; do
    CMD="$CMD $model"
  done
fi

# Add show all responses option
CMD="$CMD --show-all-responses"

echo "Command: $CMD"
echo
echo "Launching Ultra CLI..."
echo

# Run the command
eval $CMD
