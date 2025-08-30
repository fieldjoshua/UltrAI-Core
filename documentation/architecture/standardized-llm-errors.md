# Standardized LLM Error Responses

## Overview

This document describes the standardized error response format implemented across all LLM adapters in the UltraAI system. The standardization improves debugging, monitoring, and error handling consistency throughout the orchestration pipeline.

## Motivation

Previously, each LLM adapter (OpenAI, Anthropic, Google, HuggingFace) had its own error format and handling logic, leading to:
- Inconsistent error messages across providers
- Difficulty in implementing unified retry logic
- Complex error parsing in the orchestration service
- Poor debugging experience

## Architecture

### Error Type Enumeration

All errors are categorized into standardized types:

```python
class ErrorType(str, Enum):
    # Authentication and authorization
    AUTHENTICATION_FAILED = "authentication_failed"
    INVALID_API_KEY = "invalid_api_key"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    
    # Model issues
    MODEL_NOT_FOUND = "model_not_found"
    MODEL_LOADING = "model_loading"
    
    # Request issues
    INVALID_REQUEST = "invalid_request"
    TIMEOUT = "timeout"
    
    # Network and server issues
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    
    # General errors
    UNKNOWN_ERROR = "unknown_error"
```

### Error Response Model

```python
class LLMErrorResponse(BaseModel):
    error: bool = True
    error_type: ErrorType
    error_code: Optional[str]  # Provider-specific code
    error_message: str
    provider: str
    model: str
    status_code: Optional[int]
    retry_after: Optional[int]  # Seconds for rate limits
    details: Optional[Dict[str, Any]]
```

### Success Response Model

```python
class LLMSuccessResponse(BaseModel):
    generated_text: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]]  # Token usage
    finish_reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

## Implementation

### Enhanced Base Adapter

All enhanced adapters inherit from `EnhancedBaseAdapter` which provides:

1. **Common Error Handling**: Timeout, network errors, HTTP status errors
2. **Standardized Response Creation**: Helper methods for creating error/success responses
3. **Retry Information Extraction**: Parse retry-after headers from various providers
4. **Secure Logging**: Correlation IDs and masked API keys

### Provider-Specific Handling

Each provider adapter implements `_handle_http_status_error()` for provider-specific errors:

- **OpenAI**: 401 (auth), 404 (model not found), 429 (rate limit)
- **Anthropic**: Similar to OpenAI with specific error codes
- **Google**: RESOURCE_EXHAUSTED for quota, UNAUTHENTICATED for auth
- **HuggingFace**: 503 with model loading time estimates

## Migration Strategy

### Feature Flag

The system uses a feature flag to enable enhanced adapters:

```bash
export USE_ENHANCED_LLM_ADAPTERS=true
```

### Adapter Factory

`LLMAdapterFactory` creates either legacy or enhanced adapters based on configuration:

```python
adapter = LLMAdapterFactory.create_from_model_name(
    "gpt-4",
    force_enhanced=True  # Override global setting
)
```

### Backward Compatibility

Enhanced adapters maintain backward compatibility by:
1. Returning legacy format by default: `{"generated_text": "..."}`
2. Providing `to_legacy_format()` method for error conversion
3. Preserving existing error detection patterns in orchestration service

## Benefits

1. **Consistent Error Handling**: All providers return errors in the same format
2. **Better Retry Logic**: Standardized retry-after information
3. **Improved Debugging**: Structured error types and correlation IDs
4. **Enhanced Monitoring**: Easy to track error rates by type
5. **Future-Proof**: Easy to add new error types or providers

## Usage Examples

### Handling Errors in Orchestration

```python
result = await adapter.generate(prompt)

if "error" in result and result["error"]:
    # Legacy format still works
    error_text = result.get("generated_text", "")
    
    # But can also access structured data
    if "provider" in result:
        provider = result["provider"]
        
    # Retry logic can use retry_after if available
    if "retry_after" in result:
        await asyncio.sleep(result["retry_after"])
```

### Creating Custom Errors

```python
# In adapter implementation
return self._create_error_response(
    error_type=ErrorType.RATE_LIMIT_EXCEEDED,
    error_message="Daily quota exceeded",
    status_code=429,
    retry_after=3600,  # Retry in 1 hour
    details={"quota_reset": "2024-01-01T00:00:00Z"}
)
```

## Testing

Comprehensive unit tests ensure:
- All adapters produce consistent error formats
- Legacy format conversion works correctly
- Error detection patterns remain compatible
- Rate limit information is properly extracted

## Future Enhancements

1. **Structured Success Responses**: Gradually migrate to structured success format
2. **Error Metrics**: Prometheus metrics for each error type
3. **Automatic Retry**: Built-in retry based on error type
4. **Provider Health Tracking**: Track error rates per provider/model
5. **Error Response Caching**: Cache 4xx errors to reduce API calls