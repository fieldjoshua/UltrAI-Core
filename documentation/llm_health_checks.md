# LLM Provider Health Checks and Circuit Breakers

This document describes the health check system for LLM providers in the Ultra system. It explains how the health checks work, how to use them, and how circuit breakers help prevent cascading failures in production.

## Overview

The LLM provider health check system provides:

1. Real-time health status of LLM API providers (OpenAI, Anthropic, Google)
2. Circuit breaker pattern implementation to prevent repeated failures
3. REST API endpoints to check health status
4. Integration with the health service for system-wide health monitoring

## Health Check Endpoints

The following endpoints are available:

### 1. General Health Check
```
GET /api/health
```
Returns overall system health, including a summary of services.

For detailed health information including LLM providers:
```
GET /api/health?detail=true
```

### 2. LLM Provider Health Check
```
GET /api/health/llm/providers
```
Returns detailed status for each configured LLM provider, including:
- API connectivity
- API key validity
- Dependency availability
- Response time

### 3. Circuit Breaker Status
```
GET /api/health/circuit-breakers
```
Returns status of all circuit breakers, including:
- Current state (closed, open, half-open)
- Failure count
- Recovery timeouts
- Last success/failure timestamps

## Circuit Breaker Pattern

The system implements a circuit breaker pattern for LLM providers to prevent cascading failures in production environments. The circuit breaker has three states:

1. **CLOSED**: Normal operation, failure count tracked
2. **OPEN**: Service requests blocked for a cooling period
3. **HALF-OPEN**: Testing if service has recovered

When an LLM provider fails repeatedly (default: 3 failures), the circuit opens and subsequent requests are short-circuited (failed fast) for a recovery period (default: 5 minutes). This prevents:

- Wasting resources on requests likely to fail
- Degrading user experience with slow responses
- Overwhelming external API services during outages

## Testing With Production APIs

When testing the production environment using `scripts/test_production.sh`, the script now includes LLM provider health checks. If API keys are provided in `.env.api_keys`, the script will:

1. Test the health check endpoint for LLM providers
2. Display detailed health information
3. Check circuit breaker status if any providers are failing

Example output:
```
$ ./scripts/test_production.sh

LLM Provider health response:
{
  "status": "healthy",
  "message": "2 LLM providers available",
  "providers_count": 3,
  "available_count": 2,
  "providers": {
    "openai": {
      "status": "healthy",
      "message": "openai API connection successful",
      "provider": "openai",
      "dependency_available": true,
      "api_key_configured": true,
      "duration_ms": 325,
      "timestamp": "2025-05-13T10:15:23.456789"
    },
    "anthropic": {
      "status": "healthy",
      "message": "anthropic API connection successful",
      "provider": "anthropic",
      "dependency_available": true,
      "api_key_configured": true,
      "duration_ms": 412,
      "timestamp": "2025-05-13T10:15:23.567890"
    },
    "google": {
      "status": "unavailable",
      "message": "google API authentication failed",
      "provider": "google",
      "dependency_available": true,
      "api_key_configured": true,
      "api_key_valid": false,
      "status_code": 401,
      "duration_ms": 278,
      "timestamp": "2025-05-13T10:15:23.678901"
    }
  },
  "environment": "production",
  "mock_mode": false
}
```

## Monitoring and Alerting

In a production environment, it's recommended to:

1. Periodically poll the health check endpoints (e.g., every 1-5 minutes)
2. Set up alerts for degraded or unavailable LLM providers
3. Monitor circuit breaker open events to identify persistent issues with providers

## Implementation Details

The LLM provider health checks are implemented in:
- `backend/utils/health_check.py`: Core health check and circuit breaker implementation
- `backend/services/health_service.py`: Health service integration
- `backend/routes/health_routes.py`: REST API endpoints

The circuit breaker implementation has the following default parameters:
- Failure threshold: 3 consecutive failures
- Recovery timeout: 300 seconds (5 minutes)
- Half-open max calls: 1 test call per recovery attempt

## Future Improvements

Planned improvements to the health check system:

1. **Per-provider configuration**: Different thresholds and timeouts for each provider
2. **Provider fallbacks**: Automatically redirect to alternative providers when primary is unavailable
3. **Detailed monitoring metrics**: Track response times, error rates, and costs
4. **Intelligent throttling**: Adjust request rates based on provider health
5. **API usage quotas**: Monitor API usage against quotas to prevent billing surprises