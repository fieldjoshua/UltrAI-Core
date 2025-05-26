#!/bin/bash
# Menu-based launcher for UltrAI CLI

# Current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if .env file exists and source it
ENV_FILE="$DIR/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from $ENV_FILE"
    set -a  # Automatically export all variables
    source "$ENV_FILE"
    set +a
else
    # Check if env.example exists and create a copy
    if [ -f "$DIR/env.example" ]; then
        echo -e "\033[1;33mNo .env file found. Creating one from env.example...\033[0m"
        cp "$DIR/env.example" "$ENV_FILE"
        set -a
        source "$ENV_FILE"
        set +a
        echo -e "\033[1;33m.env file created. You may need to edit it with your API keys.\033[0m"
    else
        echo -e "\033[1;31mNo .env file found and env.example is missing.\033[0m"
        exit 1
    fi
fi

# Set USE_MOCK to true if no API keys are provided
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ] && [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "\033[1;33mNo API keys found. Setting USE_MOCK=true for testing mode.\033[0m"
    export USE_MOCK=true
fi

# Display banner
echo -e "\033[1;36m"
cat << "EOF"
  _   _ _ _            _    _____
 | | | | | |_ _ _ __ _| |  / __  |
 | | | | | __| '_/ _` | |  `' / /
 | |_| | | |_| | | (_| | |    / /
  \___/|_|\__|_|  \__,_|_|   /_/

Menu-Based Launcher
EOF
echo -e "\033[0m"

# Check if python3 and ultra_cli.py exist
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31mPython 3 is not installed or not in PATH. Please install Python 3.\033[0m"
    exit 1
fi

if [ ! -f "$DIR/ultra_cli.py" ]; then
    echo -e "\033[1;31multra_cli.py not found in $DIR. Make sure you're in the right directory.\033[0m"
    exit 1
fi

# Make sure the script is executable
chmod +x "$DIR/ultra_cli.py"

# Get available models based on environment variables or mock mode
echo "Detecting available LLM providers..."
AVAILABLE_MODELS=()

if [ "$USE_MOCK" = "true" ]; then
    # In mock mode, add all models
    AVAILABLE_MODELS+=("openai-gpt4o" "anthropic-claude" "google-gemini" "deepseek-chat")
    echo -e "\033[1;33mRunning in MOCK mode with simulated model responses.\033[0m"
else
    # Add models based on available API keys
    if [ -n "$OPENAI_API_KEY" ]; then
        AVAILABLE_MODELS+=("openai-gpt4o")
    fi
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        AVAILABLE_MODELS+=("anthropic-claude")
    fi
    if [ -n "$GOOGLE_API_KEY" ]; then
        AVAILABLE_MODELS+=("google-gemini")
    fi
    if [ -n "$DEEPSEEK_API_KEY" ]; then
        AVAILABLE_MODELS+=("deepseek-chat")
    fi
fi

# If no models are found, provide a warning and exit
if [ ${#AVAILABLE_MODELS[@]} -eq 0 ]; then
    echo -e "\033[1;31mNo LLM providers found. Please check your API keys in .env file or set USE_MOCK=true.\033[0m"
    exit 1
fi

echo -e "\nAvailable Models: ${AVAILABLE_MODELS[*]}\n"

# Function to display a menu and get selection
select_from_menu() {
    local title=$1
    shift
    local options=("$@")
    local selected=()
    local choice

    echo -e "\033[1;33m$title\033[0m"
    if [ "${#options[@]}" -eq 0 ]; then
        echo "No options available."
        return
    fi

    # Display numbered options with highly visible formatting
    echo -e "\033[1;31m>>> MENU OPTIONS: <<<\033[0m"
    for i in "${!options[@]}"; do
        echo -e "\033[1;37m  $((i+1)). ${options[$i]}\033[0m"
    done
    echo -e "\033[1;31m>>> END MENU <<<\033[0m"

    # Special option for multi-select
    if [[ "$title" == *"models"* ]]; then
        echo -e "  \033[1;36mA. All models\033[0m"
        echo -e "  \033[1;36mD. Done selecting\033[0m"

        # Multi-select loop
        while true; do
            echo -e "\n\033[1;31m>>> INPUT REQUIRED <<<\033[0m"
            echo -en "\033[1mYour choice (1-${#options[@]}, A for all, D when done):\033[0m "
            read -r choice

            if [[ "$choice" =~ ^[Aa]$ ]]; then
                # Select all
                selected=()
                for i in "${!options[@]}"; do
                    selected+=("${options[$i]}")
                done
                echo "Selected all models."
                break
            elif [[ "$choice" =~ ^[Dd]$ ]]; then
                # Done selecting
                echo "Selection complete."
                break
            elif [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
                # Add selection if not already selected
                option=${options[$((choice-1))]}
                if [[ ! " ${selected[*]} " =~ " $option " ]]; then
                    selected+=("$option")
                    echo -e "\033[1;32mAdded: $option\033[0m"
                else
                    echo -e "\033[1;33mAlready selected: $option\033[0m"
                fi
            else
                echo -e "\033[1;31mInvalid choice. Try again.\033[0m"
            fi

            # Show current selections
            if [ "${#selected[@]}" -gt 0 ]; then
                echo -e "Currently selected: \033[1;32m${selected[*]}\033[0m"
            fi
        done

        # If nothing selected, select all
        if [ "${#selected[@]}" -eq 0 ]; then
            for i in "${!options[@]}"; do
                selected+=("${options[$i]}")
            done
            echo -e "\033[1;33mNo specific selections made. Using all models.\033[0m"
        fi

        echo -e "\033[1;32mFinal selection: ${selected[*]}\033[0m"

    else
        # Single select for non-model choices
        while true; do
            echo -e "\n\033[1;31m>>> INPUT REQUIRED <<<\033[0m"
            echo -en "\033[1mYour choice (1-${#options[@]}):\033[0m "
            read -r choice

            if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
                selected=("${options[$((choice-1))]}")
                echo -e "\033[1;32mSelected: ${selected[0]}\033[0m"
                break
            else
                echo -e "\033[1;31mInvalid choice. Try again.\033[0m"
            fi
        done
    fi

    echo "${selected[@]}"
}

# Menu 1: Model Selection
echo -e "\n\033[1mPlease select models to use:\033[0m"
MODEL_CHOICE=($(select_from_menu "Select models to use:" "${AVAILABLE_MODELS[@]}"))
echo -e "Models selected: \033[1;32m${MODEL_CHOICE[*]}\033[0m\n"

# Menu 2: Analysis Type
ANALYSIS_OPTIONS=("comparative" "factual")
echo -e "\n\033[1mPlease select analysis type:\033[0m"
ANALYSIS_TYPE=($(select_from_menu "Select analysis type:" "${ANALYSIS_OPTIONS[@]}"))
echo -e "Analysis type selected: \033[1;32m${ANALYSIS_TYPE}\033[0m\n"

# Menu 3: Lead Model
LEAD_OPTIONS=("Use highest priority model" "${MODEL_CHOICE[@]}")
echo -e "\n\033[1mPlease select lead model for synthesis:\033[0m"
LEAD_SELECTION=($(select_from_menu "Select lead model for synthesis:" "${LEAD_OPTIONS[@]}"))

# Interpret lead model selection
if [[ "$LEAD_SELECTION" == "Use highest priority model" ]]; then
    LEAD_MODEL=""
    echo -e "Lead model: \033[1;32mUsing highest priority model\033[0m\n"
else
    LEAD_MODEL="$LEAD_SELECTION"
    echo -e "Lead model selected: \033[1;32m${LEAD_MODEL}\033[0m\n"
fi

# Menu 4: Show Analysis
SHOW_OPTIONS=("Yes" "No")
echo -e "\n\033[1mShow analysis results?\033[0m"
SHOW_ANALYSIS_CHOICE=($(select_from_menu "Show analysis results?" "${SHOW_OPTIONS[@]}"))
echo -e "Show analysis: \033[1;32m${SHOW_ANALYSIS_CHOICE}\033[0m\n"

# Menu 5: Show All Responses
echo -e "\n\033[1mShow all model responses?\033[0m"
SHOW_RESPONSES_CHOICE=($(select_from_menu "Show all model responses?" "${SHOW_OPTIONS[@]}"))
echo -e "Show all responses: \033[1;32m${SHOW_RESPONSES_CHOICE}\033[0m\n"

# Convert selections to options
if [[ "$SHOW_ANALYSIS_CHOICE" == "Yes" ]]; then
    SHOW_ANALYSIS="--show-analysis"
else
    SHOW_ANALYSIS=""
fi

if [[ "$SHOW_RESPONSES_CHOICE" == "Yes" ]]; then
    SHOW_RESPONSES="--show-all-responses"
else
    SHOW_RESPONSES=""
fi

# Build the command
CMD="python3 $DIR/ultra_cli.py --analysis $ANALYSIS_TYPE"

if [ ${#MODEL_CHOICE[@]} -gt 0 ]; then
    # Properly quote model names to handle spaces
    MODELS_ARG=""
    for model in "${MODEL_CHOICE[@]}"; do
        MODELS_ARG="$MODELS_ARG \"$model\""
    done
    CMD="$CMD --models $MODELS_ARG"
fi

if [ -n "$LEAD_MODEL" ]; then
    CMD="$CMD --lead-model \"$LEAD_MODEL\""
fi

if [ -n "$SHOW_ANALYSIS" ]; then
    CMD="$CMD $SHOW_ANALYSIS"
fi

if [ -n "$SHOW_RESPONSES" ]; then
    CMD="$CMD $SHOW_RESPONSES"
fi

# Launch the CLI with the selected options
echo -e "\n\033[1;32mLaunching UltrAI CLI with your preferences...\033[0m\n"
echo "Command: $CMD"
echo

# Execute the command using eval to handle the quotes properly
eval $CMD
