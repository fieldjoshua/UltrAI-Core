# Docker Model Runner CLI Adapter Guide

This guide explains how to use the Docker Model Runner CLI adapter, which provides an alternative integration approach using the Docker Model CLI commands instead of the REST API.

## Overview

The Docker Model Runner CLI adapter uses Docker's `docker model` commands to interact with locally installed AI models. This approach offers several advantages:

1. No need to configure API endpoints or ports
2. Uses the same commands as the Docker Desktop interface
3. Works with all models available through Docker Model Runner
4. Simple integration with minimal dependencies

## Prerequisites

Before using the CLI adapter, ensure:

1. Docker Desktop is installed and running
2. At least one model is pulled using `docker model pull` command

## How it Works

The CLI adapter:

1. Uses `docker model list` to discover available models
2. Executes `docker model run` to generate responses
3. Processes the output to provide a consistent interface
4. Supports both synchronous and streaming generation

## Installation

No special installation is needed beyond the normal Ultra setup. The adapter is included in the codebase under `src/models/docker_modelrunner_cli_adapter.py`.

## Usage

### 1. Import the Adapter

```python
from src.models.docker_modelrunner_cli_adapter import (
    DockerModelRunnerCLIAdapter,
    create_modelrunner_cli_adapter
)
```

### 2. List Available Models

```python
available_models = await DockerModelRunnerCLIAdapter.get_available_models()
```

### 3. Create an Adapter for a Model

```python
adapter = await create_modelrunner_cli_adapter("ai/smollm2")
```

### 4. Generate a Response

```python
response = await adapter.generate("What is Docker Model Runner?")
```

### 5. Stream a Response

```python
async for chunk in adapter.stream_generate("Explain containerization."):
    print(chunk, end="", flush=True)
```

## Configuration with Ultra

To use the CLI adapter with Ultra, update the Ultra configuration:

1. Set the environment variable to enable Docker Model Runner:
   ```bash
   export USE_MODEL_RUNNER=true
   export MODEL_RUNNER_TYPE=cli
   ```

2. Start the Ultra backend:
   ```bash
   python3 -m uvicorn backend.app:app --reload
   ```

## Testing

You can test the CLI adapter directly:

```bash
python3 scripts/test_modelrunner_cli.py
```

This script:
- Checks if Docker Model Runner is running
- Lists available models
- Tests generation with a simple prompt
- Tests streaming with a more complex prompt

## Available Models

To see which models are available:

```bash
docker model list
```

To pull a new model:

```bash
docker model pull ai/smollm2
```

## Troubleshooting

### No Models Listed

If no models are listed, pull a model:

```bash
docker model pull ai/smollm2
```

### Error in Response Generation

If you get an error during response generation:

1. Check if Docker Desktop is running
2. Verify the model is available with `docker model list`
3. Try running the model directly with `docker model run ai/smollm2 "Hello"`

### Other Issues

For other issues:

1. Check Docker Model Runner logs: `docker model logs`
2. Restart Docker Desktop
3. Try pulling a different model

## Comparison with API Adapter

| Feature | CLI Adapter | API Adapter |
|---------|-------------|-------------|
| Connection Method | CLI commands | HTTP API |
| Configuration | Simple | Requires port configuration |
| Performance | Slightly slower | Faster |
| Error Handling | Robust | Depends on API stability |
| Model Support | All CLI models | API-exposed models |

## Conclusion

The Docker Model Runner CLI adapter provides a simple and reliable way to integrate Ultra with locally run AI models. It requires minimal configuration and works with all models available through Docker Model Runner.