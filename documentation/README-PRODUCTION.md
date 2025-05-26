# Ultra Production Environment

This guide covers running the Ultra system in production mode with real services instead of mock mode.

## Overview

Ultra supports multiple environments:

- **Development**: Uses mock LLM responses for rapid development (default)
- **Production**: Connects to actual LLM providers via their APIs
- **Testing**: Specific configuration for automated testing

## Getting Started with Production Mode

### 1. Prerequisites

To run Ultra in production mode, you need:

- Valid API keys for at least one LLM provider (OpenAI, Anthropic, or Google)
- Proper environment configuration
- Database and cache services (if using persistence features)

### 2. Setting Up Production Environment

#### Method 1: Toggle Environment Script

```bash
# Switch to production environment
./scripts/toggle_environment.sh production

# Verify the change
cat .env | grep ENVIRONMENT
```

#### Method 2: Manual Setup

```bash
# Copy the production environment template
cp .env.production .env

# Edit environment variables
nano .env

# Ensure these settings are configured:
# ENVIRONMENT=production
# USE_MOCK=false
# MOCK_MODE=false
```

### 3. Adding API Keys

Add your LLM provider API keys to the environment file:

```
# OpenAI
OPENAI_API_KEY=your_openai_key_here
OPENAI_ORG_ID=your_openai_org_id_here  # Optional

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google
GOOGLE_API_KEY=your_google_key_here
```

### 4. Testing Production Configuration

Run the production test script to verify your setup:

```bash
# Run the production test script
./scripts/test_production.sh
```

Review the test results to ensure all essential services are working.

### Testing with Real LLM APIs

To test with real LLM providers, create a `.env.api_keys` file with your API keys:

```
# OpenAI (GPT-4, etc.)
OPENAI_API_KEY="your-openai-key"

# Anthropic (Claude)
ANTHROPIC_API_KEY="your-anthropic-key"

# Google (Gemini)
GOOGLE_API_KEY="your-google-key"
```

The test script will automatically detect available API keys and run tests with the corresponding providers.

For detailed instructions, see [Real LLM Testing Guide](./documentation/testing/real_llm_testing.md).

## Environment Configuration

Key environment variables for production:

| Variable          | Description           | Production Value |
| ----------------- | --------------------- | ---------------- |
| ENVIRONMENT       | Current environment   | production       |
| USE_MOCK          | Use mock responses    | false            |
| MOCK_MODE         | Enable mock mode      | false            |
| DEBUG             | Enable debug mode     | false            |
| LOG_LEVEL         | Logging level         | info             |
| API_HOST          | API host              | 0.0.0.0          |
| API_PORT          | API port              | 8000             |
| ENABLE_AUTH       | Enable authentication | true             |
| ENABLE_RATE_LIMIT | Enable rate limiting  | true             |

## Authentication in Production

Production mode requires proper authentication:

1. **API Keys**: Required for accessing protected endpoints
2. **JWT Tokens**: Used for user authentication
3. **Rate Limiting**: Applied based on IP and user ID

For testing, you can use the `X-Test-Mode: true` header to bypass authentication.

## Health Monitoring

The health endpoint provides system status information:

```bash
# Check basic health
curl http://localhost:8085/api/health

# Check detailed health
curl http://localhost:8085/api/health?detail=true

# Check LLM provider health
curl http://localhost:8085/api/health/llm/providers

# Check circuit breaker status
curl http://localhost:8085/api/health/circuit-breakers
```

### LLM Provider Health Checks

The system includes health checks for LLM providers, which:

1. Monitor connectivity to OpenAI, Anthropic, Google, and other providers
2. Verify API key validity and provider availability
3. Provide detailed status and response time metrics
4. Implement circuit breakers to prevent cascading failures

The circuit breaker pattern automatically stops requests to failing providers after multiple failures, then tests recovery after a timeout period. This prevents:

- Wasting resources on requests that will likely fail
- Degrading user experience with slow responses
- Overwhelming external API services during outages

For more details, see [LLM Health Checks and Circuit Breakers](./documentation/llm_health_checks.md).

## Deployment

For production deployment, consider:

1. Using Docker containers for isolation
2. Setting up a reverse proxy for HTTPS
3. Configuring proper logging
4. Setting up monitoring and alerting

### Docker Deployment

```bash
# Build the production Docker image
docker build -t ultra:production --build-arg ENVIRONMENT=production .

# Run the container
docker run -p 8085:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e ANTHROPIC_API_KEY=your_key_here \
  ultra:production
```

## Known Limitations

1. Some endpoints are still under development:

   - `/api/available-models`: To be fixed

2. Authentication system needs comprehensive testing

3. Error handling for production scenarios needs improvement

## Troubleshooting

- **401 Unauthorized**: Authentication issue, check JWT tokens or API keys
- **404 Not Found for available-models**: Known issue, being fixed
- **500 Internal Server Error**: Check logs for details
- **LLM Provider Errors**: Verify API keys and provider status

## Next Steps

See the implementation plan for ongoing work:

- [Implementation Plan](./documentation/implementation_plan.md)
- [Production Readiness Documentation](./documentation/production_readiness.md)
- [Testing Guide](./documentation/testing/production_testing.md)
- [LLM Health Checks and Circuit Breakers](./documentation/llm_health_checks.md)
