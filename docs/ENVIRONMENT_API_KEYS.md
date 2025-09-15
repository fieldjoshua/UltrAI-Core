# Environment-Specific API Key Configuration

## Overview

To prevent rate limit collisions between different environments (development, staging, production), it's crucial to use separate API keys for each environment. This guide explains how to properly configure environment-specific API keys.

## Why Separate API Keys?

1. **Rate Limit Isolation**: Each environment gets its own rate limit quota
2. **Usage Tracking**: Monitor costs and usage per environment
3. **Security**: Compromised dev keys don't affect production
4. **Testing**: Can test rate limit handling without affecting production

## Configuration Guide

### 1. Create Environment-Specific Keys

For each provider, create separate API keys:

#### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create keys with clear names:
   - `ultrai-dev`
   - `ultrai-staging`
   - `ultrai-prod`

#### Anthropic
1. Go to https://console.anthropic.com/settings/keys
2. Create keys with clear names:
   - `ultrai-development`
   - `ultrai-staging`
   - `ultrai-production`

#### Google Cloud
1. Go to https://console.cloud.google.com/apis/credentials
2. Create separate projects or API keys per environment

### 2. Environment Configuration Files

Create separate `.env` files for each environment:

#### `.env.development` (local development)
```bash
ENVIRONMENT=development
OPENAI_API_KEY=sk-dev-...
ANTHROPIC_API_KEY=sk-ant-dev-...
GOOGLE_API_KEY=AIza-dev-...
```

#### `.env.staging`
```bash
ENVIRONMENT=staging
OPENAI_API_KEY=sk-staging-...
ANTHROPIC_API_KEY=sk-ant-staging-...
GOOGLE_API_KEY=AIza-staging-...
```

#### `.env.production`
```bash
ENVIRONMENT=production
OPENAI_API_KEY=sk-prod-...
ANTHROPIC_API_KEY=sk-ant-prod-...
GOOGLE_API_KEY=AIza-prod-...
```

### 3. Render.com Configuration

For cloud deployments on Render:

1. **Staging Service** (`ultrai-staging-api`):
   - Set staging-specific API keys in environment variables
   - Use lower rate limits for cost control

2. **Production Service** (`ultrai-core`):
   - Set production-specific API keys
   - Use higher rate limits for better performance

### 4. Rate Limit Configuration

Configure different rate limits per environment:

```bash
# Development
OPENAI_RATE_LIMIT_RPM=20  # Requests per minute
ANTHROPIC_RATE_LIMIT_RPM=20

# Staging
OPENAI_RATE_LIMIT_RPM=60
ANTHROPIC_RATE_LIMIT_RPM=60

# Production
OPENAI_RATE_LIMIT_RPM=500
ANTHROPIC_RATE_LIMIT_RPM=500
```

### 5. Health Check TTLs

Configure health check cache TTLs per environment:

```bash
# Development - shorter TTLs for testing
MODEL_HEALTH_CACHE_TTL_MINUTES=2
PROVIDER_RECOVERY_WINDOW_MINUTES=2

# Production - longer TTLs for stability
MODEL_HEALTH_CACHE_TTL_MINUTES=10
PROVIDER_RECOVERY_WINDOW_MINUTES=5
```

## Best Practices

1. **Never share keys between environments**
2. **Use environment variables, not hardcoded values**
3. **Rotate keys regularly**
4. **Monitor usage per environment**
5. **Set up alerts for rate limit approaches**

## Monitoring

Track API usage per environment:
- OpenAI: https://platform.openai.com/usage
- Anthropic: https://console.anthropic.com/usage
- Google: https://console.cloud.google.com/apis/dashboard

## Rate Limit Handling

### Automatic Provider Fallback

When rate limits are encountered, the system automatically:

1. **Detects rate limit errors** from any provider
2. **Marks the provider as rate-limited** temporarily
3. **Suggests alternative providers** in priority order:
   - Anthropic and Google (Primary)
   - OpenAI (Secondary)
   - HuggingFace (Backup)
4. **Automatically switches models** for ongoing requests

### Provider Priorities

Configure provider priorities via environment variables:
```bash
# Set provider priorities (1=highest, 4=lowest)
ANTHROPIC_PRIORITY=1
GOOGLE_PRIORITY=1
OPENAI_PRIORITY=2
HUGGINGFACE_PRIORITY=4
```

### Rate Limit Recovery

- Providers are automatically retried after the recovery window
- Default recovery window: 5 minutes
- Configure via `PROVIDER_RECOVERY_WINDOW_MINUTES`

## Emergency Procedures

If rate limits are hit in production:
1. Check if staging/dev keys are being used accidentally
2. Verify correct environment variables are loaded
3. Monitor the automatic fallback to alternative providers
4. Consider temporarily increasing limits with your provider
5. Use the `/monitor` endpoint to view real-time provider status