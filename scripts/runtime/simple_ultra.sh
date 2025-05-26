#!/bin/bash
# Super Simple Ultra CLI Launcher

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

# Source env file
if [ -f "$DIR/.env" ]; then
  echo -e "${GREEN}Loading environment from .env${NC}"
  set -a
  source "$DIR/.env"
  set +a
else
  echo -e "${YELLOW}No .env file found, using mock mode${NC}"
  export USE_MOCK=true
fi

# Display banner
echo -e "${PURPLE}"
cat << "EOF"
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

Simple Menu Launcher
EOF
echo -e "${NC}"

# Define available models
if [ "$USE_MOCK" = "true" ]; then
  MODELS=("openai-gpt4o" "anthropic-claude" "google-gemini" "deepseek-chat")
  echo -e "${YELLOW}Running in MOCK mode${NC}"
else
  MODELS=()
  if [ -n "$OPENAI_API_KEY" ]; then
    MODELS+=("openai-gpt4o")
  fi
  if [ -n "$ANTHROPIC_API_KEY" ]; then
    MODELS+=("anthropic-claude")
  fi
  if [ -n "$GOOGLE_API_KEY" ]; then
    MODELS+=("google-gemini")
  fi
  if [ -n "$DEEPSEEK_API_KEY" ]; then
    MODELS+=("deepseek-chat")
  fi
fi

# Check if any models are available
if [ ${#MODELS[@]} -eq 0 ]; then
  echo -e "${RED}No API keys found. Please check your .env file or set USE_MOCK=true${NC}"
  exit 1
fi

echo -e "${GREEN}Available models: ${YELLOW}${MODELS[*]}${NC}\n"

# Select models (allow multiple with space-separated numbers)
echo -e "${CYAN}${BOLD}Step 1: Select models to use:${NC}"
for i in "${!MODELS[@]}"; do
  echo -e "  $((i+1)). ${MODELS[$i]}"
done
echo -e "${YELLOW}Enter numbers (space-separated) or 'a' for all:${NC}"
read -r model_input

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
  # Use all if invalid selection
  if [ ${#SELECTED_MODELS[@]} -eq 0 ]; then
    SELECTED_MODELS=("${MODELS[@]}")
    echo -e "${YELLOW}No valid selection, using all models.${NC}"
  fi
fi

echo -e "${GREEN}Using models: ${SELECTED_MODELS[*]}${NC}\n"

# Select analysis type
echo -e "${CYAN}${BOLD}Step 2: Select analysis type:${NC}"
echo "  1. comparative"
echo "  2. factual"
echo -e "${YELLOW}Enter number (1 or 2):${NC}"
read -r analysis_choice

if [ "$analysis_choice" = "2" ]; then
  ANALYSIS_TYPE="factual"
else
  ANALYSIS_TYPE="comparative"
fi
echo -e "${GREEN}Using analysis type: $ANALYSIS_TYPE${NC}\n"

# Lead model selection
echo -e "${CYAN}${BOLD}Step 3: Select lead model:${NC}"
echo "  0. Use highest priority model (default)"
for i in "${!SELECTED_MODELS[@]}"; do
  echo "  $((i+1)). ${SELECTED_MODELS[$i]}"
done
echo -e "${YELLOW}Enter number:${NC}"
read -r lead_choice

if [[ "$lead_choice" =~ ^[0-9]+$ ]] && [ "$lead_choice" -ge 1 ] && [ "$lead_choice" -le "${#SELECTED_MODELS[@]}" ]; then
  LEAD_MODEL="${SELECTED_MODELS[$((lead_choice-1))]}"
  echo -e "${GREEN}Using lead model: $LEAD_MODEL${NC}"
else
  LEAD_MODEL=""
  echo -e "${GREEN}Using highest priority model as lead${NC}"
fi
echo

# Show analysis results
echo -e "${CYAN}${BOLD}Step 4: Show analysis results?${NC}"
echo "  1. Yes"
echo "  2. No"
echo -e "${YELLOW}Enter number:${NC}"
read -r show_analysis_choice

if [ "$show_analysis_choice" = "1" ]; then
  SHOW_ANALYSIS="--show-analysis"
  echo -e "${GREEN}Will show analysis results${NC}"
else
  SHOW_ANALYSIS=""
  echo -e "${GREEN}Will not show analysis results${NC}"
fi
echo

# Show all responses
echo -e "${CYAN}${BOLD}Step 5: Show all responses?${NC}"
echo "  1. Yes"
echo "  2. No"
echo -e "${YELLOW}Enter number:${NC}"
read -r show_responses_choice

if [ "$show_responses_choice" = "1" ]; then
  SHOW_RESPONSES="--show-all-responses"
  echo -e "${GREEN}Will show all model responses${NC}"
else
  SHOW_RESPONSES=""
  echo -e "${GREEN}Will not show all model responses${NC}"
fi
echo

# Create fix script
echo -e "${CYAN}Creating analysis fix...${NC}"
FIX_SCRIPT="$DIR/apply_fix.py"

cat > "$FIX_SCRIPT" << 'EOF'
#!/usr/bin/env python3
# Analysis fix script
import sys, os, asyncio
sys.path.insert(0, os.getcwd())

async def apply_fix():
    # Import modules
    from src.simple_core.factory import create_from_env
    from src.simple_core.analysis.modules.comparative import ComparativeAnalysis
    from src.simple_core.analysis.modules.factual import FactualAnalysis

    # The original analyze methods
    original_comparative = ComparativeAnalysis.analyze
    original_factual = FactualAnalysis.analyze

    # Create patched method
    async def fixed_analyze(self, prompt, responses, options=None):
        options = options or {}

        # Ensure analysis model is set for mock implementation
        if not options.get("analysis_model"):
            # Let the mock method run
            options["_bypass_analysis_model_check"] = True

        return await original_comparative(self, prompt, responses, options)

    async def fixed_factual_analyze(self, prompt, responses, options=None):
        options = options or {}

        # Ensure analysis model is set for mock implementation
        if not options.get("analysis_model"):
            # Let the mock method run
            options["_bypass_analysis_model_check"] = True

        return await original_factual(self, prompt, responses, options)

    # Patch the analyze methods
    ComparativeAnalysis.analyze = fixed_analyze
    FactualAnalysis.analyze = fixed_factual_analyze

    print("Analysis fix applied successfully")

# Run the fix
asyncio.run(apply_fix())
EOF

chmod +x "$FIX_SCRIPT"
python3 "$FIX_SCRIPT"

# Build model args
MODEL_ARGS=""
for model in "${SELECTED_MODELS[@]}"; do
  MODEL_ARGS="$MODEL_ARGS $model"
done

# Create the command
if [ -n "$LEAD_MODEL" ]; then
  LEAD_ARG="--lead-model $LEAD_MODEL"
else
  LEAD_ARG=""
fi

# Full command
CMD="python3 $DIR/ultra_cli.py --analysis $ANALYSIS_TYPE $LEAD_ARG --models $MODEL_ARGS $SHOW_ANALYSIS $SHOW_RESPONSES"

# Run the command
echo -e "${CYAN}${BOLD}Launching Ultra CLI...${NC}"
echo -e "${YELLOW}Command: $CMD${NC}\n"
eval $CMD
