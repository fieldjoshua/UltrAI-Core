# Docker Model Runner Integration

This document describes the technical integration between Ultra and Docker Model Runner, allowing the use of local open-source LLMs in the Ultra platform.

## Overview

Docker Model Runner integration allows Ultra to use locally-run open-source language models through Docker Desktop's built-in model functionality. This integration uses the `docker model` CLI commands to interact with local models, providing a reliable and straightforward way to run models without external API dependencies.

## Architecture

### Integration Approach

The integration uses a CLI adapter pattern that:

1. Uses Docker CLI commands to communicate with Docker Model Runner
2. Provides an implementation of the standard LLMAdapter interface
3. Supports both synchronous and streaming text generation
4. Automatically discovers available models from Docker Model Runner

### Component Diagram

```
┌─────────────────┐      ┌───────────────────────┐      ┌───────────────────┐
│                 │      │                       │      │                   │
│  Ultra Backend  │─────▶│  DockerModelRunner   │─────▶│  Docker Desktop   │
│                 │      │  CLI Adapter         │      │  Model Runner     │
│                 │      │                       │      │                   │
└─────────────────┘      └───────────────────────┘      └───────────────────┘
        │                                                        │
        │                                                        │
        │                        ┌───────────────┐               │
        │                        │               │               │
        └────────────────────────▶   Local LLMs  ◀───────────────┘
                                 │               │
                                 └───────────────┘
```

### Key Components

1. **DockerModelRunnerCLIAdapter**: Implements the LLMAdapter interface and uses the `docker model` commands to interact with Docker Model Runner.

2. **Configuration System**: Environment variables control the Docker Model Runner integration:

   - `USE_MODEL_RUNNER`: Enables/disables Docker Model Runner integration
   - `MODEL_RUNNER_TYPE`: Specifies the adapter type ("cli" for CLI adapter)

3. **Model Discovery**: The adapter automatically discovers available models using the `docker model list` command.

## Implementation Details

### CLI Adapter

The CLI adapter implementation is in `src/models/docker_modelrunner_cli_adapter.py`. Key functions include:

```python
# Get list of available models
async def get_available_models() -> List[str]:
    process = await asyncio.create_subprocess_exec(
        "docker", "model", "list",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    # Process output to extract model names
    ...

# Generate text from a model
async def generate(self, prompt: str, **kwargs) -> str:
    process = await asyncio.create_subprocess_exec(
        "docker", "model", "run", self.model, prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    # Process and return the output
    ...

# Stream text from a model
async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
    process = await asyncio.create_subprocess_exec(
        "docker", "model", "run", self.model, prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    # Read and yield chunks of output
    ...
```

### Integration with Ultra Backend

The Ultra backend is updated to create the appropriate adapter based on configuration:

```python
# In backend/services/llm_config_service.py
if os.environ.get("USE_MODEL_RUNNER") == "true":
    model_runner_type = os.environ.get("MODEL_RUNNER_TYPE", "cli")

    if model_runner_type == "cli":
        # Create CLI adapter
        adapter = await create_modelrunner_cli_adapter(model)
    else:
        # Create API adapter (legacy)
        adapter = await create_modelrunner_adapter(model)

    return adapter
```

## Configuration

### Environment Variables

| Variable          | Description                        | Default | Required |
| ----------------- | ---------------------------------- | ------- | -------- |
| USE_MODEL_RUNNER  | Enable/disable Docker Model Runner | false   | No       |
| MODEL_RUNNER_TYPE | Adapter type (cli)                 | cli     | No       |

### Example Configuration

```bash
# Enable Docker Model Runner with CLI adapter
export USE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=cli
```

## Testing

### Test Scripts

Two test scripts are provided to verify the integration:

1. **test_modelrunner_cli.py**: Tests the CLI adapter functionality

   ```bash
   python3 scripts/test_modelrunner_cli.py
   ```

2. **verify_modelrunner_mvp.py**: Comprehensive verification script
   ```bash
   python3 scripts/verify_modelrunner_mvp.py
   ```

### Test Cases

The test suite in `tests/test_docker_modelrunner.py` includes tests for:

- Model discovery
- Text generation
- Streaming generation
- Error handling
- Integration with the Ultra backend

## Error Handling

The integration includes robust error handling:

1. **Connection Issues**: Handled with clear error messages and troubleshooting tips
2. **Missing Models**: Detected and reported with instructions for pulling models
3. **Generation Errors**: Captured and reported from both stdout and stderr
4. **Graceful Degradation**: Falls back to mock services when Docker Model Runner is unavailable

## Performance Considerations

### Model Selection

Different models have different performance characteristics:

- **Small models** (ai/smollm2): Fast, lower resource usage, good for development
- **Medium models**: Balance of quality and performance
- **Large models**: Higher quality but require more resources

### Resource Usage

Docker Model Runner manages resources automatically, but consider:

- Memory requirements increase with model size
- GPU acceleration significantly improves performance when available
- Concurrent requests may require additional resources

## Security Considerations

1. **Local Operation**: All models run locally, eliminating API key exposure
2. **Input Validation**: All user inputs are validated before being passed to models
3. **Resource Limits**: Docker Desktop enforces resource limits on models

## Known Limitations

1. The CLI adapter has slightly higher latency than API-based approaches
2. Some advanced model parameters aren't directly supported
3. Models must be pulled manually before use

## Troubleshooting

### Common Issues

1. **Docker Desktop Not Running**

   - Error: "Cannot connect to the Docker daemon"
   - Solution: Start Docker Desktop

2. **Model Not Found**

   - Error: "Unknown model" or empty model list
   - Solution: Pull the model using `docker model pull ai/smollm2`

3. **Generation Timeout**
   - Error: "Command timed out"
   - Solution: Increase timeout or use a smaller model

## Future Directions

1. **Enhanced Model Management**: Automatic model pulling and management
2. **Performance Optimization**: Caching and parallel processing
3. **UI Integration**: Direct model management from Ultra UI
4. **Advanced Parameters**: Support for more model-specific parameters
