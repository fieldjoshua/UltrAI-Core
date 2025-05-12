# Local LLM Setup Guide

This guide explains how to set up and use local AI models with Ultra using Docker Model Runner.

## Overview

Ultra supports running AI models locally on your machine using Docker Desktop's Model Runner feature. This allows you to:

- Run AI models without external API keys
- Work offline without internet connectivity
- Experiment with various open-source models
- Reduce costs associated with external API usage

## Prerequisites

Before starting, you'll need:

- Docker Desktop installed (version 4.25 or later)
- At least 4GB of available RAM (8GB+ recommended)
- 1GB+ of free disk space for small models (more for larger models)
- Admin access to install Docker Desktop if not already installed

## Installation Steps

### 1. Install Docker Desktop

If you don't already have Docker Desktop installed:

1. Download from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Follow the installation instructions for your operating system
3. Start Docker Desktop

### 2. Verify Docker Model Runner

Docker Model Runner is included with Docker Desktop. Verify it's working:

```bash
docker model status
```

You should see a message confirming Docker Model Runner is running.

### 3. Pull a Model

Pull a small model to start with:

```bash
docker model pull ai/smollm2
```

This will download a small model (approximately 250MB).

### 4. Verify Model Availability

Check that the model is available:

```bash
docker model list
```

You should see your pulled model in the list.

### 5. Test the Model

Test the model with a simple prompt:

```bash
docker model run ai/smollm2 "Hello, how are you today?"
```

You should receive a response from the model.

## Using Local Models with Ultra

### Configuration

To use Docker Model Runner with Ultra:

1. Set the required environment variables:

```bash
export USE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=cli
```

2. Start the Ultra backend:

```bash
python3 -m uvicorn backend.app:app --reload
```

### Making API Requests

When making requests to Ultra, include your local model in the models array:

```json
{
  "prompt": "What is machine learning?",
  "models": ["ai/smollm2"],
  "options": {"context": ""}
}
```

The response will include output from your local model.

### Testing Local Models

Ultra includes a verification script to test the Docker Model Runner integration:

```bash
python3 scripts/test_modelrunner_cli.py
```

This script checks:
- Docker Model Runner status
- Available models
- Text generation
- Streaming generation

## Available Models

Docker Model Runner supports a variety of open-source models. Some recommended models include:

| Model | Size | Description | Command |
|-------|------|-------------|---------|
| ai/smollm2 | ~250MB | Small, fast model good for testing | `docker model pull ai/smollm2` |
| ai/mistral | ~4GB | Mid-sized, good general performance | `docker model pull ai/mistral` |
| ai/llama3 | ~8GB | Larger model with better quality | `docker model pull ai/llama3` |

To see all available models:

```bash
docker model list
```

## Performance Tips

### Model Selection

- Start with small models like ai/smollm2 for testing
- Larger models provide better responses but require more resources
- GPU acceleration significantly improves performance when available

### Resource Management

- Close resource-intensive applications when running large models
- Docker Desktop allows configuring resource limits in settings
- Monitor performance with Docker Desktop dashboard

## Troubleshooting

### Docker Model Runner Not Running

**Symptoms:** Error connecting to Docker Model Runner, "Docker Model Runner is not running" message

**Solutions:**
1. Ensure Docker Desktop is running
2. Restart Docker Desktop
3. Run `docker model status` to check status

### Model Not Found

**Symptoms:** Empty model list, "model not found" errors

**Solutions:**
1. Pull the model again: `docker model pull ai/smollm2`
2. Check available models: `docker model list`
3. Verify disk space for model downloads

### Generation Errors

**Symptoms:** Error messages during text generation, timeouts

**Solutions:**
1. Try a smaller model
2. Restart Docker Model Runner
3. Check system resources (memory, CPU usage)
4. Verify prompt format and length

### Ultra Integration Issues

**Symptoms:** Ultra doesn't use local models despite configuration

**Solutions:**
1. Verify environment variables:
   ```bash
   echo $USE_MODEL_RUNNER
   echo $MODEL_RUNNER_TYPE
   ```
2. Run the test script: `python3 scripts/test_modelrunner_cli.py`
3. Check Ultra logs for errors

## Advanced Usage

### Pulling Custom Models

You can pull specific models:

```bash
docker model pull owner/model
```

### Running with GPU Acceleration

If your system has compatible GPU (NVIDIA or Apple Silicon):

1. Docker will automatically use GPU acceleration when available
2. No additional configuration is needed
3. Performance improvement is significant (3-10x faster)

### Using Multiple Models

You can use multiple local models in the same request:

```json
{
  "prompt": "What is machine learning?",
  "models": ["ai/smollm2", "ai/mistral"],
  "options": {"context": ""}
}
```

Ultra will run the query on all specified models and return the results.

## Additional Resources

- [Docker Model CLI Reference](https://docs.docker.com/engine/reference/commandline/model/)
- [Ultra Model Integration Documentation](/documentation/technical/integrations/docker_model_runner.md)
- [Docker Desktop Documentation](https://docs.docker.com/desktop/)