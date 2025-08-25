# PR: Circuit Breakers + Retries + Timeouts (Issue #35)

## Summary
This PR implements comprehensive resilience patterns for all LLM adapters as specified in P1 requirements:
- ✅ Circuit breakers to prevent cascading failures
- ✅ Bounded retries with exponential backoff and jitter
- ✅ Provider-specific timeout configuration
- ✅ Metrics and monitoring integration

## Implementation Details

### Circuit Breakers
- **Three states**: CLOSED (normal), OPEN (failing), HALF_OPEN (recovery testing)
- **Provider-specific thresholds**:
  - OpenAI: 5 failures before opening, 60s recovery timeout
  - Anthropic: 3 failures (more conservative), 90s recovery
  - Google: 5 failures, 45s recovery
- **Automatic recovery**: Transitions to half-open after timeout

### Retry Strategy
- **Exponential backoff** with configurable base (2.0 default)
- **Jitter** (±10%) to prevent thundering herd
- **Provider-specific settings**:
  - OpenAI: 3 attempts, 1s initial delay, 10s max
  - Anthropic: 3 attempts, 2s initial delay, 20s max  
  - Google: 4 attempts, 0.5s initial delay, 15s max
- **Smart retry logic**: No retries on 4xx errors or circuit open

### Provider Timeouts
- **Tuned per vendor characteristics**:
  - OpenAI: 30s (typical response time)
  - Anthropic: 45s (complex prompts need more time)
  - Google: 25s (typically faster)
- **Separate HTTP client** per provider with configured timeout

### Integration
- **ResilientLLMAdapter** wraps all base adapters transparently
- **Factory function** `create_resilient_adapter()` auto-detects provider
- **Correlation ID tracking** throughout retry/circuit breaker flow
- **Comprehensive metrics** for monitoring and alerting

## Files Changed
- `app/services/resilient_llm_adapter.py` - Core resilience implementation
- `app/services/orchestration_service.py` - Updated to use resilient adapters
- `tests/test_resilient_llm_adapter.py` - Comprehensive test suite
- `documentation/resilience_patterns.md` - Detailed documentation

## Testing
Created extensive test coverage including:
- Circuit breaker state transitions
- Retry behavior with backoff
- Provider-specific configurations
- Metrics tracking
- Error handling scenarios
- Integration with real adapters

## Performance Impact
- **Minimal overhead** in success case (single wrapper call)
- **Prevents cascade failures** during provider outages
- **Reduces unnecessary retries** with smart retry logic
- **Improves overall system stability**

## Monitoring & Observability
Each adapter now tracks:
```python
{
    "total_requests": 1000,
    "successful_requests": 950,
    "failed_requests": 50,
    "retries": 25,
    "circuit_opens": 2,
    "circuit_breaker": {
        "state": "closed",
        "failure_count": 0,
        "last_failure": "2025-01-24T10:30:00Z"
    }
}
```

## Configuration
All settings can be tuned via environment variables or code:
- Timeout duration per provider
- Retry attempts and delays
- Circuit breaker thresholds
- Jitter percentage

## Backward Compatibility
- No breaking changes to existing API
- Resilience is transparent to callers
- Can be disabled by using base adapters directly
- Existing error responses maintained

## Migration Notes
1. All orchestration service calls now use resilient adapters
2. Monitor circuit breaker states after deployment
3. Tune thresholds based on production metrics
4. Consider alerts for circuit breaker opens

## Next Steps
- Add Grafana dashboards for resilience metrics
- Implement circuit breaker manual reset endpoint
- Consider per-model timeout configuration
- Add distributed circuit breaker state (Redis)

## Example Usage
```python
# Automatically wrapped with resilience
adapter, model = self._create_model_adapter("gpt-4")
result = await adapter.generate(prompt)

# Metrics available
metrics = adapter.get_metrics()
logger.info(f"Circuit breaker state: {metrics['circuit_breaker']['state']}")
```