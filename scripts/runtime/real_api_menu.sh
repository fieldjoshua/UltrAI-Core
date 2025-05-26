#!/bin/bash
# Ultra API Menu Launcher (Using Real API Keys)

# Setup
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source the environment file
if [ -f "$DIR/.env" ]; then
  echo "Loading API keys from .env file"
  set -a
  source "$DIR/.env"
  set +a
else
  echo "ERROR: .env file not found. Please create one with your API keys."
  exit 1
fi

# Verify API keys
AVAILABLE_APIS=()
if [ -n "$OPENAI_API_KEY" ]; then
  AVAILABLE_APIS+=("OpenAI (Key found)")
  MODELS+=("openai-gpt4o")
fi
if [ -n "$ANTHROPIC_API_KEY" ]; then
  AVAILABLE_APIS+=("Anthropic (Key found)")
  MODELS+=("anthropic-claude")
fi
if [ -n "$GOOGLE_API_KEY" ]; then
  AVAILABLE_APIS+=("Google (Key found)")
  MODELS+=("google-gemini")
fi
if [ -n "$DEEPSEEK_API_KEY" ]; then
  AVAILABLE_APIS+=("Deepseek (Key found)")
  MODELS+=("deepseek-chat")
fi

echo "Ultra API Menu Launcher"
echo "---------------------"
echo "API Keys detected: ${#AVAILABLE_APIS[@]}"
for api in "${AVAILABLE_APIS[@]}"; do
  echo "- $api"
done
echo

# Disable mock mode
export USE_MOCK=false

if [ ${#MODELS[@]} -eq 0 ]; then
  echo "ERROR: No API keys found in .env file."
  echo "Please add at least one API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)"
  exit 1
fi

# Define analysis types
ANALYSIS_TYPES=("comparative" "factual")

# Step 1: Model selection
echo "Step 1: Select models (comma-separated numbers):"
for i in "${!MODELS[@]}"; do
  echo "$((i+1)). ${MODELS[$i]}"
done
echo "Enter numbers (e.g. 1,2,3) or 'all':"
read model_input

selected_models=()
if [ "$model_input" = "all" ]; then
  selected_models=("${MODELS[@]}")
else
  IFS=',' read -ra selections <<< "$model_input"
  for sel in "${selections[@]}"; do
    if [[ "$sel" =~ ^[0-9]+$ ]] && [ "$sel" -ge 1 ] && [ "$sel" -le "${#MODELS[@]}" ]; then
      selected_models+=("${MODELS[$((sel-1))]}")
    fi
  done
fi

# If no valid models selected, use all
if [ ${#selected_models[@]} -eq 0 ]; then
  selected_models=("${MODELS[@]}")
  echo "No valid selections, using all models."
else
  echo "Selected models: ${selected_models[*]}"
fi

# Step 2: Analysis type
echo
echo "Step 2: Select analysis type:"
for i in "${!ANALYSIS_TYPES[@]}"; do
  echo "$((i+1)). ${ANALYSIS_TYPES[$i]}"
done
echo "Enter number (1 or 2):"
read analysis_input

if [[ "$analysis_input" =~ ^[0-9]+$ ]] && [ "$analysis_input" -ge 1 ] && [ "$analysis_input" -le "${#ANALYSIS_TYPES[@]}" ]; then
  analysis_type="${ANALYSIS_TYPES[$((analysis_input-1))]}"
else
  analysis_type="comparative"
  echo "Invalid selection, using default: comparative"
fi
echo "Analysis type: $analysis_type"

# Step 3: Show analysis?
echo
echo "Step 3: Show analysis results? (y/n):"
read show_analysis_input

if [[ "$show_analysis_input" == "y" ]]; then
  show_analysis="--show-analysis"
  echo "Will show analysis results."
else
  show_analysis=""
  echo "Will not show analysis results."
fi

# Step 4: Show all responses?
echo
echo "Step 4: Show all model responses? (y/n):"
read show_responses_input

if [[ "$show_responses_input" == "y" ]]; then
  show_responses="--show-all-responses"
  echo "Will show all model responses."
else
  show_responses=""
  echo "Will not show all model responses."
fi

# Build the command
# Need to pass each model as a separate argument
models_args=""
for model in "${selected_models[@]}"; do
  models_args="$models_args $model"
done

cmd="python3 $DIR/ultra_cli.py --analysis $analysis_type --models $models_args $show_analysis $show_responses"

# Print and run the command
echo
echo "Running command: $cmd"
echo

# Run command
$cmd
