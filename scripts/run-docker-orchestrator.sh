#!/bin/bash
# Script to run the LLM orchestrator in Docker

# Set default values
ANALYSIS_TYPE=${1:-comparative}
PROMPT=${2:-"Explain quantum computing to a software developer"}
MODELS=${3:-"openai-gpt4o,anthropic-claude"}
USE_MOCK=${USE_MOCK:-false}
OUTPUT_FORMAT=${4:-text}

# Color codes for better output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display info
echo -e "${BLUE}=== Running UltraLLM Orchestrator in Docker ===${NC}"
echo -e "Analysis type: ${GREEN}$ANALYSIS_TYPE${NC}"
echo -e "Models: ${GREEN}$MODELS${NC}"
echo -e "Prompt: ${GREEN}\"$PROMPT\"${NC}"
echo -e "Mock mode: ${GREEN}$USE_MOCK${NC}"
echo -e "Output format: ${GREEN}$OUTPUT_FORMAT${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if the backend container is running
if ! docker compose ps | grep -q "backend.*Up"; then
    echo -e "${YELLOW}Backend container is not running. Starting it now...${NC}"
    docker compose up -d backend
    
    # Wait for container to be ready
    echo -e "${YELLOW}Waiting for container to be ready...${NC}"
    
    # Wait for the health check to pass, with a timeout
    TIMEOUT=60
    start_time=$(date +%s)
    while true; do
        if docker compose ps | grep -q "backend.*healthy"; then
            echo -e "${GREEN}Backend is healthy and ready!${NC}"
            break
        fi
        
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $TIMEOUT ]; then
            echo -e "${RED}Timeout waiting for backend to be ready. Check container logs:${NC}"
            echo -e "${YELLOW}docker compose logs backend${NC}"
            exit 1
        fi
        
        echo -e "${YELLOW}Waiting for backend to be ready... ($elapsed seconds elapsed)${NC}"
        sleep 5
    done
fi

# Check if Docker Model Runner models are requested and available
if [[ "$MODELS" == *"docker_modelrunner"* ]]; then
    echo -e "${BLUE}Docker Model Runner requested, checking if it's enabled...${NC}"
    
    # Check if model-runner service is running
    if ! docker compose ps | grep -q "model-runner.*Up"; then
        echo -e "${YELLOW}Model Runner container is not running. Starting it now...${NC}"
        docker compose --profile with-model-runner up -d model-runner
        
        # Wait for container to be ready
        echo -e "${YELLOW}Waiting for Model Runner to be ready...${NC}"
        sleep 10
    fi
    
    # Enable model runner in the environment
    docker compose exec -e ENABLE_MODEL_RUNNER=true backend bash -c "export ENABLE_MODEL_RUNNER=true"
fi

# Run the orchestrator in the container
echo -e "${BLUE}Executing orchestrator in Docker container...${NC}"
docker compose exec -e USE_MOCK=$USE_MOCK -e ENABLE_MODEL_RUNNER=${ENABLE_MODEL_RUNNER:-false} -e PYTHONPATH=/app backend python -m src.cli.run_test \
    --analysis $ANALYSIS_TYPE \
    --models $MODELS \
    --prompt "$PROMPT" \
    --output $OUTPUT_FORMAT

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
echo -e "${BLUE}To run with different parameters:${NC}"
echo "./scripts/run-docker-orchestrator.sh [analysis_type] [prompt] [models] [output_format]"
echo ""
echo -e "${BLUE}Examples:${NC}"
echo "./scripts/run-docker-orchestrator.sh comparative \"What is quantum computing?\" openai-gpt4o,anthropic-claude text"
echo "./scripts/run-docker-orchestrator.sh factual \"Who was Albert Einstein?\" anthropic-claude json"
echo "./scripts/run-docker-orchestrator.sh comparative \"Explain Docker containers\" docker_modelrunner-phi3:mini,docker_modelrunner-llama3:8b text"