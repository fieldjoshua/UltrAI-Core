# Ultra Error Handling System

This document describes the comprehensive error handling system implemented in the Ultra backend. The system is designed to provide consistent error handling, reporting, and recovery mechanisms across the application.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Components](#key-components)
- [Error Classification](#error-classification)
- [Domain-Specific Exceptions](#domain-specific-exceptions)
- [Recovery Strategies](#recovery-strategies)
- [Integration with FastAPI](#integration-with-fastapi)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Architecture Overview

The Ultra error handling system is built around the following principles:

1. **Consistency**: All errors are handled and reported in a consistent manner
2. **Clarity**: Error messages provide clear information about what went wrong
3. **Context**: Errors include relevant context to aid debugging
4. **Recovery**: The system includes mechanisms for automatic recovery from transient failures
5. **Isolation**: Failures are isolated to prevent cascading failures

The system uses a layered approach to error handling:

```
┌───────────────────────────────────────────────────────────┐
│                   API Request/Response                     │
├───────────────────────────────────────────────────────────┤
│                Global Error Handling Middleware            │
├───────────────────────────────────────────────────────────┤
│                Exception Handler Registration              │
├───────────────────────────────────────────────────────────┤
│                                                           │
│           ┌───────────────┐       ┌────────────────┐     │
│           │Unified Error  │       │Domain-Specific  │     │
│           │Handler        │◄─────►│Exceptions       │     │
│           └───────────────┘       └────────────────┘     │
│                  ▲                       ▲               │
│                  │                       │               │
│                  ▼                       │               │
│           ┌───────────────┐              │               │
│           │Error          │              │               │
│           │Classification │              │               │
│           └───────────────┘              │               │
│                  ▲                       │               │
│                  │                       │               │
│                  ▼                       ▼               │
│           ┌───────────────┐       ┌────────────────┐     │
│           │Recovery       │◄─────►│Error Response  │     │
│           │Strategies     │       │Formatting      │     │
│           └───────────────┘       └────────────────┘     │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Key Components

### Unified Error Handler (`unified_error_handler.py`)

The unified error handler module is the core of the error handling system. It provides:

- A base exception class (`UltraBaseException`) that all custom exceptions inherit from
- A set of standardized error codes (`ErrorCode`) for consistent error identification
- Error classification mechanisms to map exceptions to HTTP status codes, severity levels, and categories
- Middleware for global error handling with consistent error responses
- Utility functions for formatting and logging exceptions

### Domain-Specific Exceptions (`domain_exceptions.py`)

Domain-specific exceptions extend the base exception class to provide specialized error handling for different parts of the application, including:

- Authentication and authorization exceptions
- Resource exceptions
- Service exceptions
- Validation exceptions
- Database exceptions
- Model/LLM exceptions
- Document processing exceptions
- Payment and pricing exceptions

### Recovery Strategies (`recovery_strategies.py`)

Recovery strategies provide mechanisms for automatic recovery from transient failures, including:

- Retry mechanisms with exponential backoff
- Circuit breakers to protect against cascading failures
- Fallback mechanisms for graceful degradation
- Bulkheads for isolation of failures
- Rate limiting to prevent overload
- Timeouts to prevent resource exhaustion

## Error Classification

### Error Codes

Error codes provide a consistent way to identify errors across the application. They are grouped by domain:

- **General errors (1xx)**: `internal_error`, `not_found`, `bad_request`, etc.
- **Validation errors (2xx)**: `validation_error`, `invalid_input`, `missing_field`, etc.
- **Authentication errors (3xx)**: `unauthorized`, `forbidden`, `invalid_auth`, etc.
- **Resource errors (4xx)**: `resource_exists`, `resource_not_found`, `resource_conflict`, etc.
- **Rate limiting errors (5xx)**: `rate_limit_exceeded`, `quota_exceeded`, etc.
- **Service errors (6xx)**: `service_unavailable`, `external_service_error`, `timeout`, etc.
- **Business logic errors (7xx)**: `business_logic_error`, `permission_denied`, etc.
- **Data errors (8xx)**: `database_error`, `data_integrity_error`, etc.
- **LLM and model errors (9xx)**: `model_error`, `model_unavailable`, `model_timeout`, etc.
- **Document errors (10xx)**: `document_error`, `document_not_found`, etc.
- **Payment and pricing errors (11xx)**: `payment_required`, `payment_failed`, etc.

### Error Severity

Errors are classified by severity to guide logging and monitoring behavior:

- **CRITICAL**: System is unusable, immediate attention required
- **ERROR**: Error that prevents operation from completing
- **WARNING**: Potentially harmful situation, operation can continue
- **INFO**: Informational message about an error
- **DEBUG**: Debugging information about an error

### Error Categories

Errors are grouped into categories for easier management:

- **SECURITY**: Security-related errors
- **VALIDATION**: Input validation errors
- **AUTHORIZATION**: Authentication/authorization errors
- **RESOURCE**: Resource access/manipulation errors
- **SERVICE**: Service availability/external service errors
- **SYSTEM**: System/infrastructure errors
- **BUSINESS**: Business logic errors
- **RATE_LIMIT**: Rate limiting/quota errors
- **CLIENT**: Client-side errors
- **DATA**: Data/database errors
- **MODEL**: LLM/model errors
- **DOCUMENT**: Document processing errors
- **PAYMENT**: Payment/pricing errors
- **UNKNOWN**: Uncategorized errors

## Domain-Specific Exceptions

### Authentication and Authorization Exceptions

- `AuthenticationException`: Base exception for authentication failures
- `AuthorizationException`: Exception for authorization failures
- `InvalidTokenException`: Exception for invalid tokens
- `ExpiredTokenException`: Exception for expired tokens
- `MissingTokenException`: Exception for missing tokens

### Rate Limiting Exceptions

- `RateLimitException`: Exception for rate limit exceeded
- `QuotaExceededException`: Exception for quota exceeded

### Validation Exceptions

- `ValidationException`: Base exception for validation failures
- `InvalidInputException`: Exception for invalid input
- `MissingFieldException`: Exception for missing required fields

### Resource Exceptions

- `ResourceNotFoundException`: Exception for resource not found
- `ResourceAlreadyExistsException`: Exception for resource already exists
- `ResourceConflictException`: Exception for resource conflicts

### Service Exceptions

- `ServiceException`: Base exception for service errors
- `ServiceUnavailableException`: Exception for unavailable services
- `ExternalServiceException`: Exception for external service errors
- `TimeoutException`: Exception for timeouts
- `CircuitOpenException`: Exception for open circuit breakers

### Database Exceptions

- `DatabaseException`: Base exception for database errors
- `DataIntegrityException`: Exception for data integrity errors

### LLM/Model Exceptions

- `ModelException`: Base exception for model errors
- `ModelUnavailableException`: Exception for unavailable models
- `ModelTimeoutException`: Exception for model timeouts
- `ModelContentFilterException`: Exception for content filter issues
- `ModelContextLengthException`: Exception for context length exceeded

### Document Exceptions

- `DocumentException`: Base exception for document errors
- `DocumentNotFoundException`: Exception for document not found
- `DocumentFormatException`: Exception for invalid document formats
- `DocumentTooLargeException`: Exception for documents that are too large
- `DocumentProcessingException`: Exception for document processing errors

### Payment and Pricing Exceptions

- `PaymentException`: Base exception for payment errors
- `PaymentRequiredException`: Exception for payment required
- `InsufficientFundsException`: Exception for insufficient funds
- `SubscriptionRequiredException`: Exception for subscription required
- `SubscriptionExpiredException`: Exception for expired subscriptions

## Recovery Strategies

### Retry Mechanisms

The system includes several retry strategies for handling transient failures:

- `NoRetryStrategy`: Does not retry failures
- `FixedRetryStrategy`: Retries with a fixed delay
- `ExponentialBackoffRetryStrategy`: Retries with exponential backoff

Example:

```python
# Create a retry strategy with exponential backoff
retry_strategy = ExponentialBackoffRetryStrategy(
    max_retries=3,
    initial_delay=0.1,
    max_delay=10.0,
    backoff_factor=2.0,
    jitter=True,
    retryable_errors=[RetryableErrorType.CONNECTION, RetryableErrorType.TIMEOUT],
)

# Use the retry strategy
result = await retry_strategy.execute_with_retry(
    my_function, arg1, arg2, kwarg1=value1
)
```

### Circuit Breaker

The circuit breaker pattern prevents cascading failures by failing fast when a service is consistently failing:

```python
# Create a circuit breaker
circuit_breaker = CircuitBreaker(
    name="my_service",
    failure_threshold=5,
    reset_timeout=30,
    half_open_success_threshold=2,
)

# Use the circuit breaker as a decorator
@circuit_breaker
async def call_external_service():
    # ...

# Or use it directly
result = await circuit_breaker.execute(
    call_external_service, arg1, arg2
)
```

### Bulkhead

The bulkhead pattern isolates failures and prevents them from consuming all resources:

```python
# Create a bulkhead
bulkhead = Bulkhead(
    name="my_service",
    max_concurrent_calls=10,
    max_queue_size=10,
)

# Use the bulkhead as a decorator
@bulkhead
async def call_external_service():
    # ...

# Or use it directly
result = await bulkhead.execute(
    call_external_service, arg1, arg2
)
```

### Fallback

The fallback pattern provides alternative responses when a service fails:

```python
# Create a fallback
async def fallback_function(*args, **kwargs):
    return {"status": "fallback", "data": "default_data"}

fallback = Fallback(
    fallback_function=fallback_function,
    should_fallback_on=[ServiceUnavailableException, TimeoutException],
)

# Use the fallback as a decorator
@fallback
async def call_external_service():
    # ...

# Or use it directly
result = await fallback.execute(
    call_external_service, arg1, arg2
)
```

### Rate Limiter

The rate limiter pattern controls the rate of requests to prevent overload:

```python
# Create a rate limiter
rate_limiter = RateLimiter(
    name="my_service",
    max_calls=10,
    period=1.0,
)

# Use the rate limiter as a decorator
@rate_limiter
async def call_external_service():
    # ...

# Or use it directly
result = await rate_limiter.execute(
    call_external_service, arg1, arg2
)
```

### Timeout

The timeout pattern limits the time a function can take:

```python
# Create a timeout
timeout = Timeout(timeout_seconds=30.0)

# Use the timeout as a decorator
@timeout
async def call_external_service():
    # ...

# Or use it directly
result = await timeout.execute(
    call_external_service, arg1, arg2
)
```

### Resilience Composite

The resilience composite pattern combines multiple resilience patterns:

```python
# Create a resilience composite
composite = ResilienceComposite(
    name="my_service",
    rate_limiter=rate_limiter,
    circuit_breaker=circuit_breaker,
    bulkhead=bulkhead,
    timeout=timeout,
    retry_strategy=retry_strategy,
    fallback=fallback,
)

# Use the composite as a decorator
@composite
async def call_external_service():
    # ...

# Or use it directly
result = await composite.execute(
    call_external_service, arg1, arg2
)
```

## Integration with FastAPI

The error handling system integrates seamlessly with FastAPI:

```python
from fastapi import FastAPI
from backend.utils.unified_error_handler import setup_error_handling

app = FastAPI()

# Set up error handling
setup_error_handling(
    app,
    include_debug_details=False,
    exclude_paths=["/health", "/metrics"],
)
```

This sets up:

1. Global error handling middleware for consistent error responses
2. Exception handlers for standard FastAPI exceptions
3. Exception handlers for custom Ultra exceptions

## Best Practices

### Raising Exceptions

When raising exceptions, use the most specific exception type that applies:

```python
# Not recommended
raise UltraBaseException("Resource not found")

# Recommended
raise ResourceNotFoundException(
    resource_type="User",
    resource_id="123",
    message="User with ID 123 not found",
)
```

Include relevant context in the exception:

```python
raise ModelTimeoutException(
    model_name="gpt-4",
    message="Request to GPT-4 timed out",
    provider="OpenAI",
    timeout_seconds=30.0,
)
```

### Handling Exceptions

Use try/except blocks to handle expected exceptions:

```python
try:
    result = await call_external_service()
except ServiceUnavailableException as e:
    # Handle service unavailable
    logger.warning(f"Service unavailable: {e.message}")
    # Provide a graceful fallback
    result = {"status": "error", "message": "Service temporarily unavailable"}
except ExternalServiceException as e:
    # Handle external service error
    logger.error(f"External service error: {e.message}")
    # Provide a graceful fallback
    result = {"status": "error", "message": "External service error"}
except TimeoutException as e:
    # Handle timeout
    logger.warning(f"Timeout: {e.message}")
    # Provide a graceful fallback
    result = {"status": "error", "message": "Request timed out"}
except Exception as e:
    # Handle unexpected exceptions
    logger.error(f"Unexpected error: {str(e)}")
    # Re-raise as UltraBaseException for consistent handling
    raise UltraBaseException(
        message="An unexpected error occurred",
        code=ErrorCode.INTERNAL_ERROR,
        original_exception=e,
    )
```

### Using Recovery Strategies

Choose the appropriate recovery strategy for each use case:

- Use `ExponentialBackoffRetryStrategy` for retrying transient failures
- Use `CircuitBreaker` for preventing cascading failures
- Use `Bulkhead` for isolating failures
- Use `Fallback` for providing alternative responses
- Use `RateLimiter` for controlling request rates
- Use `Timeout` for preventing resource exhaustion
- Use `ResilienceComposite` for combining multiple strategies

Use factory functions for common patterns:

```python
from backend.utils.recovery_strategies import (
    create_standard_retry,
    create_circuit_breaker,
    create_bulkhead,
    create_rate_limiter,
    create_timeout,
    create_resilience_composite,
)

# Create standard patterns
retry = create_standard_retry(max_retries=3, initial_delay=0.1)
circuit_breaker = create_circuit_breaker(service_name="my_service", failure_threshold=5)
bulkhead = create_bulkhead(service_name="my_service", max_concurrent_calls=10)
rate_limiter = create_rate_limiter(service_name="my_service", max_calls=50, period=1.0)
timeout = create_timeout(timeout_seconds=30.0)

# Create a composite with all patterns
composite = create_resilience_composite(
    service_name="my_service",
    max_retries=3,
    failure_threshold=5,
    max_concurrent_calls=10,
    timeout_seconds=30.0,
    rate_limit_max_calls=50,
    rate_limit_period=1.0,
    fallback_function=my_fallback_function,
)
```

## Examples

### Example 1: Handling Authentication Errors

```python
from fastapi import Depends, HTTPException
from backend.utils.domain_exceptions import (
    AuthenticationException,
    InvalidTokenException,
    ExpiredTokenException,
)
from backend.utils.auth import get_current_user

async def get_authenticated_user(token: str):
    try:
        return await get_current_user(token)
    except InvalidTokenException as e:
        # Invalid token
        raise e
    except ExpiredTokenException as e:
        # Expired token
        raise e
    except Exception as e:
        # Unexpected error
        raise AuthenticationException(
            message="Authentication failed due to an unexpected error",
            original_exception=e,
        )

@app.get("/protected")
async def protected_route(user = Depends(get_authenticated_user)):
    return {"message": f"Hello, {user.username}!"}
```

### Example 2: Resilient External Service Call

```python
from backend.utils.recovery_strategies import (
    create_resilience_composite,
)
from backend.utils.domain_exceptions import (
    ExternalServiceException,
    TimeoutException,
)

# Create a fallback function
async def service_fallback(*args, **kwargs):
    return {"status": "fallback", "data": "default_data"}

# Create a resilience composite
service_client = create_resilience_composite(
    service_name="external_service",
    max_retries=3,
    failure_threshold=5,
    max_concurrent_calls=10,
    timeout_seconds=30.0,
    rate_limit_max_calls=50,
    rate_limit_period=1.0,
    fallback_function=service_fallback,
)

# Use the composite as a decorator
@service_client
async def call_external_service(query: str):
    try:
        response = await httpx.get(f"https://api.example.com/search?q={query}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise ExternalServiceException(
            service_name="external_service",
            message=f"External service returned error: {e.response.status_code}",
            status_code=e.response.status_code,
            original_error=e,
        )
    except httpx.TimeoutException as e:
        raise TimeoutException(
            service_name="external_service",
            message="External service timed out",
            timeout_seconds=30.0,
        )
    except Exception as e:
        raise ExternalServiceException(
            service_name="external_service",
            message=f"Error calling external service: {str(e)}",
            original_error=e,
        )

# Call the service
result = await call_external_service("query")
```

### Example 3: Document Processing with Error Handling

```python
from backend.utils.domain_exceptions import (
    DocumentNotFoundException,
    DocumentFormatException,
    DocumentTooLargeException,
    DocumentProcessingException,
)

async def process_document(document_id: str):
    try:
        # Get document
        document = await get_document(document_id)
        if not document:
            raise DocumentNotFoundException(document_id=document_id)

        # Check format
        if document.format not in ["pdf", "docx", "txt"]:
            raise DocumentFormatException(
                document_id=document_id,
                format=document.format,
                message=f"Unsupported document format: {document.format}",
            )

        # Check size
        if document.size > 10_000_000:  # 10 MB
            raise DocumentTooLargeException(
                document_id=document_id,
                size=document.size,
                max_size=10_000_000,
            )

        # Process document
        try:
            result = await process_document_content(document)
            return result
        except Exception as e:
            raise DocumentProcessingException(
                document_id=document_id,
                message=f"Error processing document: {str(e)}",
                processing_stage="content_processing",
                original_exception=e,
            )
    except (DocumentNotFoundException, DocumentFormatException, DocumentTooLargeException) as e:
        # Re-raise known exceptions
        raise
    except Exception as e:
        # Handle unexpected exceptions
        raise DocumentProcessingException(
            document_id=document_id,
            message=f"Unexpected error processing document: {str(e)}",
            original_exception=e,
        )
```
