# Docker Model Runner Installation Guide

This guide provides step-by-step instructions for installing and configuring Docker Model Runner for use with Ultra.

## Prerequisites

- Docker Desktop 4.40 or later
- Mac with Apple Silicon or Windows with NVIDIA GPUs
- At least 8GB of RAM (16GB recommended)
- 20GB+ of free disk space for models

## Installation Steps

### 1. Install Docker Desktop

If you don't already have Docker Desktop installed:

1. Download Docker Desktop from [the official website](https://www.docker.com/products/docker-desktop/)
2. Install and launch Docker Desktop
3. Verify it's running by checking the Docker icon in your system tray/menu bar

### 2. Enable Docker Extensions

Docker Model Runner is available as an extension for Docker Desktop:

1. Open Docker Desktop
2. Click on the Settings/Preferences icon
3. Go to "Extensions"
4. Ensure "Allow installation from Docker Marketplace" is checked
5. If you want to allow the modelrunner extension from Docker Hub, also check "Allow installation from Docker Hub"

### 3. Install Docker Model Runner

#### Method 1: Through Docker Desktop GUI

1. Open Docker Desktop
2. Click on "Extensions" in the left sidebar
3. Click on "Marketplace"
4. Search for "Model Runner"
5. Click "Install" on the Docker Model Runner extension
   - For Mac with Apple Silicon: Install "Model Runner (Metal)"
   - For Windows with NVIDIA GPUs: Install "Model Runner (CUDA)"

#### Method 2: Through Command Line

If you've allowed installation from Docker Hub:

For Apple Silicon Macs:

```bash
docker extension install docker/modelrunner-metal:latest
```

For Windows with NVIDIA GPUs:

```bash
docker extension install docker/modelrunner-cuda:latest
```

### 4. Verify Installation

After installation, verify that Docker Model Runner is working:

1. In Docker Desktop, click on "Extensions" in the left sidebar
2. You should see "Model Runner" in your installed extensions
3. Click on the "Model Runner" extension to open its interface
4. You should see the Model Runner dashboard

Alternatively, verify from the command line:

```bash
docker extension ls
```

You should see the modelrunner extension in the list.

### 5. Test Docker Model Runner

Let's test if Docker Model Runner is working properly:

1. From the Model Runner interface in Docker Desktop, click on "Run Model"
2. Choose a small model like "Phi-3 Mini" for the initial test
3. Enter a simple prompt like "Hello, how are you?"
4. Click "Submit" and verify you get a response

Or test via command line API:

```bash
# Check available models
curl http://localhost:8080/v1/models

# Test a simple completion
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:mini",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 100
  }'
```

## Configuring Docker Model Runner

### Basic Configuration

Docker Model Runner works out of the box, but you can configure it in Docker Desktop:

1. Go to the Model Runner extension interface
2. Click on "Settings"
3. Configure options like:
   - Default model
   - Maximum memory usage
   - GPU settings (if applicable)

### Advanced Configuration

For more advanced configuration, you can set environment variables when using Docker Model Runner in Docker Compose:

```yaml
model-runner:
  environment:
    - GPU_ENABLED=true # For GPU acceleration
    - DEFAULT_MODEL=llama3:8b # Default model to load
    - MODELS=llama3:8b,phi3:mini,mistral:7b # Models to make available
    - CACHE_DIR=/modelrunner/cache # Cache directory for models
```

## Troubleshooting

### Common Issues

#### Model Runner Not Starting

If the Model Runner service doesn't start:

1. Check Docker Desktop logs
2. Ensure you have enough disk space
3. Restart Docker Desktop

#### Slow Model Downloads

Initial model downloads can be slow:

1. Be patient during first use as models are downloaded
2. Check your internet connection
3. Consider using smaller models first (e.g., Phi-3 Mini instead of Llama 3)

#### Out of Memory Errors

If you encounter out of memory errors:

1. Try smaller models
2. Close other applications to free memory
3. Adjust memory limits in Docker Desktop settings

#### API Connection Issues

If you can't connect to the API:

1. Confirm Model Runner is running
2. Check the port (default is 8080)
3. Use `localhost` rather than `127.0.0.1` if you're having issues

## Testing with Ultra Helper Scripts

Ultra includes several helper scripts to simplify testing and using Docker Model Runner:

### 1. Verify Connection and Models

To quickly check if Docker Model Runner is available and list available models:

```bash
python3 scripts/test_modelrunner.py
```

### 2. Test Generation with a Specific Model

To test generating a response with a specific model:

```bash
python3 scripts/test_modelrunner.py --generate --model phi3:mini
```

You can customize the prompt:

```bash
python3 scripts/test_modelrunner.py --generate --model phi3:mini --prompt "Explain quantum computing"
```

### 3. Pull Models for Local Use

To pull specific models for use with Ultra:

```bash
python3 scripts/pull_modelrunner_models.py --models phi3:mini,llama3:8b
```

This script will:

- Connect to Docker Model Runner
- Check which models are already available
- Pull any requested models that aren't already downloaded
- Monitor the download progress

### 4. Run Automated Tests

To run the automated test suite for the Docker Model Runner integration:

```bash
python3 -m pytest tests/test_docker_modelrunner.py -v
```

## Next Steps

After installing and testing Docker Model Runner:

1. Configure Docker Compose to include the Model Runner service
2. Set up the Ultra backend to communicate with Model Runner
3. Use the test scripts to verify the integration
4. Refer to the testing guide for advanced testing scenarios

For detailed instructions on these steps, refer to the other documentation in this action.
