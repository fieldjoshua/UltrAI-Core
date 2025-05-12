#!/bin/bash
# Start the Ultra backend with Docker Model Runner enabled

# Set environment variables for Docker Model Runner
export USE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=cli
export DEFAULT_LOCAL_MODEL=ai/smollm2

# Start the backend
echo "Starting Ultra backend with Docker Model Runner enabled..."
echo "Using model: $DEFAULT_LOCAL_MODEL"
echo "Model Runner type: $MODEL_RUNNER_TYPE"

# Run the backend with uvicorn
cd "$(dirname "$0")/.." || exit
python -m uvicorn backend.app:app --reload