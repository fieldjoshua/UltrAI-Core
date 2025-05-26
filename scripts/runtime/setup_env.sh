#!/bin/bash
# Setup environment variables for UltrAI CLI

# Save API keys to a local .env file
cat > .env << EOF
# OpenAI API Key and Organization ID
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_ORG_ID="your_openai_org_id_here"  # Optional: Only needed if you're part of multiple orgs

# Anthropic API Key
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Google API Key (for Gemini)
export GOOGLE_API_KEY="your_google_api_key_here"

# Deepseek API Key and Base URL
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
export DEEPSEEK_API_BASE="https://api.deepseek.com"  # Or your custom endpoint if different

# Ollama Configuration
export OLLAMA_BASE_URL="http://localhost:11434"  # Default local Ollama URL
export OLLAMA_MODEL="llama3"  # Default model to use with Ollama

# Optional: Path to a local Llama model
# export LLAMA_MODEL_PATH="/path/to/llama/model"
# export LLAMA_COMMAND="llama"
EOF

# Make the file executable
chmod +x .env

echo "Created .env file with placeholder API keys."
echo "Please edit the .env file to add your actual API keys."
echo ""
echo "After editing, run: source .env"
echo "Then run: ./ultra_cli.py"
