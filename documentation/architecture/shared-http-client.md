# Shared HTTP Client Architecture

## Overview

The UltraAI system uses a critical architectural pattern called the "shared HTTP client" for all LLM API communications. This document explains what it is, why it's important, and how it must be maintained.

## What is the Shared HTTP Client?

The shared HTTP client is a single instance of `httpx.AsyncClient` that is created once and reused by all LLM adapters (OpenAI, Anthropic, Google, HuggingFace) throughout the application's lifecycle.

```python
# Located in app/services/llm_adapters.py
CLIENT = httpx.AsyncClient(timeout=45.0)
```

This single client instance is then used by all adapter classes:

```python
class BaseAdapter:
    # Class-level client shared by all adapters
    CLIENT = CLIENT
```

## Why is it Important?

### 1. Connection Pooling & Resource Efficiency

Instead of creating a new HTTP connection for each API request, the shared client maintains a pool of connections that can be reused. This is crucial because:

- **TCP Connection Overhead**: Opening and closing TCP connections is computationally expensive
- **Rate Limit Compliance**: LLM APIs often have rate limits on connection establishment
- **Latency Reduction**: Reusing connections significantly reduces request latency
- **Keep-Alive Benefits**: Persistent connections maintain keep-alive, reducing handshake overhead

### 2. Prevents Connection Exhaustion

Without a shared client, each adapter instance would create its own client, potentially leading to:

- **File Descriptor Exhaustion**: Too many open connections can exhaust system file descriptors
- **Memory Leaks**: Unclosed clients can cause memory leaks
- **"Too Many Open Files" Errors**: Operating system limits on open connections
- **Connection Pool Fragmentation**: Multiple small pools instead of one efficient pool

### 3. Consistent Timeout Behavior

The shared client enforces a consistent 45-second timeout across ALL LLM API calls:

- **Prevents Hung Requests**: No request can block indefinitely
- **Predictable Behavior**: All providers have the same timeout characteristics
- **Pipeline Optimization**: The 45-second timeout accounts for the multi-stage Ultra Synthesis™ pipeline
- **Error Recovery**: Consistent timeouts enable predictable error handling

### 4. Performance in the Ultra Synthesis Pipeline

The UltraAI system makes multiple parallel API calls during its 3-stage pipeline:

1. **Initial Response Stage**: Multiple models generate responses in parallel
2. **Peer Review Stage**: Models review each other's responses
3. **Final Synthesis Stage**: Lead model creates the final synthesis

With a shared client, these parallel requests efficiently reuse the same connection pool rather than competing for resources.

### 5. Production Stability

In production environments, the shared client pattern provides:

- **Resource Predictability**: Known maximum number of connections
- **Better Monitoring**: Single point to monitor all LLM API traffic
- **Graceful Degradation**: Connection pool limits prevent cascade failures
- **Memory Efficiency**: One client instance vs. potentially hundreds

## Implementation Details

### Current Implementation

```python
# app/services/llm_adapters.py

# A single, shared async client for all adapters to use
CLIENT = httpx.AsyncClient(timeout=45.0)

class BaseAdapter:
    """Base adapter for all LLM providers."""
    
    # Class-level client so wrappers can override per-adapter class
    CLIENT = CLIENT
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
```

### What NOT to Do

```python
# ❌ BAD: Creates a new client for each request
class OpenAIAdapter:
    async def generate(self, prompt):
        async with httpx.AsyncClient() as client:  # New client every time!
            response = await client.post(...)

# ❌ WORSE: Creates client but never closes it
class AnthropicAdapter:
    def __init__(self):
        self.client = httpx.AsyncClient()  # Memory leak!

# ❌ WORST: Multiple clients with different configurations
class GoogleAdapter:
    def __init__(self):
        self.read_client = httpx.AsyncClient(timeout=30.0)
        self.write_client = httpx.AsyncClient(timeout=60.0)
```

### Correct Usage Pattern

```python
# ✅ CORRECT: Use the shared CLIENT
class OpenAIAdapter(BaseAdapter):
    async def generate(self, prompt: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Use the shared CLIENT instance
        response = await self.CLIENT.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={...}
        )
        return response.json()
```

## Critical Rules

1. **NEVER create new `httpx.AsyncClient` instances** in adapter code
2. **ALWAYS use the shared `CLIENT` instance** from the base class
3. **DO NOT modify the timeout** on the shared client
4. **DO NOT close the shared client** during normal operation
5. **ALL new LLM adapters MUST use the shared client pattern**

## Performance Implications

### With Shared Client
- Connection establishment: ~50-200ms (first request only)
- Subsequent requests: ~5-10ms connection overhead
- Memory usage: ~10MB for client and connection pool
- File descriptors: ~10-50 depending on concurrent requests

### Without Shared Client
- Connection establishment: ~50-200ms (EVERY request)
- Memory usage: ~10MB × number of client instances
- File descriptors: Can exhaust system limits
- Risk of "Connection pool exhausted" errors

## Monitoring and Debugging

### Health Checks
The shared client's health can be monitored through:
- Connection pool statistics
- Active connection count
- Request success/failure rates
- Timeout occurrences

### Common Issues and Solutions

1. **"Connection pool exhausted"**
   - Cause: Too many concurrent requests
   - Solution: Implement request queuing or increase pool limits

2. **Timeout errors across all providers**
   - Cause: Network issues or overloaded client
   - Solution: Check network connectivity and client resource usage

3. **Memory growth over time**
   - Cause: Potential connection leak
   - Solution: Ensure proper request cleanup and error handling

## Future Considerations

1. **Connection Pool Tuning**: The default pool size may need adjustment based on production load
2. **Per-Provider Clients**: If providers have vastly different requirements, consider a pool of shared clients
3. **Circuit Breakers**: Add circuit breaker pattern on top of shared client for better resilience
4. **Metrics Collection**: Integrate prometheus metrics for connection pool monitoring

## References

- [httpx Documentation - Connection Pooling](https://www.python-httpx.org/advanced/#pool-limit-configuration)
- [httpx Best Practices](https://www.python-httpx.org/advanced/#client-instances)
- [Ultra Synthesis Pipeline Documentation](../architecture/ultra-synthesis-pipeline.md)