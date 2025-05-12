# Environment Variables

This document describes the environment variables used by the Ultra application.

## Overview

Ultra uses environment variables for configuration. These variables can be set in various ways:

1. In an `.env` file in the project root directory
2. In environment-specific files like `.env.development`, `.env.testing`, or `.env.production`
3. Directly in the shell environment

We provide a script `scripts/set-env.sh` to easily switch between environments:

```bash
# Set up development environment
./scripts/set-env.sh development

# Set up testing environment
./scripts/set-env.sh testing

# Set up production environment
./scripts/set-env.sh production
```

## Environment Profiles

Ultra supports different environment profiles to make configuration easier:

### Development

Development environment is optimized for local development with mock services enabled by default:

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug
USE_MOCK=true
MOCK_MODE=true
ENABLE_AUTH=false
DATABASE_URL=sqlite:///./ultra_dev.db
```

### Testing

Testing environment is used for running automated tests:

```bash
ENVIRONMENT=testing
TESTING=true
DEBUG=false
LOG_LEVEL=info
USE_MOCK=true
MOCK_MODE=true
ENABLE_AUTH=true
DATABASE_URL=sqlite:///:memory:
```

### Production

Production environment is optimized for security and performance:

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
USE_MOCK=false
MOCK_MODE=false
ENABLE_AUTH=true
DATABASE_URL=postgresql://user:password@db:5432/ultra
ENABLE_HTTPS_REDIRECT=true
CORS_ORIGINS=https://app.ultrai.app,https://api.ultrai.app
```

## Configuration Categories

### Core Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment (development, testing, production) | `development` | Yes |
| `DEBUG` | Enable debug mode | `false` | No |
| `LOG_LEVEL` | Logging level (debug, info, warning, error) | `info` | No |
| `API_HOST` | API host | `0.0.0.0` | No |
| `API_PORT` | API port | `8000` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | Yes |
| `SECRET_KEY` | Secret key for encryption | None | Yes |

### Authentication

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_AUTH` | Enable authentication | `true` | No |
| `JWT_SECRET` | Secret for JWT token signing | None | Yes |
| `JWT_ALGORITHM` | Algorithm for JWT token signing | `HS256` | No |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration in minutes | `30` | No |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration in days | `7` | No |

### Database

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./ultra.db` | Yes |
| `DATABASE_POOL_SIZE` | Database connection pool size | `5` | No |
| `DATABASE_MAX_OVERFLOW` | Maximum number of connections to overflow | `10` | No |
| `DATABASE_POOL_TIMEOUT` | Connection pool timeout in seconds | `30` | No |
| `POSTGRES_USER` | PostgreSQL username (for Docker) | `ultra` | No |
| `POSTGRES_PASSWORD` | PostgreSQL password (for Docker) | None | No |
| `POSTGRES_DB` | PostgreSQL database name (for Docker) | `ultra` | No |

### Redis Cache

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` | No |
| `REDIS_PASSWORD` | Redis password (for Docker) | None | No |
| `ENABLE_CACHE` | Enable Redis caching | `true` | No |
| `CACHE_TTL` | Cache TTL in seconds | `3600` | No |

### LLM Providers

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | None | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | None | Yes* |
| `GOOGLE_API_KEY` | Google Generative AI API key | None | Yes* |
| `MISTRAL_API_KEY` | Mistral API key | None | No |
| `DEEPSEEK_API_KEY` | DeepSeek API key | None | No |
| `COHERE_API_KEY` | Cohere API key | None | No |
| `DEFAULT_PROVIDER` | Default LLM provider | `openai` | No |
| `DEFAULT_MODEL` | Default model for the selected provider | `gpt-4o` | No |
| `DEFAULT_LEAD_MODEL` | Default lead model for orchestration | `anthropic-claude` | No |
| `DEFAULT_ANALYSIS_TYPE` | Default analysis type | `comparative` | No |

*At least one LLM provider API key is required in production mode.

### Storage

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DOCUMENT_STORAGE_PATH` | Path for document storage | `document_storage` | No |
| `TEMP_UPLOADS_PATH` | Path for temporary uploads | `temp_uploads` | No |
| `TEMP_PATH` | Path for temporary files | `temp` | No |
| `LOGS_PATH` | Path for log files | `logs` | No |

### Security

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENABLE_SECURITY_HEADERS` | Enable security headers | `true` | No |
| `ENABLE_RATE_LIMIT` | Enable rate limiting | `true` | No |
| `ENABLE_HTTPS_REDIRECT` | Redirect HTTP to HTTPS | `false` | No |
| `API_KEY_ENCRYPTION_KEY` | Key for API key encryption | None | Yes |

### Mock Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USE_MOCK` | Enable mock mode | `false` | No |
| `MOCK_MODE` | Enable mock mode (alias) | `false` | No |
| `ENABLE_MOCK_LLM` | Enable mock LLM responses | `false` | No |

### Monitoring

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SENTRY_DSN` | Sentry DSN for error tracking | None | No |
| `SENTRY_ENVIRONMENT` | Sentry environment | Same as `ENVIRONMENT` | No |
| `SENTRY_TRACES_SAMPLE_RATE` | Sentry trace sample rate | `1.0` | No |

### Frontend Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_URL` | API URL for frontend | `http://localhost:8000` | No |

## Generating Secure Keys

For security-related variables like `SECRET_KEY`, `JWT_SECRET`, and `API_KEY_ENCRYPTION_KEY`, you should use strong random values.

In Python, you can generate a secure key with:

```python
import secrets
print(secrets.token_urlsafe(32))
```

For API key encryption, you need a valid Fernet key:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

## Docker Environment

When running with Docker, environment variables can be specified in:

1. docker-compose.yml file
2. .env file used by docker-compose
3. Environment variables passed to docker-compose command

Example docker-compose.yml:

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env.production
    environment:
      - DATABASE_URL=postgresql://ultra:${POSTGRES_PASSWORD}@postgres:5432/ultra
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
```

## Secrets Management

For production, consider using a secrets management solution like:

1. Docker secrets
2. Kubernetes secrets
3. HashiCorp Vault
4. AWS Secrets Manager
5. Google Secret Manager

Never commit sensitive information like API keys to your repository.

## Validation

Configuration validation happens during application startup. If required environment variables are missing or invalid in production, the application will exit with an error.

In development and testing environments, the application will continue with warnings.