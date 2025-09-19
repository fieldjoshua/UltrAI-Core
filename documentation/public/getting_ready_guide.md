# Getting READY: A Guide to Service Readiness

This guide helps you troubleshoot common issues that prevent the Ultra service from reaching a `READY` or `healthy` state. The service requires a minimum number of healthy AI providers to function correctly.

## Common Readiness Failures

### 1. Missing API Keys

**Symptom:** The service fails to start or the `/api/orchestrator/status` endpoint shows `service_available: false` with messages about missing providers.

**Error Message (503 Payload):**
```json
{
  "detail": "UltraAI requires at least 3 models and providers: ['anthropic', 'google', 'openai']; missing: ['google']; available_models=2",
  "error_details": {
    "providers_present": ["anthropic", "openai"],
    "required_providers": ["anthropic", "google", "openai"]
  }
}
```

**Fix:** Ensure that the API keys for the required providers (`openai`, `anthropic`, `google`) are correctly configured as environment variables.

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

### 2. Provider is Down or Unresponsive

**Symptom:** The service is `degraded` or `unavailable`, and the `provider_health` section of the status response shows one or more providers as `unhealthy`.

**Status Response (`/api/orchestrator/status`):**
```json
{
  "provider_health": {
    "available_providers": ["openai", "anthropic"],
    "details": {
      "google": { "status": "unhealthy", "last_error": "Request timed out" }
    }
  }
}
```

**Fix:**
1. **Check Provider Status:** Visit the official status pages for the affected providers (e.g., status.openai.com) to see if there is an ongoing incident.
2. **Check Network Connectivity:** Ensure your server can reach the provider's API endpoints. Firewall or network issues can prevent connections.
3. **Wait and Retry:** Temporary provider issues usually resolve on their own. The service will periodically probe for health and will automatically recover when the provider is back online.

### 3. Insufficient Healthy Models

**Symptom:** Even if API keys are present, the service may be unavailable if not enough models pass their health checks.

**Status Response (`/api/orchestrator/status`):**
```json
{
  "status": "unavailable",
  "service_available": false,
  "message": "Service unavailable. Only 2 model(s) available, 3 required"
}
```

**Fix:** This is often a consequence of a provider being down. Follow the steps for "Provider is Down or Unresponsive". If all providers appear healthy, this might indicate a configuration issue or a problem with the specific models being used. Check the service logs for more detailed error messages.
