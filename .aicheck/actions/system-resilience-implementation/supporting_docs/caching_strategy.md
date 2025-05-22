# Caching Strategy

## Overview

Multi-layer caching strategy to improve performance and provide resilience during provider failures.

## Cache Layers

### 1. Browser Cache (L1)

- Local storage for user preferences
- Session data
- Recent queries
- TTL: 1 hour

### 2. CDN Cache (L2)

- Static assets
- Common responses
- Public data
- TTL: 24 hours

### 3. Application Cache (L3)

- In-memory cache (Node.js)
- Request deduplication
- Response buffering
- TTL: 15 minutes

### 4. Redis Cache (L4)

- Distributed cache
- Shared across instances
- Persistent storage
- TTL: 1-6 hours

### 5. Database Cache (L5)

- Analysis results
- User history
- Model outputs
- TTL: 7 days

## Caching Strategies

### Response Caching

```python
def cache_llm_response(key, response, ttl=3600):
    # Hash the request
    cache_key = hashlib.sha256(key.encode()).hexdigest()

    # Store in multiple layers
    local_cache.set(cache_key, response, ttl=900)  # 15 min
    redis_cache.setex(cache_key, ttl, response)    # 1 hour

    # Store metadata
    metadata = {
        'timestamp': time.time(),
        'provider': response.provider,
        'model': response.model
    }
    redis_cache.hset(f"{cache_key}:meta", mapping=metadata)
```

### Query Deduplication

- Identify duplicate requests
- Merge identical queries
- Share responses
- Reduce API calls

### Preemptive Caching

- Popular queries
- Common patterns
- Predicted requests
- Background warming

## Cache Keys

### Key Structure

```
{service}:{version}:{hash}:{metadata}
```

Examples:

- `llm:v1:sha256_hash:gpt4`
- `analysis:v2:sha256_hash:comparative`
- `user:v1:user_id:preferences`

### Key Generation

```python
def generate_cache_key(service, payload, metadata=None):
    # Normalize payload
    normalized = json.dumps(payload, sort_keys=True)

    # Generate hash
    hash_value = hashlib.sha256(normalized.encode()).hexdigest()

    # Build key
    parts = [service, "v1", hash_value]
    if metadata:
        parts.append(metadata)

    return ":".join(parts)
```

## Invalidation

### TTL-Based

- Automatic expiration
- Sliding windows
- Refresh on access
- Background updates

### Event-Based

- Model updates
- Configuration changes
- User modifications
- System events

### Manual

- Admin controls
- Debug operations
- Emergency flush
- Selective clearing

## Cache Warming

### Startup Warming

```python
async def warm_cache_on_startup():
    # Load popular queries
    popular_queries = await get_popular_queries()

    # Pre-fetch responses
    for query in popular_queries:
        if not cache.exists(query.key):
            response = await fetch_response(query)
            cache.set(query.key, response)
```

### Periodic Warming

- Scheduled jobs
- Off-peak processing
- Priority queues
- Resource limits

## Performance Optimization

### Hit Rate Optimization

- Monitor cache metrics
- Adjust TTL values
- Optimize key design
- Improve algorithms

### Memory Management

- LRU eviction
- Size limits
- Compression
- Tiered storage

### Network Optimization

- Batch operations
- Pipeline commands
- Connection pooling
- Regional caches

## Resilience Features

### Fallback Mechanisms

1. Cache miss → API call
2. API fail → Stale cache
3. Cache fail → Direct query
4. All fail → Error message

### Graceful Degradation

```python
async def get_with_fallback(key):
    try:
        # Try cache first
        cached = await cache.get(key)
        if cached:
            return cached

        # Try API
        response = await api.call(key)
        cache.set(key, response)
        return response

    except APIError:
        # Try stale cache
        stale = await cache.get(key, include_expired=True)
        if stale:
            return stale

        # Last resort
        return get_default_response()
```

## Monitoring

### Metrics

- Cache hit rate
- Response times
- Memory usage
- Eviction rate

### Alerts

- Low hit rate
- High latency
- Memory pressure
- Connection issues

### Dashboards

- Real-time metrics
- Historical trends
- Performance analysis
- Capacity planning

## Configuration

```yaml
cache:
  redis:
    host: localhost
    port: 6379
    db: 0
    max_connections: 100

  ttl:
    default: 3600
    user_preferences: 86400
    llm_responses: 3600
    analysis_results: 7200

  limits:
    max_memory: 1gb
    max_keys: 1000000
    eviction_policy: lru

  warming:
    enabled: true
    interval: 3600
    max_items: 1000
```
