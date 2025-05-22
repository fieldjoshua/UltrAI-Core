# Docker-based Orchestrator Setup Guide

This guide explains how to set up and use the LLM orchestration system within the Docker environment, ensuring it reproduces the current functionality without unnecessary complexity.

## Prerequisites

- Docker and Docker Compose installed
- Access to LLM API keys (or willingness to use mock mode)
- Basic familiarity with Docker concepts

## Setup Process

### 1. Environment Variables Configuration

Create or update your `.env` file in the project root with the following variables:

```
# Core environment settings
ENVIRONMENT=development
LOG_LEVEL=debug
DEBUG=true

# LLM API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here

# Mock mode (set to true if you don't have API keys)
USE_MOCK=true
ENABLE_MOCK_LLM=true

# Orchestrator settings
ORCHESTRATOR_ENABLE=true
ORCHESTRATOR_DEFAULT_ANALYSIS=comparative
```

If you don't have API keys, set `USE_MOCK=true` and `ENABLE_MOCK_LLM=true` to use simulated responses.

### 2. Docker Compose Configuration

The existing docker-compose.yml already includes the necessary volume mappings:

```yaml
volumes:
  - ./backend:/app/backend
  - ./scripts:/app/scripts
  - ./src:/app/src # Contains orchestrator code
  - ./logs:/app/logs
  - ./data:/app/data
```

No changes are needed to the volume mappings unless your orchestrator code is in a different location.

### 3. Starting the Docker Environment

To start the Docker environment with orchestrator support:

```bash
# Build and start the containers
docker compose up -d backend

# If you want to see logs as the containers start
docker compose up backend
```

To stop the environment:

```bash
docker compose down
```

### 4. Verifying Orchestrator Functionality

To verify that the orchestrator is working correctly in Docker:

```bash
# Check logs for any errors
docker compose logs -f backend

# Access the backend shell to run Python commands
docker compose exec backend bash

# Once inside the container, you can run Python to test the orchestrator
python -c "from src.orchestration import Orchestrator; print('Orchestrator imported successfully')"
```

## Using the Orchestrator in Docker

### Running the CLI Interface

To use the CLI interface within Docker:

```bash
# Access the backend container shell
docker compose exec backend bash

# Run the menu interface
python -m src.cli.menu_ultra
```

### Testing with Sample Prompts

To test the orchestrator with sample prompts:

```bash
# Access the backend container shell
docker compose exec backend bash

# Run the test script
python -m src.cli.run_test --prompt "Explain quantum computing in simple terms" --models openai-gpt4o,anthropic-claude --analysis comparative
```

## Troubleshooting

### Common Issues and Solutions

1. **ImportError: No module named 'src'**

   - Ensure the src directory is properly mounted
   - Check that the Python path includes the project root
   - Try running `export PYTHONPATH=$PYTHONPATH:/app` in the container

2. **API Key errors**

   - Verify that environment variables are correctly set in .env
   - Check that Docker Compose is using the .env file
   - Try setting the variables directly in docker-compose.yml for testing

3. **Permission errors on mounted volumes**

   - Check file permissions in the host system
   - Run `chmod -R 755 ./src` to ensure files are readable

4. **Container fails to start**
   - Check logs: `docker compose logs backend`
   - Ensure all required dependencies are installed
   - Verify that ports are not already in use

## Examples

### Example 1: Basic Comparative Analysis

```bash
docker compose exec backend bash -c "python -m src.cli.run_test --prompt 'What is the most effective way to learn a new programming language?' --models openai-gpt4o,anthropic-claude --analysis comparative"
```

Expected output:

```
Running comparative analysis with 2 models...
Initial responses received
Analyzing responses...
Analysis complete. Results:
[Summary of the comparative analysis between the models]
```

### Example 2: Using Mock Mode

```bash
docker compose exec backend bash -c "export USE_MOCK=true && python -m src.cli.run_test --prompt 'Explain blockchain technology' --models openai-gpt4o,anthropic-claude,google-gemini --analysis comparative"
```

Expected output:

```
MOCK MODE ENABLED
Running comparative analysis with 3 models...
Initial responses received (mock data)
Analyzing responses...
Analysis complete. Results:
[Simulated analysis summary]
```

## Additional Resources

- For more details on the orchestrator architecture, see `src/orchestration/README.md`
- For details on analysis modules, see `src/analysis/README.md`
- For information on LLM adapters, see `src/adapters/README.md`
