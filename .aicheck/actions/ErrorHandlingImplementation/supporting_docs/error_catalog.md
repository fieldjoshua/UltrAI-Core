# Error Catalog

This document defines the standard error types, codes, and user-facing messages for the Ultra system.

## Error Structure

All errors in the system follow this standard structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-facing error message",
    "request_id": "unique-request-identifier",
    "timestamp": "2025-05-11T10:15:30Z",
    "details": {
      // Optional additional details specific to error type
    }
  }
}
```

## Error Categories

Errors are categorized into the following groups:

1. **Input Validation Errors** (400 range)
   - Invalid input format or content
   - Missing required fields
   - Value constraints not met

2. **Authentication Errors** (401, 403)
   - Authentication failures
   - Authorization failures
   - Token issues

3. **Resource Errors** (404, 409, 410)
   - Resource not found
   - Resource conflict
   - Resource no longer available

4. **Rate Limiting and Quota Errors** (429)
   - Rate limit exceeded
   - Quota exhausted
   - Usage limit reached

5. **External Service Errors** (502, 503, 504)
   - LLM provider errors
   - Database service errors
   - Third-party API errors

6. **Internal System Errors** (500)
   - Unexpected exceptions
   - System failures
   - Infrastructure issues

## Standard Error Codes

### Input Validation Errors

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `INVALID_REQUEST` | 400 | The request is invalid. {detail} | General invalid request |
| `MISSING_FIELD` | 400 | The required field '{field}' is missing. | Missing required field |
| `INVALID_FIELD` | 400 | The field '{field}' is invalid. {detail} | Field fails validation |
| `INVALID_FORMAT` | 400 | The format of '{field}' is invalid. {detail} | Invalid format |
| `VALUE_TOO_LARGE` | 400 | The value of '{field}' exceeds the maximum allowed size. | Value size limit exceeded |
| `VALUE_TOO_SMALL` | 400 | The value of '{field}' is below the minimum required. | Value below minimum |
| `INVALID_OPTION` | 400 | The option '{value}' for '{field}' is not valid. | Invalid option selection |

### Authentication Errors

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Authentication is required to access this resource. | No authentication provided |
| `INVALID_CREDENTIALS` | 401 | The provided credentials are invalid. | Incorrect credentials |
| `EXPIRED_TOKEN` | 401 | Your authentication token has expired. Please sign in again. | Token expired |
| `INVALID_TOKEN` | 401 | The authentication token is invalid. | Invalid token format or signature |
| `INSUFFICIENT_PERMISSIONS` | 403 | You don't have permission to access this resource. | Inadequate permissions |
| `ACCOUNT_LOCKED` | 403 | Your account has been locked. Please contact support. | Account security lock |

### Resource Errors

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `RESOURCE_NOT_FOUND` | 404 | The requested resource was not found. | Resource doesn't exist |
| `RESOURCE_CONFLICT` | 409 | A resource conflict occurred. {detail} | Resource conflict |
| `RESOURCE_GONE` | 410 | The requested resource is no longer available. | Resource removed |
| `DUPLICATE_RESOURCE` | 409 | A resource with this identifier already exists. | Duplicate resource |

### Rate Limiting and Quota Errors

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded. Please try again in {reset_time} seconds. | Too many requests |
| `QUOTA_EXCEEDED` | 429 | Your quota has been exceeded for this {period}. | Usage quota exceeded |
| `CONCURRENT_LIMIT` | 429 | Too many concurrent requests. Please try again shortly. | Too many parallel requests |

### External Service Errors

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `LLM_UNAVAILABLE` | 502 | The AI service is currently unavailable. Please try again later. | LLM provider unavailable |
| `LLM_TIMEOUT` | 504 | The AI service took too long to respond. Please try again. | LLM request timeout |
| `LLM_ERROR` | 502 | The AI service encountered an error. | General LLM error |
| `DATABASE_ERROR` | 503 | Database service error. Please try again later. | Database issue |
| `CACHE_ERROR` | 503 | Cache service error. Please try again later. | Cache service issue |
| `EXTERNAL_API_ERROR` | 502 | An external service error occurred. | Third-party API error |

### Internal System Errors

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `INTERNAL_ERROR` | 500 | An internal server error occurred. | Generic server error |
| `UNEXPECTED_ERROR` | 500 | An unexpected error occurred. Please try again. | Unexpected exception |
| `SERVICE_UNAVAILABLE` | 503 | The service is temporarily unavailable. Please try again later. | Service unavailable |
| `NOT_IMPLEMENTED` | 501 | This feature is not implemented yet. | Feature not implemented |

## LLM-Specific Error Codes

| Code | HTTP Status | Message Template | Description |
|------|-------------|------------------|-------------|
| `LLM_CONTENT_FILTERED` | 422 | The AI service filtered this content. Please revise your input. | Content violates filters |
| `LLM_CONTEXT_LIMIT` | 413 | The input exceeds the maximum context length. | Context length exceeded |
| `LLM_TOKEN_LIMIT` | 413 | The response exceeded the maximum token limit. | Token limit exceeded |
| `LLM_PROVIDER_QUOTA` | 429 | The AI service quota has been exceeded. | Provider quota exceeded |
| `LLM_BAD_RESPONSE` | 502 | The AI service returned an invalid response. | Malformed LLM response |

## Error Handling Guidelines

### User-Facing Messages

1. Be clear and specific about what went wrong
2. Provide guidance on how to resolve the issue when possible
3. Avoid technical jargon in user-facing messages
4. Do not expose system internals or sensitive information
5. Include actionable advice where appropriate

### Internal Error Logging

1. Log detailed technical information for debugging
2. Include all relevant context and parameters
3. Record stack traces for unexpected errors
4. Log the request ID for correlation
5. Do not log sensitive information (PII, credentials, etc.)

## Example Error Responses

### Validation Error

```json
{
  "error": {
    "code": "INVALID_FIELD",
    "message": "The field 'email' is invalid. Please provide a valid email address.",
    "request_id": "req_7f328ab1-e8c2-4b89-9c5a-90f4c15a7a2d",
    "timestamp": "2025-05-11T10:15:30Z",
    "details": {
      "field": "email",
      "validation": "email_format"
    }
  }
}
```

### Authentication Error

```json
{
  "error": {
    "code": "EXPIRED_TOKEN",
    "message": "Your authentication token has expired. Please sign in again.",
    "request_id": "req_a1b2c3d4-e5f6-4a5b-8c9d-1e2f3a4b5c6d",
    "timestamp": "2025-05-11T14:22:15Z"
  }
}
```

### LLM Provider Error

```json
{
  "error": {
    "code": "LLM_UNAVAILABLE",
    "message": "The AI service is currently unavailable. Please try again later.",
    "request_id": "req_7b43c1a2-9d8e-4f6a-b5c3-2d1e0f9a8b7c",
    "timestamp": "2025-05-11T16:45:22Z",
    "details": {
      "provider": "gpt4o",
      "retry_after": 300
    }
  }
}
```