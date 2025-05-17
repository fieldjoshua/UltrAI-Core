# Environment Configuration for Production

This document outlines the environment configuration requirements for running Ultra in production.

## Environment Variables

The following environment variables should be configured for production deployments:

### Core Configuration

| Variable       | Description                                               | Default       | Required |
| -------------- | --------------------------------------------------------- | ------------- | -------- |
| `ENVIRONMENT`  | Deployment environment (development, testing, production) | `development` | Yes      |
| `DEBUG`        | Enable debug mode                                         | `false`       | No       |
| `LOG_LEVEL`    | Logging level (debug, info, warning, error)               | `info`        | No       |
| `API_HOST`     | API host                                                  | `0.0.0.0`     | No       |
| `API_PORT`     | API port                                                  | `8000`        | No       |
| `CORS_ORIGINS` | Allowed CORS origins                                      | `*`           | Yes      |
| `SECRET_KEY`   | Secret key for encryption                                 | None          | Yes      |

### Authentication

| Variable                          | Description                        | Default | Required |
| --------------------------------- | ---------------------------------- | ------- | -------- |
| `JWT_SECRET`                      | Secret for JWT token signing       | None    | Yes      |
| `JWT_ALGORITHM`                   | Algorithm for JWT token signing    | `HS256` | No       |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration in minutes | `30`    | No       |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token expiration in days   | `7`     | No       |
| `ENABLE_AUTH`                     | Enable authentication              | `true`  | No       |

### Database

| Variable                | Description                               | Default                | Required |
| ----------------------- | ----------------------------------------- | ---------------------- | -------- |
| `DATABASE_URL`          | Database connection URL                   | `sqlite:///./ultra.db` | Yes      |
| `DATABASE_POOL_SIZE`    | Database connection pool size             | `5`                    | No       |
| `DATABASE_MAX_OVERFLOW` | Maximum number of connections to overflow | `10`                   | No       |
| `DATABASE_POOL_TIMEOUT` | Connection pool timeout in seconds        | `30`                   | No       |

### LLM Providers

| Variable            | Description                             | Default  | Required |
| ------------------- | --------------------------------------- | -------- | -------- |
| `OPENAI_API_KEY`    | OpenAI API key                          | None     | Yes\*    |
| `ANTHROPIC_API_KEY` | Anthropic API key                       | None     | Yes\*    |
| `GOOGLE_API_KEY`    | Google Generative AI API key            | None     | Yes\*    |
| `DEFAULT_PROVIDER`  | Default LLM provider                    | `openai` | No       |
| `DEFAULT_MODEL`     | Default model for the selected provider | `gpt-4o` | No       |

\*At least one LLM provider API key is required.

### Redis Cache

| Variable       | Description          | Default                    | Required |
| -------------- | -------------------- | -------------------------- | -------- |
| `REDIS_URL`    | Redis connection URL | `redis://localhost:6379/0` | No       |
| `ENABLE_CACHE` | Enable Redis caching | `true`                     | No       |
| `CACHE_TTL`    | Cache TTL in seconds | `3600`                     | No       |

### Rate Limiting

| Variable              | Description                                | Default   | Required |
| --------------------- | ------------------------------------------ | --------- | -------- |
| `ENABLE_RATE_LIMIT`   | Enable rate limiting                       | `true`    | No       |
| `RATE_LIMIT_STRATEGY` | Rate limiting strategy (fixed, sliding)    | `sliding` | No       |
| `RATE_LIMIT_STORAGE`  | Rate limit storage backend (memory, redis) | `memory`  | No       |

### Storage

| Variable                | Description                 | Default            | Required |
| ----------------------- | --------------------------- | ------------------ | -------- |
| `DOCUMENT_STORAGE_PATH` | Path for document storage   | `document_storage` | No       |
| `MAX_DOCUMENT_SIZE_MB`  | Maximum document size in MB | `10`               | No       |

### Security

| Variable                  | Description                | Default | Required |
| ------------------------- | -------------------------- | ------- | -------- |
| `ENABLE_SECURITY_HEADERS` | Enable security headers    | `true`  | No       |
| `ENABLE_HTTPS_REDIRECT`   | Redirect HTTP to HTTPS     | `true`  | No       |
| `API_KEY_ENCRYPTION_KEY`  | Key for API key encryption | None    | Yes      |

## Environment Profiles

The system supports different environment profiles for easier configuration:

### Development

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug
DATABASE_URL=sqlite:///./ultra_dev.db
ENABLE_AUTH=false
USE_MOCK=true
```

### Testing

```bash
ENVIRONMENT=testing
DEBUG=false
LOG_LEVEL=info
DATABASE_URL=sqlite:///./ultra_test.db
ENABLE_AUTH=true
USE_MOCK=false
```

### Production

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
DATABASE_URL=postgresql://user:password@db:5432/ultra
ENABLE_AUTH=true
USE_MOCK=false
ENABLE_HTTPS_REDIRECT=true
CORS_ORIGINS=https://example.com
```

## Configuration Validation

The system should validate configurations at startup:

1. Check that required environment variables are set
2. Validate format of variables like URLs and API keys
3. Test connections to critical services (database, Redis)
4. Report clear error messages for configuration issues

## Secrets Management

For production, secrets should be managed securely:

1. Use environment variables for secrets, not config files
2. Consider using a secrets management service like HashiCorp Vault or AWS Secrets Manager
3. Rotate secrets regularly
4. Use different secrets for different environments
5. Limit access to production secrets

## Configuration File

For local development, a .env file can be used. For production, environment variables should be set in the deployment environment.

Example .env file:

```
# Core
ENVIRONMENT=production
LOG_LEVEL=info
API_PORT=8000
CORS_ORIGINS=https://example.com
SECRET_KEY=your-secret-key

# Auth
JWT_SECRET=your-jwt-secret
ENABLE_AUTH=true

# Database
DATABASE_URL=postgresql://user:password@db:5432/ultra

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-opus-20240229

# Redis
REDIS_URL=redis://redis:6379/0
ENABLE_CACHE=true

# Security
ENABLE_SECURITY_HEADERS=true
ENABLE_HTTPS_REDIRECT=true
API_KEY_ENCRYPTION_KEY=your-encryption-key
```
