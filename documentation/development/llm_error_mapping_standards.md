# LLM Provider Error Mapping Standards

## Overview

This document defines the standardized error mapping across all LLM provider adapters to ensure consistent error handling and user experience.

## Error Response Format

All LLM adapters return errors in the following format:
```json
{
  "generated_text": "Error: [Error message]"
}
```

## Standardized Error Categories

### 1. Timeout Errors

**Pattern**: `Error: [Provider] request timed out.`

- OpenAI: `"Error: OpenAI request timed out."`
- Anthropic: `"Error: Anthropic request timed out."`
- Google Gemini: `"Error: Google Gemini request timed out."`
- HuggingFace: `"Error: HuggingFace request timed out."`

**Trigger**: `httpx.ReadTimeout` exception

### 2. Authentication Errors (401)

**Pattern**: `Error: [Provider] API authentication failed. Check API key.`

- OpenAI: `"Error: OpenAI API authentication failed. Check API key."`
- Anthropic: `"Error: Anthropic API authentication failed. Check API key."`
- Google Gemini: `"Error: Google API authentication failed. Check API key."`
- HuggingFace: `"Error: HuggingFace API authentication failed."`

**Trigger**: HTTP 401 status code

### 3. Model Not Found (404)

**Pattern**: `Error: Model [model_name] not found in [Provider] API`

- OpenAI: `"Error: Model {model} not found in OpenAI API"`
- Anthropic: `"Error: Model {model} not found in Anthropic API"`
- Google Gemini: `"Error: Model {model} not found or Google API key invalid"`
- HuggingFace: `"Error: Model {model} not found on HuggingFace."`

**Trigger**: HTTP 404 status code

### 4. Rate Limiting (429)

**Pattern**: `Error: [Provider] API rate limit exceeded. Please retry later.`

- OpenAI: `"Error: OpenAI API rate limit exceeded. Please retry later."`
- Anthropic: Handled as generic HTTP error (should be standardized)
- Google Gemini: `"Error: Google API quota exceeded. Please retry later."`
- HuggingFace: Handled as generic HTTP error (should be standardized)

**Trigger**: HTTP 429 status code

### 5. Bad Request (400)

**Pattern**: `Error: Invalid request to [Provider] API`

- OpenAI: Handled as generic HTTP error
- Anthropic: Handled as generic HTTP error
- Google Gemini: `"Error: Invalid request to Google Gemini API."`
- HuggingFace: Handled as generic HTTP error

**Trigger**: HTTP 400 status code

### 6. Service Errors (500-503)

**Pattern**: `Error: [Provider] service temporarily unavailable.`

- OpenAI: Handled as generic HTTP error (should be standardized)
- Anthropic: Handled as generic HTTP error (should be standardized)
- Google Gemini: `"Error: Google Gemini service temporarily unavailable."`
- HuggingFace: `"Error: HuggingFace service unavailable."`

**Trigger**: HTTP 500, 502, 503 status codes

### 7. Generic HTTP Errors

**Pattern**: `Error: [Provider] API HTTP [status_code]: [error_details]`

Examples:
- `"Error: OpenAI API HTTP 403: Forbidden"`
- `"Error: Anthropic API HTTP 500: Internal Server Error"`

**Trigger**: Any unhandled HTTP status error

### 8. Generic Exceptions

**Pattern**: `Error: An issue occurred with the [Provider] API: [error_details]`

Examples:
- `"Error: An issue occurred with the OpenAI API: Connection refused"`
- `"Error: An issue occurred with the Anthropic API: DNS resolution failed"`

**Trigger**: Any unhandled exception

## Provider Health Manager Integration

When errors occur, the provider health manager should track:

1. **Error Type Classification**:
   - Transient errors (timeouts, rate limits, 503s) → Provider marked as "degraded"
   - Persistent errors (auth, 404s) → Provider marked as "unhealthy" after threshold
   - Network errors → Provider marked as "unhealthy" immediately

2. **Recovery Windows**:
   - Rate limit errors: 5 minute recovery window
   - Timeout errors: 2 minute recovery window
   - Auth/config errors: Manual intervention required

## Recommendations for Improvement

### 1. Standardize Rate Limit Handling

Currently only OpenAI and Google explicitly handle 429 errors. All providers should:
```python
elif e.response.status_code == 429:
    return {
        "generated_text": f"Error: {provider_name} API rate limit exceeded. Please retry later."
    }
```

### 2. Standardize Service Error Handling

Add explicit handling for 500-503 errors:
```python
elif e.response.status_code in [500, 502, 503]:
    return {
        "generated_text": f"Error: {provider_name} service temporarily unavailable."
    }
```

### 3. Add Error Metadata

Consider adding error metadata for better tracking:
```python
return {
    "generated_text": f"Error: {error_message}",
    "error_metadata": {
        "provider": provider_name,
        "error_type": "rate_limit|timeout|auth|not_found|service_error|unknown",
        "status_code": status_code,
        "retryable": True|False,
        "retry_after": seconds  # For rate limits
    }
}
```

### 4. Consistent Provider Names

Ensure consistent provider naming across all error messages:
- OpenAI (not "OpenAI API")
- Anthropic (not "Anthropic API")
- Google Gemini (not "Google API" or "Gemini")
- HuggingFace (not "Hugging Face" or "HF")

## Testing Error Scenarios

Each adapter should have tests for:
1. Timeout scenarios (mock slow responses)
2. Authentication failures (invalid API keys)
3. Model not found (invalid model names)
4. Rate limiting (429 responses)
5. Service errors (500/503 responses)
6. Network errors (connection failures)

## Current Status

As of the latest review:

✅ **Well Standardized**:
- Timeout errors
- Authentication errors
- Model not found errors
- Generic exception handling

⚠️ **Needs Improvement**:
- Rate limit handling (inconsistent across providers)
- Service error handling (mostly generic)
- Bad request handling (inconsistent)

🔴 **Missing**:
- Error metadata for health tracking
- Retry guidance in error messages
- Consistent provider naming