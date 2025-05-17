# Docker Orchestrator Integration Guide

This guide details how to setup, use, and troubleshoot the UltraLLM Orchestrator in a Docker environment.

## Overview

The Docker-based orchestration system allows UltraLLM to run in a containerized environment, providing consistent development and deployment experiences. The system can operate with cloud-based LLMs (OpenAI, Anthropic, etc.) as well as local models through Docker's Model Runner feature.

## Quick Start

To quickly get started with the Docker orchestrator:

```bash
# Start the Docker environment with orchestrator
./scripts/start-docker.sh -d --service backend

# Run a test analysis with the orchestrator
./scripts/run-docker-orchestrator.sh comparative "Explain quantum computing to a software developer" openai-gpt4o,anthropic-claude
```

## Docker Components

The Docker orchestration environment includes the following main components:

1. **Backend Container**: Runs the FastAPI application and orchestration logic
2. **Redis Container**: Provides caching and message queuing
3. **Postgres Container**: Stores analysis results and user data (optional)
4. **Model Runner Container**: Runs local LLMs for inference (optional)
5. **Worker Container**: Handles background tasks (optional)
6. **Frontend Container**: Provides the web UI (optional)

## Configuration

### Environment Variables

Key environment variables for the orchestrator:

| Variable              | Description                                     | Default                    |
| --------------------- | ----------------------------------------------- | -------------------------- |
| `USE_MOCK`            | Enable mock mode for testing                    | `false`                    |
| `ENABLE_MODEL_RUNNER` | Enable Docker Model Runner                      | `false`                    |
| `MODEL_RUNNER_TYPE`   | Type of Model Runner interface (`api` or `cli`) | `api`                      |
| `MODEL_RUNNER_URL`    | URL for Model Runner API                        | `http://model-runner:8080` |
| `DEFAULT_LOCAL_MODEL` | Default model for local inference               | `phi3:mini`                |

### Docker Compose Profiles

The Docker environment supports different profiles to enable different components:

- Default: `backend`, `postgres`, `redis`
- With Model Runner: `backend`, `postgres`, `redis`, `model-runner`
- With Frontend: `backend`, `postgres`, `redis`, `frontend`
- With Worker: `backend`, `postgres`, `redis`, `worker`

To start a specific profile:

```bash
docker compose --profile with-model-runner up -d
```

## Using the Orchestrator

### 1. Running Analyses in Docker

To run an analysis with the orchestrator in Docker:

```bash
./scripts/run-docker-orchestrator.sh [analysis_type] [prompt] [models] [output_format]
```

Examples:

```bash
# Comparative analysis with multiple models
./scripts/run-docker-orchestrator.sh comparative "Compare Python and JavaScript" openai-gpt4o,anthropic-claude text

# Factual analysis with one model
./scripts/run-docker-orchestrator.sh factual "Who was Albert Einstein?" anthropic-claude json
```

### 2. Using the Interactive CLI

To use the interactive CLI within Docker:

```bash
docker compose exec backend python -m src.cli.menu_ultra
```

### 3. Using Local Models

To use local models with the orchestrator:

1. Make sure Docker Model Runner is installed and set up
2. Pull the models you want to use:

```bash
python scripts/pull_modelrunner_models.py --models phi3:mini,llama3:8b
```

3. Enable model runner in your environment:

```bash
export ENABLE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=api
```

4. Run the orchestrator with local models:

```bash
./scripts/run-docker-orchestrator.sh comparative "Explain Docker" docker_modelrunner-phi3:mini,docker_modelrunner-llama3:8b
```

## Troubleshooting

### Common Issues

1. **Model Runner Connectivity Issues**

   - Ensure Docker Desktop is running
   - Verify Model Runner extension is installed and enabled
   - Check if the model-runner container is running
   - Verify the correct port is being used (default: 8080)

2. **LLM API Connection Issues**

   - Check API keys are correctly set in environment variables
   - Enable mock mode for testing without API keys
   - Check network connectivity to LLM providers

3. **Docker Environment Issues**
   - Check Docker Compose is installed and configured
   - Make sure the Docker daemon is running
   - Check container logs with `docker compose logs backend`

### Testing Docker Model Runner

To test your Docker Model Runner connectivity:

```bash
python scripts/test_modelrunner.py --generate
```

### Docker Logs

To view the logs for different containers:

```bash
# Backend logs
docker compose logs backend

# Model Runner logs
docker compose logs model-runner

# All container logs
docker compose logs
```

## Using the Web API

The Docker orchestrator exposes a REST API for integration with other systems:

- `POST /api/analyze`: Run an analysis with the orchestrator
- `GET /api/models`: List available models
- `GET /api/analyses`: List completed analyses
- `GET /api/analysis/{id}`: Get a specific analysis result

Example API request:

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "analysis_type": "comparative",
    "models": ["openai-gpt4o", "anthropic-claude"],
    "output_format": "json"
  }'
```

## Advanced Configuration

### Custom Model Mappings

The Docker environment supports custom model mappings to simplify model selection:

```env
MODEL_MAPPING='{"gpt4": "openai-gpt4o", "claude": "anthropic-claude-3-opus", "llama": "docker_modelrunner-llama3:8b"}'
```

### Custom Analysis Patterns

You can define and load custom analysis patterns for the orchestrator:

```env
ANALYSIS_PATTERNS_PATH="/app/data/analysis_patterns.json"
```

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Model Runner Documentation](https://docs.docker.com/engine/extend/model-runner/)
- [UltraLLM API Reference](./api_reference.md)
