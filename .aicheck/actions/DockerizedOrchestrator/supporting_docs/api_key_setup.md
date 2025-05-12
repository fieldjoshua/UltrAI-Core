# Setting Up API Keys for Real LLM Usage in Docker

This document explains how to set up API keys for using real LLM providers with the dockerized orchestration system.

## Overview

The orchestrator can use several LLM providers including:

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Cohere
- Mistral

To use these providers, you need to:

1. Obtain API keys from the respective providers
2. Make these keys available to the Docker containers

## Option 1: Using a .env File (Recommended)

The most secure way to provide API keys is through a `.env` file that Docker Compose will automatically load.

1. Create a `.env` file in the project root:

```bash
touch .env
chmod 600 .env  # Restrict permissions for security
```

2. Add your API keys to the file:

```
# LLM API Keys
OPENAI_API_KEY=sk-...your-openai-key...
ANTHROPIC_API_KEY=sk-ant-...your-anthropic-key...
GOOGLE_API_KEY=...your-google-key...
COHERE_API_KEY=...your-cohere-key...
MISTRAL_API_KEY=...your-mistral-key...

# Orchestrator Settings
USE_MOCK=false
```

3. Docker Compose will automatically load these variables when you start containers.

## Option 2: Environment Variables in docker-compose.yml

You can add the API keys directly in the `docker-compose.yml` file, but this is less secure as it might get committed to version control.

```yaml
services:
  backend:
    # ...existing configuration...
    environment:
      # ...existing environment variables...
      - OPENAI_API_KEY=sk-...your-openai-key...
      - ANTHROPIC_API_KEY=sk-ant-...your-anthropic-key...
      - GOOGLE_API_KEY=...your-google-key...
      - USE_MOCK=false
```

## Option 3: Pass Environment Variables at Runtime

You can pass environment variables when running the Docker commands:

```bash
OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-... docker compose up backend
```

Or when executing the orchestrator script:

```bash
OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-... ./scripts/run-docker-orchestrator.sh
```

## Switching Between Providers

To specify which provider to use for a particular run:

```bash
# Use OpenAI's GPT-4
./scripts/run-docker-orchestrator.sh comparative "Your prompt here" openai-gpt4o

# Use Anthropic's Claude 
./scripts/run-docker-orchestrator.sh comparative "Your prompt here" anthropic-claude

# Use both
./scripts/run-docker-orchestrator.sh comparative "Your prompt here" openai-gpt4o,anthropic-claude
```

## Verifying API Key Configuration

To verify your API keys are properly configured:

```bash
# Check environment variables in the container
docker compose exec backend env | grep -E 'OPENAI|ANTHROPIC|GOOGLE|COHERE|MISTRAL'

# Test a specific provider
docker compose exec -e PYTHONPATH=/app backend python -c "from src.adapters.adapter_factory import create_adapter; adapter = create_adapter('openai-gpt4o'); print('Adapter created successfully' if adapter else 'Failed to create adapter')"
```

## Troubleshooting

If you encounter issues with API keys:

1. **Keys not available in container**:
   - Ensure `.env` file is in the project root
   - Check file permissions (should be readable)
   - Verify Docker Compose is loading the file

2. **Authentication errors**:
   - Confirm API keys are valid and active
   - Check for typos in key values
   - Verify you have billing set up with the provider

3. **Rate limiting**:
   - Some providers have usage limits
   - Check your provider dashboard for quota information
   - Implement retry logic or reduce request frequency

## Security Best Practices

1. **Never commit API keys to version control**:
   - Add `.env` to your `.gitignore`
   - Use environment variables in CI/CD pipelines

2. **Restrict file permissions**:
   - `chmod 600 .env` to make it readable only by the owner

3. **Use dedicated keys for development**:
   - Create separate API keys for development and production
   - Apply usage limits to development keys

4. **Rotate keys periodically**:
   - Change API keys regularly
   - Revoke any keys that might have been exposed