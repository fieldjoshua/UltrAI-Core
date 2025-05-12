# Docker Model Runner Integration Architecture

## Overview

This document outlines the architecture for integrating Docker Model Runner with the Ultra platform. The integration will allow Ultra to use local open-source LLMs alongside cloud-based providers, enhancing development capabilities and providing offline functionality.

## System Components

### 1. Docker Model Runner Service

The Docker Model Runner service will be a containerized component that:

- Runs various open-source LLMs locally
- Exposes an OpenAI-compatible API endpoint
- Manages model loading/unloading
- Handles AI inference requests

### 2. Docker Model Runner Adapter

A new adapter in the Ultra backend that:

- Communicates with the Docker Model Runner API
- Translates Ultra requests to Docker Model Runner format
- Normalizes Docker Model Runner responses to match other providers
- Handles error conditions and fallbacks

### 3. Configuration System

Updates to the configuration system to:

- Define available Docker Model Runner models
- Toggle between local and cloud models
- Set model-specific parameters
- Define fallback strategies

## Integration Architecture

```
┌─────────────────────────────────────┐
│            Ultra Frontend           │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│            Ultra Backend            │
│                                     │
│  ┌─────────────┐   ┌─────────────┐  │
│  │ LLM         │   │Model        │  │
│  │ Orchestrator│◄──┤Selection    │  │
│  └──────┬──────┘   └─────────────┘  │
│         │                           │
│         ▼                           │
│  ┌─────────────────────────────┐    │
│  │       Provider Adapters     │    │
│  │                             │    │
│  │  ┌─────┐ ┌─────┐ ┌───────┐  │    │
│  │  │OpenAI│ │Claude│ │Google│  │    │
│  │  └─────┘ └─────┘ └───────┘  │    │
│  │                             │    │
│  │  ┌─────────────────────┐    │    │
│  │  │Docker Model Runner  │    │    │
│  │  │Adapter (new)        │    │    │
│  │  └─────────────────────┘    │    │
│  └──────────────┬──────────────┘    │
└─────────────────┼──────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     Docker Model Runner Service     │
│                                     │
│  ┌─────────────┐   ┌─────────────┐  │
│  │ API         │   │Model        │  │
│  │ Endpoint    │◄──┤Management   │  │
│  └──────┬──────┘   └─────────────┘  │
│         │                           │
│         ▼                           │
│  ┌─────────────────────────────┐    │
│  │        Model Registry       │    │
│  │                             │    │
│  │  ┌─────┐ ┌─────┐ ┌───────┐  │    │
│  │  │Llama│ │Mistral│ │Phi   │  │    │
│  │  └─────┘ └─────┘ └───────┘  │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

## Request Flow

1. **User Request**:
   - User submits a prompt to Ultra for analysis
   - User selects models to use (including local models)

2. **Model Selection**:
   - Ultra determines which models to use
   - If local model is selected, routes to Docker Model Runner adapter

3. **Adapter Processing**:
   - Adapter formats the request for Docker Model Runner
   - Sends request to Docker Model Runner service
   - Receives response and normalizes format

4. **Result Handling**:
   - Response is combined with other model responses
   - Results are displayed to the user
   - Metrics are collected on model performance

## Docker Compose Integration

The Docker Model Runner service will be integrated with the existing Docker Compose setup by adding a new service definition:

```yaml
# Docker Model Runner Service
model-runner:
  image: docker/modelrunner:latest
  container_name: ultra-model-runner
  volumes:
    - model-runner-data:/root/.cache/modelrunner
  ports:
    - "${MODEL_RUNNER_PORT:-8080}:8080"
  environment:
    - GPU_ENABLED=${GPU_ENABLED:-false}
    - DEFAULT_MODEL=${DEFAULT_MODEL:-llama3:8b}
    - MODELS=${MODELS:-llama3:8b,phi3:mini,mistral:7b}
  networks:
    - ultra-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/v1/models"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 15s
  restart: ${RESTART_POLICY:-unless-stopped}
```

## API Compatibility

Docker Model Runner provides an OpenAI-compatible API, making integration straightforward. The key endpoints are:

1. **Models endpoint**: `/v1/models`
   - Lists available models

2. **Completion endpoint**: `/v1/chat/completions`
   - For chat completions (most common use case)

3. **Embeddings endpoint**: `/v1/embeddings`
   - For generating embeddings (if supported by the model)

The adapter will implement these endpoints and translate responses to match the format expected by Ultra.

## Feature Flags and Configuration

New environment variables will be added:

```
# Docker Model Runner Configuration
ENABLE_MODEL_RUNNER=true
MODEL_RUNNER_URL=http://model-runner:8080
DEFAULT_LOCAL_MODEL=llama3:8b
AVAILABLE_LOCAL_MODELS=llama3:8b,phi3:mini,mistral:7b
USE_LOCAL_MODELS_WHEN_OFFLINE=true
LOCAL_MODEL_TIMEOUT=60000
```

## Data Flow Considerations

### Prompt Template Compatibility

Different models may require adjustments to prompt formatting. The adapter will handle model-specific prompt engineering to ensure optimal results across different model architectures.

### Response Normalization

Responses from different models vary in structure and formatting. The adapter will normalize responses to provide a consistent interface to the rest of the Ultra system.

### Error Handling

The adapter will implement robust error handling to manage:

- Model loading failures
- Timeout issues
- Resource constraints
- Malformed requests or responses

## Offline Mode Support

The integration will support a complete offline development workflow:

1. Docker Model Runner models are downloaded and cached during initial setup
2. When offline, Ultra automatically routes requests to local models
3. All features function without external API access

## Performance Considerations

### Memory Management

Models can be large (several GB), so the adapter will need to:

- Support lazy loading of models
- Implement model unloading when not in use
- Provide configuration for memory limits

### CPU/GPU Utilization

The integration will:

- Support both CPU and GPU inference
- Allow configuration of resource limits
- Implement queuing for high-load scenarios

## Logging and Monitoring

The integration will include:

- Detailed logging of model operations
- Performance metrics collection
- Error rate tracking
- Resource utilization monitoring

## Testing Approach

The integration will be tested with:

1. **Unit tests**:
   - Adapter functionality
   - Request/response formatting
   - Error handling

2. **Integration tests**:
   - End-to-end request flow
   - Docker Compose service interaction
   - Multiple model comparison

3. **Performance tests**:
   - Response time benchmarking
   - Memory usage profiling
   - Load testing

## Security Considerations

The implementation will ensure:

- No sensitive data is stored in model caches
- Network isolation between services
- Proper error handling to prevent information leakage
- Validation of all inputs to prevent injection attacks