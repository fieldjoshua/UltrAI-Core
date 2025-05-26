#!/bin/bash
# Debug version of menu launcher

echo "Simple menu test script"
echo "----------------------"

# Mock models
MODELS=("openai-gpt4o" "anthropic-claude" "google-gemini" "deepseek-chat")

echo "Available models: ${MODELS[*]}"
echo

# Display menu
echo "Please select a model:"
for i in "${!MODELS[@]}"; do
    echo "  $((i+1)). ${MODELS[$i]}"
done

echo
echo "Enter your choice (1-${#MODELS[@]}):"
read -p "> " choice

if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#MODELS[@]}" ]; then
    selected=${MODELS[$((choice-1))]}
    echo "You selected: $selected"
else
    echo "Invalid choice."
fi

echo
echo "Test complete. Press Enter to exit."
read
