# Request ID Tracking Architecture

## Overview

The UltraAI system implements comprehensive request tracking using unique request IDs and correlation IDs that follow requests through all services and external API calls. This enables end-to-end debugging, performance monitoring, and distributed tracing.

## Key Concepts

### Request ID
A unique identifier generated for each incoming HTTP request. Format: `req_{uuid_hex[:16]}`

Example: `req_a1b2c3d4e5f6g7h8`

### Correlation ID
An identifier that groups related requests across services. In a distributed system, one user action might trigger multiple internal requests - all share the same correlation ID.

### Tracking Headers
- `X-Request-ID`: Unique per request
- `X-Correlation-ID`: Shared across related requests
- `X-Trace-ID`: Alternative correlation ID header (fallback)

## Architecture Components

### 1. Request ID Middleware

Enhanced middleware that:
- Generates request IDs if not provided
- Extracts or creates correlation IDs
- Sets IDs in request state
- Adds tracking headers to responses
- Integrates with logging context

```python
# Automatic in all requests
request.state.request_id    # "req_a1b2c3d4e5f6g7h8"
request.state.correlation_id # "corr_x9y8z7w6v5u4t3s2"
```

### 2. Correlation Context

Thread-local storage for correlation IDs used by the logging system:

```python
from app.utils.logging import CorrelationContext

# Automatically set by middleware
correlation_id = CorrelationContext.get_correlation_id()

# All logs include correlation ID
logger.info("Processing request")  # Includes correlation_id in JSON
```

### 3. Tracked LLM Adapters

Wrappers that add tracking to all LLM API calls:

```python
# Automatically tracks outgoing requests
adapter = TrackedOpenAIAdapter(api_key, model)
adapter.set_tracking_ids(request_id, correlation_id)

# All API calls now include tracking headers
response = await adapter.generate(prompt)
```

### 4. Tracked Orchestration Service

Extended orchestration service that:
- Tracks pipeline execution stages
- Logs with request/correlation IDs
- Passes tracking to LLM adapters

```python
service = TrackedOrchestrationService(...)
service.set_request_context(request)  # From FastAPI

# All pipeline operations are now tracked
result = await service.run_pipeline(...)
```

## Implementation Flow

1. **Client Request**
   ```
   GET /api/orchestrator/analyze
   X-Request-ID: client-req-123 (optional)
   ```

2. **Middleware Processing**
   - Extracts or generates request ID
   - Sets correlation context
   - Adds to request state

3. **Endpoint Handler**
   ```python
   @router.post("/orchestrator/analyze")
   async def analyze(request: Request):
       # IDs available via request.state
       orchestration_service.set_request_context(request)
   ```

4. **Service Layer**
   - Uses tracked orchestration service
   - Logs include request/correlation IDs
   - Creates tracked LLM adapters

5. **External API Calls**
   ```
   POST https://api.openai.com/v1/chat/completions
   X-Request-ID: req_a1b2c3d4e5f6g7h8
   X-Correlation-ID: corr_x9y8z7w6v5u4t3s2
   ```

6. **Response**
   ```
   200 OK
   X-Request-ID: req_a1b2c3d4e5f6g7h8
   X-Correlation-ID: corr_x9y8z7w6v5u4t3s2
   ```

## Log Correlation

All logs automatically include tracking IDs:

```json
{
  "timestamp": "2024-01-20T10:30:45.123Z",
  "level": "INFO",
  "logger": "orchestration_service",
  "message": "Starting stage: initial_response",
  "correlation_id": "corr_x9y8z7w6v5u4t3s2",
  "request_id": "req_a1b2c3d4e5f6g7h8",
  "stage": "initial_response",
  "module": "orchestration_service",
  "function": "run_pipeline",
  "line": 472
}
```

## Debugging Workflow

### 1. Find Request by ID
```bash
# Search logs for specific request
grep "req_a1b2c3d4e5f6g7h8" logs/requests.log
```

### 2. Trace Full Flow
```bash
# Find all related requests via correlation ID
grep "corr_x9y8z7w6v5u4t3s2" logs/*.log
```

### 3. Filter by Service
```json
// Logs include service context
{
  "correlation_id": "corr_x9y8z7w6v5u4t3s2",
  "service": "ultrai-orchestrator",
  "stage": "peer_review_and_revision"
}
```

## Performance Monitoring

Request tracking enables performance analysis:

```json
{
  "event": "request_complete",
  "request_id": "req_a1b2c3d4e5f6g7h8",
  "method": "POST",
  "path": "/api/orchestrator/analyze",
  "status_code": 200,
  "duration_ms": 3456.78,
  "service": "ultrai-orchestrator"
}
```

## Configuration

### Environment Variables

```bash
# Enable debug logging for tracking
LOG_LEVEL=DEBUG

# Service name for tracking
SERVICE_NAME=ultrai-orchestrator
```

### Middleware Order

Request tracking should be early in the middleware stack:

```python
app.add_middleware(RequestIDMiddleware)  # First
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)
```

## Best Practices

1. **Always Propagate IDs**: When making internal service calls, pass tracking headers
2. **Log Context**: Include request/correlation IDs in all significant log messages
3. **Error Tracking**: Include IDs in error reports for easier debugging
4. **Performance Metrics**: Tag metrics with request IDs for correlation
5. **Client Integration**: Return tracking headers to clients for support

## Client Implementation

### JavaScript/TypeScript
```typescript
const response = await fetch('/api/orchestrator/analyze', {
  method: 'POST',
  headers: {
    'X-Request-ID': generateRequestId(),
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
});

const requestId = response.headers.get('X-Request-ID');
console.log(`Request completed: ${requestId}`);
```

### Python
```python
import requests

response = requests.post(
    'https://api.example.com/api/orchestrator/analyze',
    headers={'X-Request-ID': 'client-req-123'},
    json=data
)

print(f"Request ID: {response.headers.get('X-Request-ID')}")
print(f"Correlation ID: {response.headers.get('X-Correlation-ID')}")
```

## Monitoring Integration

### Prometheus Metrics
```python
request_duration.labels(
    method=request.method,
    path=request.url.path,
    status=response.status_code,
    request_id=request.state.request_id
).observe(duration)
```

### Distributed Tracing
Compatible with OpenTelemetry and Jaeger using correlation IDs as trace IDs.

## Troubleshooting

### Missing Request IDs
- Check middleware order
- Verify middleware is added to app
- Check for header name mismatches

### Correlation Context Lost
- Ensure async context is preserved
- Check for thread boundary crossings
- Verify context cleanup in finally blocks

### Performance Impact
- Request tracking adds <1ms overhead
- Logging with IDs has minimal impact
- Header propagation is negligible

## Future Enhancements

1. **Distributed Tracing**: Full OpenTelemetry integration
2. **Request Sampling**: Sample detailed logs for % of requests
3. **Trace Visualization**: UI for viewing request flows
4. **Anomaly Detection**: Alert on unusual request patterns
5. **Cost Attribution**: Track LLM costs by request ID