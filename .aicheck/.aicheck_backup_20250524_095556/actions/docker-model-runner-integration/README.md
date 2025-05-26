# Docker Model Runner Integration

This directory contains documentation and supporting files for the Docker Model Runner integration with Ultra.

## Overview

Docker Model Runner integration enables Ultra to use locally-run open-source LLMs through Docker Desktop's Model Runner extension. This provides a powerful development and testing capability without requiring external API keys or internet access.

## Quick Start

For the fastest way to get started with Docker Model Runner, run:

```bash
python3 scripts/verify_modelrunner_mvp.py
```

This script will:

1. Check if Docker Desktop is running
2. Verify Model Runner extension is installed
3. Check Model Runner API connectivity
4. Verify or pull a model
5. Test basic response generation

## Documentation

The following documentation is available:

- [Integration Architecture](supporting_docs/integration_architecture.md) - Overview of the integration design
- [Installation Guide](supporting_docs/installation_guide.md) - How to install and configure Docker Model Runner
- [Testing Guide](supporting_docs/testing_guide.md) - How to test the Docker Model Runner integration
- [Model Compatibility](supporting_docs/model_compatibility.md) - Model compatibility information
- [Usage Examples](supporting_docs/usage_examples.md) - Examples of using Docker Model Runner with Ultra
- [Quickstart Guide](supporting_docs/quickstart.md) - Minimal steps for MVP functionality
- [Implementation Summary](supporting_docs/implementation_summary.md) - Summary of the implementation
- [Completion Report](supporting_docs/completion_report.md) - Final report on the integration
- [PR Checklist](supporting_docs/pr_checklist.md) - Checklist for the integration PR

## Key Files

The Docker Model Runner integration consists of the following key files:

- `docker-compose.yml` - Docker Compose configuration with Model Runner service
- `src/models/docker_modelrunner_adapter.py` - Adapter for Docker Model Runner
- `scripts/test_modelrunner.py` - Script for testing Docker Model Runner connectivity
- `scripts/pull_modelrunner_models.py` - Script for pulling models
- `scripts/verify_modelrunner_mvp.py` - Script for verifying MVP functionality
- `tests/test_docker_modelrunner.py` - Test suite for Docker Model Runner

## Environment Variables

The following environment variables control Docker Model Runner integration:

| Variable          | Description                                      | Default                        |
| ----------------- | ------------------------------------------------ | ------------------------------ |
| USE_MODEL_RUNNER  | Enable/disable Docker Model Runner               | false                          |
| MODEL_RUNNER_URL  | URL for Docker Model Runner API                  | http://localhost:8080          |
| MODEL_RUNNER_PORT | Port for Docker Model Runner service             | 8080                           |
| DEFAULT_MODEL     | Default model to use                             | phi3:mini                      |
| AVAILABLE_MODELS  | Comma-separated list of models to make available | phi3:mini,llama3:8b,mistral:7b |
| GPU_ENABLED       | Enable/disable GPU acceleration                  | false                          |

## Usage

To use Docker Model Runner with Ultra:

1. Ensure Docker Desktop is running with Model Runner extension installed
2. Start Ultra with Docker Model Runner enabled:
   ```bash
   export USE_MODEL_RUNNER=true
   python3 -m uvicorn backend.app:app --reload
   ```
3. Use local models in your API requests:
   ```json
   {
     "prompt": "What is machine learning?",
     "models": ["phi3:mini"],
     "options": { "context": "" }
   }
   ```

## Next Steps

While the MVP functionality is complete, the following enhancements could be considered:

1. Automatic model pulling based on configuration
2. Performance optimizations for larger models
3. Enhanced UI integration
4. Support for additional model types

## Support

For issues or questions about Docker Model Runner integration, please refer to the [Testing Guide](supporting_docs/testing_guide.md) for troubleshooting information.
