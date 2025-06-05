# Docker Model Runner Testing Guide

This document provides guidance on testing the Docker Model Runner integration with Ultra. It includes information on test scripts, verification methods, and troubleshooting steps.

## Prerequisites

Before testing, ensure:

1. Docker Desktop is installed and running
2. Docker Model Runner extension is installed in Docker Desktop
3. At least one model is pulled and available in Docker Model Runner
4. Docker Compose environment is configured correctly

## Quick Connection Test

To quickly verify Docker Model Runner connectivity:

```bash
python3 scripts/test_modelrunner.py
```

This script will:

- Check if the Docker Model Runner API is reachable
- List available models
- Provide troubleshooting tips if the connection fails

To test model response generation:

```bash
python3 scripts/test_modelrunner.py --generate --model phi3:mini
```

## Running Unit Tests

The test suite for Docker Model Runner integration can be run with:

```bash
python3 -m pytest tests/test_docker_modelrunner.py -v
```

These tests will:

- Test adapter creation and configuration
- Test response generation
- Test streaming capabilities
- Test fallback behavior in the mock LLM service

If Docker Model Runner is not available, tests requiring a live connection will be skipped.

## Manual Testing

For manual testing of the Ultra platform with Docker Model Runner:

1. Start the system with Docker Model Runner enabled:

   ```bash
   docker-compose --profile with-model-runner up -d
   ```

2. In a separate terminal, start the backend with Model Runner support:

   ```bash
   USE_MODEL_RUNNER=true python3 -m uvicorn backend.app:app --reload
   ```

3. Test an analysis request that will use the Model Runner:

   ```bash
   curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"prompt":"What is machine learning?","models":["phi3:mini"],"options":{"context":""}}'
   ```

4. Alternatively, use the frontend UI to submit an analysis request and observe the Docker Model Runner logs:
   ```bash
   docker logs -f ultra-model-runner
   ```

## Troubleshooting

### Docker Model Runner Not Available

If the Docker Model Runner is not available, check:

1. Docker Desktop status:

   ```bash
   docker info
   ```

2. Docker Model Runner extension status in Docker Desktop

   - Open Docker Desktop → Extensions → Model Runner
   - Check if it shows as "Installed" and "Running"

3. Docker Model Runner logs:

   ```bash
   docker logs ultra-model-runner
   ```

4. Network accessibility:
   ```bash
   curl http://localhost:8080/v1/models
   ```

### Model Loading Issues

If models fail to load:

1. Check Model Runner logs for errors:

   ```bash
   docker logs ultra-model-runner
   ```

2. Verify model is downloaded and available:

   ```bash
   curl http://localhost:8080/v1/models
   ```

3. Check available disk space and memory:

   ```bash
   df -h
   free -m
   ```

4. Try pulling the model manually via Docker Desktop UI

### Mock Service Fallback Testing

To test the fallback mechanism:

1. Start the backend with Model Runner support but no running Model Runner:

   ```bash
   USE_MODEL_RUNNER=true MODEL_RUNNER_URL=http://localhost:9999 python3 -m uvicorn backend.app:app --reload
   ```

2. Submit an analysis request - the system should fall back to static responses:

   ```bash
   curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"prompt":"What is machine learning?","models":["phi3:mini"],"options":{"context":""}}'
   ```

3. Check logs for fallback messages

## Performance Testing

For performance testing with Docker Model Runner:

1. Test response times with different models:

   ```bash
   time python3 scripts/test_modelrunner.py --generate --model phi3:mini
   time python3 scripts/test_modelrunner.py --generate --model llama3:8b
   ```

2. Test concurrent requests:
   ```bash
   for i in {1..5}; do
     python3 scripts/test_modelrunner.py --generate --prompt "Explain concept $i" &
   done
   ```

## Verifying Successful Integration

The Docker Model Runner integration is working correctly when:

1. The system can detect and list available models from Docker Model Runner
2. Analysis requests using Docker Model Runner models return generated responses
3. The system gracefully falls back to mock responses when Docker Model Runner is unavailable
4. Streaming responses work correctly with the UI

## Next Steps After Testing

After successful testing:

1. Document any issues or limitations discovered
2. Update configuration recommendations based on performance observations
3. Add new models to the compatibility matrix
4. Create user-facing documentation on using local models with Ultra
