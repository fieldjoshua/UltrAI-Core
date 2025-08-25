# Resilience Patterns for LLM Adapters

## Overview
This document describes the resilience patterns implemented for LLM API calls in UltrAI-Core, including circuit breakers, bounded retries with jitter, and provider-specific timeouts.

## Circuit Breakers

### Purpose
Circuit breakers prevent cascading failures by stopping requests to a failing service, giving it time to recover.

### States
1. **CLOSED** - Normal operation, requests pass through
2. **OPEN** - Service is failing, requests are rejected immediately
3. **HALF_OPEN** - Testing if service has recovered

### Configuration
Each provider has tuned circuit breaker settings:

| Provider | Failure Threshold | Success Threshold | Timeout | Min Calls |
|----------|------------------|-------------------|---------|-----------|
| OpenAI | 5 | 2 | 60s | 10 |
| Anthropic | 3 | 2 | 90s | 10 |
| Google | 5 | 3 | 45s | 10 |

### Behavior
- After `failure_threshold` failures, circuit opens
- After `timeout` seconds, circuit transitions to half-open
- In half-open state, `success_threshold` successes close the circuit
- Any failure in half-open state reopens the circuit

## Retry Strategy

### Bounded Retries
All providers implement bounded retries with:
- Maximum retry attempts per provider
- Exponential backoff between retries
- Jitter to prevent thundering herd

### Retry Configuration

| Provider | Max Attempts | Initial Delay | Max Delay | Backoff Base |
|----------|--------------|---------------|-----------|--------------|
| OpenAI | 3 | 1.0s | 10.0s | 2.0 |
| Anthropic | 3 | 2.0s | 20.0s | 2.0 |
| Google | 4 | 0.5s | 15.0s | 2.0 |

### Retry Logic
```
delay = min(initial_delay * (backoff_base ^ attempt), max_delay)
jittered_delay = delay ± (delay * jitter_factor)
```

### Non-Retryable Errors
The following errors are NOT retried:
- 4xx client errors (400-499)
- Circuit breaker open
- Authentication failures (401)
- Invalid model errors (404)

## Provider-Specific Timeouts

### Timeout Configuration
Each provider has optimized timeouts based on typical response times:

| Provider | Timeout | Rationale |
|----------|---------|-----------|
| OpenAI | 30s | Typically responds within 30s |
| Anthropic | 45s | Claude can take longer for complex prompts |
| Google | 25s | Gemini is typically fast |

### Timeout Behavior
- Each provider gets its own HTTP client with configured timeout
- Timeouts trigger retry logic (if retries available)
- All timeouts are logged with correlation IDs

## Implementation Details

### ResilientLLMAdapter
Wraps base LLM adapters with resilience patterns:
```python
# Create resilient adapter
base_adapter = OpenAIAdapter(api_key, model)
resilient_adapter = create_resilient_adapter(base_adapter)

# Use normally
result = await resilient_adapter.generate(prompt)
```

### Metrics Tracking
Each adapter tracks:
- Total requests
- Successful requests
- Failed requests
- Retry attempts
- Circuit breaker opens

Access metrics:
```python
metrics = resilient_adapter.get_metrics()
```

### Error Handling
All errors include:
- Original error message
- Provider name
- Correlation ID for tracing
- Retry information (if applicable)

## Best Practices

### 1. Use Provider-Specific Configs
Don't use generic timeouts - each provider has different performance characteristics.

### 2. Monitor Circuit Breaker State
Log and alert on circuit breaker state changes to detect provider issues early.

### 3. Implement Graceful Degradation
When a provider fails, consider:
- Falling back to another provider
- Returning cached results
- Providing degraded functionality

### 4. Tune Based on Production Data
Initial configurations should be adjusted based on:
- Actual provider response times
- Error rates
- Traffic patterns

## Testing

### Unit Tests
```bash
pytest tests/test_resilient_llm_adapter.py -v
```

### Integration Testing
Test with real providers (requires API keys):
```bash
pytest tests/test_resilient_llm_adapter.py -m integration -v
```

### Load Testing
Simulate high load to verify:
- Circuit breakers open appropriately
- Retries don't overwhelm the system
- Timeouts are reasonable

## Monitoring and Alerts

### Key Metrics to Monitor
1. **Circuit Breaker State** - Alert when circuit opens
2. **Retry Rate** - High retry rate indicates issues
3. **Timeout Rate** - Frequent timeouts need investigation
4. **Success Rate** - Per-provider success rates

### Logging
All resilience events are logged with:
- Correlation IDs for request tracing
- Provider information
- Error details
- Timing information

## Configuration

### Environment Variables
```bash
# Override default timeouts (seconds)
OPENAI_TIMEOUT=30
ANTHROPIC_TIMEOUT=45
GOOGLE_TIMEOUT=25

# Override retry settings
MAX_RETRIES=3
RETRY_INITIAL_DELAY=1.0
RETRY_MAX_DELAY=30.0

# Circuit breaker settings
CIRCUIT_FAILURE_THRESHOLD=5
CIRCUIT_TIMEOUT=60
```

### Dynamic Configuration
For production, consider:
- Feature flags for enabling/disabling resilience patterns
- Dynamic configuration updates without restart
- A/B testing different configurations

## Troubleshooting

### Circuit Breaker Always Open
- Check provider API status
- Verify API keys are valid
- Review error logs for patterns
- Manually reset circuit if needed

### High Retry Rate
- Check network connectivity
- Verify provider isn't rate limiting
- Review timeout settings
- Consider increasing initial delay

### Timeouts Too Frequent
- Increase timeout for that provider
- Check prompt complexity
- Verify network latency
- Consider regional endpoints