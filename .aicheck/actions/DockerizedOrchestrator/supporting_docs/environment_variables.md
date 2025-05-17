# Environment Variables for Dockerized Orchestrator

This document provides a comprehensive list of environment variables used by the orchestrator within the Docker environment, explaining their purpose and recommended values.

## Core Environment Variables

| Variable      | Purpose                             | Default       | Recommended                                                 |
| ------------- | ----------------------------------- | ------------- | ----------------------------------------------------------- |
| `ENVIRONMENT` | Sets the deployment environment     | `development` | `development` for local Docker, `production` for deployment |
| `LOG_LEVEL`   | Controls logging verbosity          | `debug`       | `debug` for development, `info` for production              |
| `DEBUG`       | Enables additional debugging output | `true`        | `true` for development, `false` for production              |

## LLM API Keys

| Variable            | Purpose                               | Default                  | Recommended                             |
| ------------------- | ------------------------------------- | ------------------------ | --------------------------------------- |
| `OPENAI_API_KEY`    | Authentication for OpenAI services    | None                     | Valid API key if using OpenAI models    |
| `ANTHROPIC_API_KEY` | Authentication for Anthropic services | None                     | Valid API key if using Anthropic models |
| `GOOGLE_API_KEY`    | Authentication for Google AI services | None                     | Valid API key if using Google models    |
| `DEEPSEEK_API_KEY`  | Authentication for DeepSeek services  | None                     | Valid API key if using DeepSeek models  |
| `OLLAMA_BASE_URL`   | URL for Ollama service                | `http://localhost:11434` | Appropriate URL for Ollama if used      |

## Mock Mode Settings

| Variable              | Purpose                                          | Default | Recommended                                                 |
| --------------------- | ------------------------------------------------ | ------- | ----------------------------------------------------------- |
| `USE_MOCK`            | Enables mock responses instead of real API calls | `true`  | `true` for testing without API keys, `false` for real usage |
| `ENABLE_MOCK_LLM`     | Specifically enables LLM mocking                 | `true`  | Same as `USE_MOCK`                                          |
| `MOCK_RESPONSE_DELAY` | Simulated delay in mock responses (ms)           | `500`   | `100-1000` for realistic simulation                         |

## Orchestrator Configuration

| Variable                        | Purpose                                   | Default                  | Recommended                               |
| ------------------------------- | ----------------------------------------- | ------------------------ | ----------------------------------------- |
| `ORCHESTRATOR_ENABLE`           | Enables the orchestrator system           | `true`                   | `true` to use orchestrator                |
| `ORCHESTRATOR_DEFAULT_ANALYSIS` | Default analysis type                     | `comparative`            | `comparative` or `factual` based on needs |
| `ORCHESTRATOR_MODULE_PATH`      | Path to orchestrator modules in container | `/app/src/orchestration` | Use default unless structure changes      |
| `ORCHESTRATOR_CONFIG_PATH`      | Path to orchestrator config               | `/app/src/config`        | Use default unless structure changes      |
| `ORCHESTRATOR_MAX_TOKENS`       | Maximum tokens for responses              | `4000`                   | `1000-8000` based on model capabilities   |
| `ORCHESTRATOR_TIMEOUT`          | API call timeout in seconds               | `60`                     | `30-120` based on expected response times |
| `ORCHESTRATOR_RETRY_COUNT`      | Number of retries for failed API calls    | `3`                      | `1-5` based on reliability needs          |

## Cache Configuration

| Variable         | Purpose                          | Default          | Recommended                                                       |
| ---------------- | -------------------------------- | ---------------- | ----------------------------------------------------------------- |
| `ENABLE_CACHE`   | Enables response caching         | `true`           | `true` for development, consider `false` for some production uses |
| `CACHE_TTL`      | Cache time-to-live in seconds    | `3600`           | `3600` (1 hour) for development, adjust for production            |
| `REDIS_HOST`     | Redis hostname for cache storage | `redis`          | Use default in Docker environment                                 |
| `REDIS_PORT`     | Redis port                       | `6379`           | Use default unless customized                                     |
| `REDIS_PASSWORD` | Redis authentication             | `redis_password` | Change for production                                             |

## Analysis Module Settings

| Variable                     | Purpose                             | Default            | Recommended                                                     |
| ---------------------------- | ----------------------------------- | ------------------ | --------------------------------------------------------------- |
| `COMPARATIVE_ANALYSIS_MODEL` | Model used for comparative analysis | `anthropic-claude` | High-capability model like `anthropic-claude` or `openai-gpt4o` |
| `FACTUAL_ANALYSIS_MODEL`     | Model used for factual analysis     | `openai-gpt4o`     | Model with strong knowledge like `openai-gpt4o`                 |
| `ANALYSIS_TIMEOUT`           | Timeout for analysis operations     | `120`              | `60-180` based on complexity                                    |
| `ENABLE_DETAILED_ANALYSIS`   | Enables more detailed analysis      | `true`             | `true` for comprehensive results                                |

## Docker-specific Settings

| Variable       | Purpose                   | Default                     | Recommended                                          |
| -------------- | ------------------------- | --------------------------- | ---------------------------------------------------- |
| `PYTHONPATH`   | Python module search path | `/app`                      | Include project root: `/app`                         |
| `VITE_API_URL` | Frontend API endpoint     | `http://localhost:8000/api` | Match backend port and path                          |
| `NODE_ENV`     | Node.js environment       | `development`               | `development` for local, `production` for deployment |

## Setting Environment Variables

Environment variables can be set in multiple ways:

1. **In .env file** (recommended for development):

   ```
   OPENAI_API_KEY=your_key_here
   USE_MOCK=true
   ```

2. **In docker-compose.yml** (for service-specific settings):

   ```yaml
   environment:
     - OPENAI_API_KEY=${OPENAI_API_KEY:-}
     - USE_MOCK=${USE_MOCK:-true}
   ```

3. **Command-line override** (for temporary testing):
   ```bash
   docker compose exec -e USE_MOCK=false backend bash
   ```

## Variable Precedence

When the same variable is defined in multiple places, the precedence order is:

1. Command-line override
2. docker-compose.yml
3. .env file
4. Default values

## Example Configurations

### Development with Mock Mode

```
ENVIRONMENT=development
LOG_LEVEL=debug
DEBUG=true
USE_MOCK=true
ENABLE_MOCK_LLM=true
ORCHESTRATOR_ENABLE=true
ORCHESTRATOR_DEFAULT_ANALYSIS=comparative
ENABLE_CACHE=true
```

### Development with Real APIs

```
ENVIRONMENT=development
LOG_LEVEL=debug
DEBUG=true
USE_MOCK=false
ENABLE_MOCK_LLM=false
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
ORCHESTRATOR_ENABLE=true
ORCHESTRATOR_DEFAULT_ANALYSIS=comparative
ENABLE_CACHE=true
```

### Production Configuration

```
ENVIRONMENT=production
LOG_LEVEL=info
DEBUG=false
USE_MOCK=false
ENABLE_MOCK_LLM=false
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
ORCHESTRATOR_ENABLE=true
ORCHESTRATOR_DEFAULT_ANALYSIS=comparative
ENABLE_CACHE=true
CACHE_TTL=7200
REDIS_PASSWORD=strong_production_password
ORCHESTRATOR_TIMEOUT=90
ORCHESTRATOR_RETRY_COUNT=3
```
