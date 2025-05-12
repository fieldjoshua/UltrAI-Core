# Docker Model Runner Quick Start Guide

This guide provides the minimum steps needed to get Docker Model Runner working with Ultra. It focuses on essential functionality for a minimum viable product (MVP).

## 1. Install Docker Model Runner

### Prerequisites

- Docker Desktop installed and running (version 4.25+)
- Admin access to install Docker Desktop

### Verify Docker Desktop

Make sure Docker Desktop is installed and running:

```bash
docker --version
```

You should see something like `Docker version 24.0.6, build ed223bc`.

### Docker Model Integration

Docker Desktop now includes integrated Model Runner functionality via the `docker model` command. No extensions are needed.

## 2. Verify Docker Model Runner

Check if Docker Model Runner is running:

```bash
docker model status
```

You should see a message like:
```
Docker Model Runner is running

Status:
llama.cpp: running llama.cpp latest-metal
```

If it's not running, Docker will start it automatically when you run model commands.

## 3. Pull a Small Model

For MVP functionality, pull a small model like ai/smollm2:

```bash
docker model pull ai/smollm2
```

This will download the model (approximately 250MB).

## 4. List Available Models

Verify the model is available:

```bash
docker model list
```

You should see something like:
```
MODEL NAME  PARAMETERS  QUANTIZATION    ARCHITECTURE  MODEL ID      CREATED      SIZE       
ai/smollm2  361.82 M    IQ2_XXS/Q4_K_M  llama         354bf30d0aa3  5 weeks ago  256.35 MiB
```

## 5. Test Basic Response Generation

Test that the model can generate responses:

```bash
docker model run ai/smollm2 "What is Docker Model Runner in one sentence?"
```

You should see a response generated from the model.

## 6. Test the CLI Adapter

Ultra includes a CLI adapter that uses the Docker Model commands. Test it with:

```bash
python3 scripts/test_modelrunner_cli.py
```

This will:
1. Check if Docker Model Runner is running
2. List available models
3. Test generation with a simple prompt
4. Test streaming generation

## 7. Run Ultra with Docker Model Runner

Start the Ultra backend with Docker Model Runner enabled:

```bash
# Export necessary environment variables
export USE_MODEL_RUNNER=true
export MODEL_RUNNER_TYPE=cli

# Start the backend
python3 -m uvicorn backend.app:app --reload
```

## 8. Test Through Ultra API

Make a simple request to the Ultra API using Docker Model Runner:

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is machine learning?","models":["ai/smollm2"],"options":{"context":""}}'
```

You should receive a response from the model through the Ultra platform.

## Troubleshooting

### Docker Model Runner Not Available

If Docker Model Runner is not running:

1. Check Docker Desktop is running
2. Try restarting Docker Desktop
3. Check Docker Model Runner status:
   ```bash
   docker model status
   ```

### Model Not Found

If the model is not available:

1. List available models:
   ```bash
   docker model list
   ```
2. Try pulling the model again:
   ```bash
   docker model pull ai/smollm2
   ```

### Ultra Backend Errors

If the Ultra backend has issues:

1. Verify environment variables:
   ```bash
   echo $USE_MODEL_RUNNER
   echo $MODEL_RUNNER_TYPE
   ```
2. Check that Docker Model Runner is running:
   ```bash
   docker model status
   ```
3. Test the CLI adapter directly:
   ```bash
   python3 scripts/test_modelrunner_cli.py
   ```

## Next Steps

Once the MVP is working, you can:

1. Pull additional models (llama3:8b, mistral:7b)
2. Configure more options in docker-compose.yml
3. Enable GPU acceleration for better performance
4. Test streaming responses
5. Compare responses between different models

## Command Reference

### Start Docker Model Runner

```bash
docker-compose --profile with-model-runner up -d
```

### Stop Docker Model Runner

```bash
docker-compose --profile with-model-runner down
```

### View Docker Model Runner Logs

```bash
docker logs ultra-model-runner
```

### Check Available Models

```bash
curl http://localhost:8080/v1/models
```

### Test Single Model

```bash
python3 scripts/test_modelrunner.py --generate --model phi3:mini --prompt "Your prompt here"
```