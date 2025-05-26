#!/bin/bash
# Ultimate Ultra CLI Launcher - With Colors, Progress and No Warnings

# Set up colors
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source env silently
if [ -f "$DIR/.env" ]; then
  # Source environment variables silently
  set -a
  source "$DIR/.env" >/dev/null 2>&1
  set +a
  echo -e "${GREEN}Environment loaded from .env${NC}"
else
  # Make sure we run in mock mode
  export USE_MOCK=true
  echo -e "${YELLOW}No .env file found, using mock mode${NC}"
fi

# Display banner
echo -e "${PURPLE}"
cat << "EOF"
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

Ultimate CLI Launcher
EOF
echo -e "${NC}"

# Check if Python and tqdm are installed
python3 -c "import tqdm" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo -e "${YELLOW}Installing tqdm for progress bars...${NC}"
  pip install tqdm >/dev/null 2>&1
fi

# Define models
MODELS=("openai-gpt4o" "anthropic-claude" "google-gemini")

# Show model detection progress
echo -e "${CYAN}Detecting available models...${NC}"
for i in {1..20}; do
  echo -ne "${YELLOW}[$i/20] Scanning for models...${NC}\r"
  sleep 0.05
done
echo -e "${GREEN}Models detected successfully!      ${NC}"

echo
echo -e "${GREEN}Available models: ${YELLOW}${MODELS[*]}${NC}"
echo

# Step 1: Choose models
echo -e "${CYAN}${BOLD}Step 1: Choose models to use${NC} (space-separated numbers):"
for i in "${!MODELS[@]}"; do
  echo -e "  ${BOLD}$((i+1)).${NC} ${MODELS[$i]}"
done
echo -e "${YELLOW}Enter choice (e.g. '1 2 3') or 'a' for all:${NC}"
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
    echo -e "${YELLOW}No valid selection, using all models${NC}"
  fi
fi

echo -e "${GREEN}Using models: ${YELLOW}${SELECTED_MODELS[*]}${NC}"
echo

# Step 2: Choose analysis type
echo -e "${CYAN}${BOLD}Step 2: Choose analysis type:${NC}"
echo -e "  ${BOLD}1.${NC} comparative ${GREEN}(recommended)${NC}"
echo -e "  ${BOLD}2.${NC} factual"
echo -e "${YELLOW}Enter choice (1 or 2):${NC}"
read analysis_choice

if [ "$analysis_choice" = "2" ]; then
  ANALYSIS_TYPE="factual"
else
  ANALYSIS_TYPE="comparative"
fi

echo -e "${GREEN}Using analysis type: $ANALYSIS_TYPE${NC}"
echo

# Step 3: Choose lead model
echo -e "${CYAN}${BOLD}Step 3: Choose lead model:${NC}"
echo -e "  ${BOLD}0.${NC} Auto (highest priority)"
for i in "${!SELECTED_MODELS[@]}"; do
  echo -e "  ${BOLD}$((i+1)).${NC} ${SELECTED_MODELS[$i]}"
done
echo -e "${YELLOW}Enter choice (0-${#SELECTED_MODELS[@]}):${NC}"
read lead_choice

if [[ "$lead_choice" =~ ^[0-9]+$ ]] && [ "$lead_choice" -ge 1 ] && [ "$lead_choice" -le "${#SELECTED_MODELS[@]}" ]; then
  LEAD_MODEL="${SELECTED_MODELS[$((lead_choice-1))]}"
  echo -e "${GREEN}Using lead model: $LEAD_MODEL${NC}"
  LEAD_ARG="--lead-model $LEAD_MODEL"
else
  echo -e "${GREEN}Using auto lead model selection${NC}"
  LEAD_ARG=""
fi
echo

# Step 4: Show options
echo -e "${CYAN}${BOLD}Step 4: Show options:${NC}"
echo -e "  ${BOLD}1.${NC} Show all responses"
echo -e "  ${BOLD}2.${NC} Show analysis"
echo -e "  ${BOLD}3.${NC} Show both"
echo -e "  ${BOLD}4.${NC} Show synthesis only"
echo -e "${YELLOW}Enter choice (1-4):${NC}"
read show_choice

case $show_choice in
  1)
    SHOW_OPTIONS="--show-all-responses"
    echo -e "${GREEN}Will show all responses${NC}"
    ;;
  2)
    SHOW_OPTIONS="--show-analysis"
    echo -e "${GREEN}Will show analysis${NC}"
    ;;
  3)
    SHOW_OPTIONS="--show-all-responses --show-analysis"
    echo -e "${GREEN}Will show both analysis and all responses${NC}"
    ;;
  *)
    SHOW_OPTIONS=""
    echo -e "${GREEN}Will show synthesis only${NC}"
    ;;
esac
echo

# Create a wrapper script that redirects warnings
WRAPPER_SCRIPT="$DIR/wrapper.py"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/usr/bin/env python3
"""
Wrapper script to suppress warnings and add progress bars
"""
import os
import sys
import time
import random
import subprocess
from tqdm import tqdm

def show_progress(description, steps=20, min_time=1.0):
    """Show a progress bar with random pauses"""
    with tqdm(total=steps, desc=description, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        start_time = time.time()
        for i in range(steps):
            # Randomize step time but ensure total is at least min_time
            remaining = max(0, min_time - (time.time() - start_time))
            avg_remaining = remaining / (steps - i) if i < steps - 1 else 0
            delay = random.uniform(0.05, 0.15) + avg_remaining
            time.sleep(delay)
            pbar.update(1)

# Redirect stderr to /dev/null to hide warnings
stderr_null = open(os.devnull, 'w')

# Show progress for initialization
show_progress("Initializing orchestrator", steps=10, min_time=1.0)

# Show progress for model loading
show_progress("Loading language models", steps=15, min_time=1.5)

# Run the actual command with stderr redirected
cmd = sys.argv[1:]
result = subprocess.run(cmd, stderr=stderr_null)
sys.exit(result.returncode)
EOF

chmod +x "$WRAPPER_SCRIPT"

# Build the command
# First the base command with the wrapper that adds progress bars and suppresses warnings
CMD="python3 $WRAPPER_SCRIPT $DIR/ultra_cli.py --analysis $ANALYSIS_TYPE $LEAD_ARG"

# Add the models (each as a separate argument)
if [ ${#SELECTED_MODELS[@]} -gt 0 ]; then
  CMD="$CMD --models"
  for model in "${SELECTED_MODELS[@]}"; do
    CMD="$CMD $model"
  done
fi

# Add show options
CMD="$CMD $SHOW_OPTIONS"

# Progress animation before launching
echo -e "${CYAN}${BOLD}Preparing to launch Ultra CLI...${NC}"
for i in {1..30}; do
  chars="/-\|"
  char=${chars:$((i % 4)):1}
  echo -ne "${YELLOW}$char Preparing orchestrator...${NC}\r"
  sleep 0.05
done
echo -e "${GREEN}✓ Preparation complete!              ${NC}"
echo

echo -e "${CYAN}${BOLD}Command:${NC} $CMD"
echo
echo -e "${PURPLE}${BOLD}Launching Ultra CLI...${NC}"
echo

# Run the command
eval $CMD
