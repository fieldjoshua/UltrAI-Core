# Resilience Configuration Guide

This guide explains how to configure the resilience features of the Ultra system to meet your specific requirements.

## Overview

The Ultra system includes a comprehensive set of resilience features that can be configured through environment variables and configuration files. This guide explains the available configuration options and recommended values for different deployment scenarios.

## Configuration Methods

Resilience features can be configured through:

1. **Environment Variables**: Used for deployment-specific settings
2. **Configuration Files**: Used for application-wide defaults
3. **Code-Level Configuration**: Used for component-specific settings

## Core Resilience Features

### Circuit Breaker Configuration

Circuit breakers prevent cascading failures by stopping calls to failing services:

| Configuration Option | Environment Variable                 | Default | Description                                    |
| -------------------- | ------------------------------------ | ------- | ---------------------------------------------- |
| Failure Threshold    | `CIRCUIT_BREAKER_FAILURE_THRESHOLD`  | 5       | Number of failures before circuit opens        |
| Reset Timeout        | `CIRCUIT_BREAKER_RESET_TIMEOUT`      | 60      | Seconds to wait before attempting reset        |
| Half-Open Requests   | `CIRCUIT_BREAKER_HALF_OPEN_REQUESTS` | 1       | Number of requests to allow in half-open state |
| Timeout              | `CIRCUIT_BREAKER_TIMEOUT`            | 30      | Seconds before request times out               |

**Example Configuration**:

```python
# In config.py
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")),
    "reset_timeout": int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60")),
    "half_open_requests": int(os.getenv("CIRCUIT_BREAKER_HALF_OPEN_REQUESTS", "1")),
    "timeout": int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "30")),
}

# Provider-specific overrides
PROVIDER_CIRCUIT_BREAKER_CONFIG = {
    "openai": {
        "failure_threshold": 3,
        "reset_timeout": 30,
    },
    "anthropic": {
        "failure_threshold": 5,
        "reset_timeout": 60,
    },
}
```

**Recommended Values**:

- **Development**: Lower thresholds for testing (2-3)
- **Production**: Higher thresholds to avoid false positives (5-10)
- **High-Traffic**: Adjust based on traffic patterns (10-20)

### Retry Strategy Configuration

Retry strategies automatically retry failed operations:

| Configuration Option | Environment Variable   | Default | Description                          |
| -------------------- | ---------------------- | ------- | ------------------------------------ |
| Max Retries          | `RETRY_MAX_ATTEMPTS`   | 3       | Maximum number of retry attempts     |
| Initial Delay        | `RETRY_INITIAL_DELAY`  | 0.1     | Initial delay in seconds             |
| Max Delay            | `RETRY_MAX_DELAY`      | 2.0     | Maximum delay in seconds             |
| Backoff Factor       | `RETRY_BACKOFF_FACTOR` | 2.0     | Multiplier for delay between retries |
| Jitter               | `RETRY_JITTER`         | true    | Enable random jitter in retry delays |

**Example Configuration**:

```python
# In config.py
RETRY_CONFIG = {
    "max_retries": int(os.getenv("RETRY_MAX_ATTEMPTS", "3")),
    "initial_delay": float(os.getenv("RETRY_INITIAL_DELAY", "0.1")),
    "max_delay": float(os.getenv("RETRY_MAX_DELAY", "2.0")),
    "backoff_factor": float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0")),
    "jitter": os.getenv("RETRY_JITTER", "true").lower() in ("true", "1", "yes"),
}

# Operation-specific overrides
OPERATION_RETRY_CONFIG = {
    "database": {
        "max_retries": 5,
        "initial_delay": 0.05,
    },
    "llm_provider": {
        "max_retries": 2,
        "max_delay": 5.0,
    },
}
```

**Recommended Values**:

- **Development**: More retries for testing (3-5)
- **Production**: Balanced approach (2-3)
- **High-Traffic**: Fewer retries to prevent overload (1-2)

### Cache Configuration

Caching improves performance and resilience:

| Configuration Option | Environment Variable | Default          | Description                     |
| -------------------- | -------------------- | ---------------- | ------------------------------- |
| Memory Cache Size    | `CACHE_MEMORY_SIZE`  | 1000             | Number of items in memory cache |
| Disk Cache Directory | `CACHE_DISK_DIR`     | /tmp/ultra_cache | Directory for disk cache        |
| Redis URL            | `CACHE_REDIS_URL`    | None             | URL for Redis cache server      |
| Default TTL          | `CACHE_DEFAULT_TTL`  | 3600             | Default cache TTL in seconds    |
| Enable Cache         | `CACHE_ENABLED`      | true             | Enable or disable caching       |

**Example Configuration**:

```python
# In config.py
CACHE_CONFIG = {
    "memory_size": int(os.getenv("CACHE_MEMORY_SIZE", "1000")),
    "disk_dir": os.getenv("CACHE_DISK_DIR", "/tmp/ultra_cache"),
    "redis_url": os.getenv("CACHE_REDIS_URL"),
    "default_ttl": int(os.getenv("CACHE_DEFAULT_TTL", "3600")),
    "enabled": os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes"),
}

# Cache namespaces
CACHE_NAMESPACES = {
    "llm_responses": {
        "ttl": 3600,
        "levels": ["memory", "redis"],
    },
    "user_data": {
        "ttl": 300,
        "levels": ["memory"],
    },
    "document_analysis": {
        "ttl": 86400,
        "levels": ["memory", "disk", "redis"],
    },
}
```

**Recommended Values**:

- **Development**: Smaller caches with shorter TTLs
- **Production**: Larger caches with Redis for distribution
- **High-Traffic**: Very large memory cache with Redis cluster

### Request Queue Configuration

Request queues handle transient failures:

| Configuration Option | Environment Variable        | Default                      | Description                       |
| -------------------- | --------------------------- | ---------------------------- | --------------------------------- |
| Storage Path         | `QUEUE_STORAGE_PATH`        | /tmp/ultra_request_queue.pkl | Path for queue persistence        |
| Max Size             | `QUEUE_MAX_SIZE`            | 1000                         | Maximum queue size                |
| Worker Count         | `QUEUE_WORKER_COUNT`        | 5                            | Number of queue workers           |
| Processing Interval  | `QUEUE_PROCESSING_INTERVAL` | 1.0                          | Seconds between processing cycles |
| Enable Queue         | `QUEUE_ENABLED`             | true                         | Enable or disable request queuing |

**Example Configuration**:

```python
# In config.py
QUEUE_CONFIG = {
    "storage_path": os.getenv("QUEUE_STORAGE_PATH", "/tmp/ultra_request_queue.pkl"),
    "max_size": int(os.getenv("QUEUE_MAX_SIZE", "1000")),
    "worker_count": int(os.getenv("QUEUE_WORKER_COUNT", "5")),
    "processing_interval": float(os.getenv("QUEUE_PROCESSING_INTERVAL", "1.0")),
    "enabled": os.getenv("QUEUE_ENABLED", "true").lower() in ("true", "1", "yes"),
}

# Queue priorities
QUEUE_PRIORITIES = {
    "user_request": 10,
    "background_task": 5,
    "maintenance_task": 1,
}
```

**Recommended Values**:

- **Development**: Small queue with fewer workers
- **Production**: Larger queue with more workers
- **High-Traffic**: Very large queue with many workers

### System Operation Mode Configuration

System operation mode manages degradation:

| Configuration Option | Environment Variable               | Default | Description                           |
| -------------------- | ---------------------------------- | ------- | ------------------------------------- |
| Initial Mode         | `SYSTEM_INITIAL_MODE`              | NORMAL  | Initial system operation mode         |
| Auto Degradation     | `SYSTEM_AUTO_DEGRADATION`          | true    | Automatically degrade based on health |
| Mode Check Interval  | `SYSTEM_MODE_CHECK_INTERVAL`       | 60      | Seconds between mode checks           |
| User Notifications   | `SYSTEM_DEGRADATION_NOTIFICATIONS` | true    | Show degradation notifications        |

**Example Configuration**:

```python
# In config.py
OPERATION_MODE_CONFIG = {
    "initial_mode": os.getenv("SYSTEM_INITIAL_MODE", "NORMAL"),
    "auto_degradation": os.getenv("SYSTEM_AUTO_DEGRADATION", "true").lower() in ("true", "1", "yes"),
    "mode_check_interval": int(os.getenv("SYSTEM_MODE_CHECK_INTERVAL", "60")),
    "user_notifications": os.getenv("SYSTEM_DEGRADATION_NOTIFICATIONS", "true").lower() in ("true", "1", "yes"),
}

# Component degradation thresholds
COMPONENT_DEGRADATION_THRESHOLDS = {
    "database": {
        "response_time_ms": 1000,
        "error_rate_percent": 10,
    },
    "openai": {
        "response_time_ms": 2000,
        "error_rate_percent": 20,
    },
    "anthropic": {
        "response_time_ms": 3000,
        "error_rate_percent": 20,
    },
}
```

**Recommended Values**:

- **Development**: Auto-degradation off for testing
- **Production**: Auto-degradation on with reasonable thresholds
- **High-Traffic**: More aggressive thresholds to prevent overload

## LLM Provider-Specific Configuration

### Provider Failover Configuration

Configure provider failover priorities and capabilities:

| Configuration Option | Environment Variable      | Default          | Description                      |
| -------------------- | ------------------------- | ---------------- | -------------------------------- |
| Primary Provider     | `LLM_PRIMARY_PROVIDER`    | openai           | Primary LLM provider             |
| Failover Order       | `LLM_FAILOVER_ORDER`      | anthropic,google | Order of provider fallbacks      |
| Failover Timeout     | `LLM_FAILOVER_TIMEOUT`    | 5.0              | Seconds before failing over      |
| Capability Matching  | `LLM_CAPABILITY_MATCHING` | true             | Enable capability-based fallback |

**Example Configuration**:

```python
# In config.py
LLM_FAILOVER_CONFIG = {
    "primary_provider": os.getenv("LLM_PRIMARY_PROVIDER", "openai"),
    "failover_order": os.getenv("LLM_FAILOVER_ORDER", "anthropic,google").split(","),
    "failover_timeout": float(os.getenv("LLM_FAILOVER_TIMEOUT", "5.0")),
    "capability_matching": os.getenv("LLM_CAPABILITY_MATCHING", "true").lower() in ("true", "1", "yes"),
}

# Model capability mapping
MODEL_CAPABILITIES = {
    "openai": {
        "gpt-4o": ["summarization", "code_generation", "complex_reasoning"],
        "gpt-4": ["summarization", "code_generation", "complex_reasoning"],
        "gpt-3.5-turbo": ["summarization", "simple_reasoning"],
    },
    "anthropic": {
        "claude-3-opus": ["summarization", "code_generation", "complex_reasoning"],
        "claude-3-sonnet": ["summarization", "code_generation", "complex_reasoning"],
        "claude-3-haiku": ["summarization", "simple_reasoning"],
    },
    "google": {
        "gemini-1.5-pro": ["summarization", "code_generation", "complex_reasoning"],
        "gemini-1.5-flash": ["summarization", "simple_reasoning"],
    },
}

# Model fallback mapping
MODEL_FALLBACKS = {
    "openai": {
        "gpt-4o": ["anthropic/claude-3-opus", "google/gemini-1.5-pro"],
        "gpt-4": ["anthropic/claude-3-opus", "google/gemini-1.5-pro"],
        "gpt-3.5-turbo": ["anthropic/claude-3-haiku", "google/gemini-1.5-flash"],
    },
    "anthropic": {
        "claude-3-opus": ["openai/gpt-4o", "google/gemini-1.5-pro"],
        "claude-3-sonnet": ["openai/gpt-4", "google/gemini-1.5-pro"],
        "claude-3-haiku": ["openai/gpt-3.5-turbo", "google/gemini-1.5-flash"],
    },
}
```

**Recommended Values**:

- **Development**: Simple failover for testing
- **Production**: Capability-based matching for quality
- **High-Traffic**: Balance across providers for stability

### Provider-Specific Resilience

Configure resilience settings for each provider:

| Configuration Option | Environment Variable Pattern         | Description                 |
| -------------------- | ------------------------------------ | --------------------------- |
| Timeout              | `{PROVIDER}_TIMEOUT`                 | Request timeout in seconds  |
| Rate Limit           | `{PROVIDER}_RATE_LIMIT`              | Maximum requests per minute |
| Max Concurrent       | `{PROVIDER}_MAX_CONCURRENT`          | Maximum concurrent requests |
| Circuit Breaker      | `{PROVIDER}_CIRCUIT_BREAKER_ENABLED` | Enable circuit breaker      |

**Example Configuration**:

```python
# In config.py
PROVIDER_RESILIENCE_CONFIG = {
    "openai": {
        "timeout": float(os.getenv("OPENAI_TIMEOUT", "10.0")),
        "rate_limit": int(os.getenv("OPENAI_RATE_LIMIT", "3000")),
        "max_concurrent": int(os.getenv("OPENAI_MAX_CONCURRENT", "100")),
        "circuit_breaker_enabled": os.getenv("OPENAI_CIRCUIT_BREAKER_ENABLED", "true").lower() in ("true", "1", "yes"),
    },
    "anthropic": {
        "timeout": float(os.getenv("ANTHROPIC_TIMEOUT", "15.0")),
        "rate_limit": int(os.getenv("ANTHROPIC_RATE_LIMIT", "600")),
        "max_concurrent": int(os.getenv("ANTHROPIC_MAX_CONCURRENT", "50")),
        "circuit_breaker_enabled": os.getenv("ANTHROPIC_CIRCUIT_BREAKER_ENABLED", "true").lower() in ("true", "1", "yes"),
    },
    "google": {
        "timeout": float(os.getenv("GOOGLE_TIMEOUT", "12.0")),
        "rate_limit": int(os.getenv("GOOGLE_RATE_LIMIT", "1200")),
        "max_concurrent": int(os.getenv("GOOGLE_MAX_CONCURRENT", "75")),
        "circuit_breaker_enabled": os.getenv("GOOGLE_CIRCUIT_BREAKER_ENABLED", "true").lower() in ("true", "1", "yes"),
    },
}
```

**Recommended Values**:

- **OpenAI**: Timeout 10s, high concurrency
- **Anthropic**: Timeout 15s, moderate concurrency
- **Google**: Timeout 12s, moderate concurrency

## Database Resilience Configuration

Configure database resilience settings:

| Configuration Option | Environment Variable         | Default | Description                   |
| -------------------- | ---------------------------- | ------- | ----------------------------- |
| Connection Pool Size | `DB_POOL_SIZE`               | 10      | Maximum database connections  |
| Connection Timeout   | `DB_CONNECTION_TIMEOUT`      | 5.0     | Connection timeout in seconds |
| Retry Attempts       | `DB_RETRY_ATTEMPTS`          | 3       | Maximum retry attempts        |
| Circuit Breaker      | `DB_CIRCUIT_BREAKER_ENABLED` | true    | Enable circuit breaker        |

**Example Configuration**:

```python
# In config.py
DATABASE_RESILIENCE_CONFIG = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "connection_timeout": float(os.getenv("DB_CONNECTION_TIMEOUT", "5.0")),
    "retry_attempts": int(os.getenv("DB_RETRY_ATTEMPTS", "3")),
    "circuit_breaker_enabled": os.getenv("DB_CIRCUIT_BREAKER_ENABLED", "true").lower() in ("true", "1", "yes"),
}

# Query-specific settings
QUERY_RESILIENCE_CONFIG = {
    "read": {
        "timeout": 3.0,
        "retries": 3,
    },
    "write": {
        "timeout": 5.0,
        "retries": 2,
    },
    "transaction": {
        "timeout": 10.0,
        "retries": 1,
    },
}
```

**Recommended Values**:

- **Development**: Smaller pool with more retries
- **Production**: Larger pool with balanced retries
- **High-Traffic**: Very large pool with connection backoff

## External API Resilience Configuration

Configure resilience for external API calls:

| Configuration Option | Environment Variable          | Default | Description                 |
| -------------------- | ----------------------------- | ------- | --------------------------- |
| Default Timeout      | `API_DEFAULT_TIMEOUT`         | 10.0    | Default timeout in seconds  |
| Retry Attempts       | `API_RETRY_ATTEMPTS`          | 2       | Maximum retry attempts      |
| Circuit Breaker      | `API_CIRCUIT_BREAKER_ENABLED` | true    | Enable circuit breaker      |
| Rate Limit           | `API_RATE_LIMIT`              | 100     | Maximum requests per minute |

**Example Configuration**:

```python
# In config.py
EXTERNAL_API_RESILIENCE_CONFIG = {
    "default_timeout": float(os.getenv("API_DEFAULT_TIMEOUT", "10.0")),
    "retry_attempts": int(os.getenv("API_RETRY_ATTEMPTS", "2")),
    "circuit_breaker_enabled": os.getenv("API_CIRCUIT_BREAKER_ENABLED", "true").lower() in ("true", "1", "yes"),
    "rate_limit": int(os.getenv("API_RATE_LIMIT", "100")),
}

# API-specific overrides
API_SPECIFIC_CONFIG = {
    "payment_gateway": {
        "timeout": 30.0,
        "retries": 3,
        "critical": true,
    },
    "notification_service": {
        "timeout": 5.0,
        "retries": 1,
        "critical": false,
    },
}
```

**Recommended Values**:

- **Critical APIs**: Longer timeouts, more retries
- **Non-Critical APIs**: Shorter timeouts, fewer retries

## Advanced Configuration

### Composite Resilience Strategies

Configure composite resilience strategies combining multiple patterns:

```python
# In config.py
COMPOSITE_RESILIENCE_CONFIG = {
    "openai_service": {
        "circuit_breaker": {
            "enabled": true,
            "failure_threshold": 5,
            "reset_timeout": 60,
        },
        "retry": {
            "enabled": true,
            "max_retries": 2,
            "initial_delay": 0.1,
        },
        "timeout": {
            "enabled": true,
            "timeout_seconds": 10.0,
        },
        "rate_limit": {
            "enabled": true,
            "max_calls": 3000,
            "period_seconds": 60,
        },
        "bulkhead": {
            "enabled": true,
            "max_concurrent_calls": 100,
        },
        "fallback": {
            "enabled": true,
            "fallback_service": "anthropic_service",
        },
    }
}
```

### System-Wide Resilience

Configure system-wide resilience settings:

```python
# In config.py
SYSTEM_RESILIENCE_CONFIG = {
    "degradation_thresholds": {
        "error_rate": 0.05,  # 5% error rate
        "response_time": 2.0,  # 2 second response time
        "availability": 0.99,  # 99% availability
    },
    "health_check": {
        "interval": 30,  # seconds
        "required_services": ["database", "cache", "openai"],
        "optional_services": ["anthropic", "google"],
    },
    "graceful_shutdown": {
        "timeout": 30,  # seconds
        "drain_connections": true,
    },
}
```

## Environment-Specific Recommendations

### Development Environment

```ini
# .env.development
CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
RETRY_MAX_ATTEMPTS=5
CACHE_MEMORY_SIZE=100
CACHE_DISK_DIR=/tmp/ultra_dev_cache
QUEUE_MAX_SIZE=100
QUEUE_WORKER_COUNT=2
SYSTEM_AUTO_DEGRADATION=false
```

### Testing Environment

```ini
# .env.testing
CIRCUIT_BREAKER_FAILURE_THRESHOLD=2
RETRY_MAX_ATTEMPTS=2
CACHE_ENABLED=false
QUEUE_ENABLED=false
SYSTEM_INITIAL_MODE=NORMAL
SYSTEM_AUTO_DEGRADATION=false
```

### Production Environment

```ini
# .env.production
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
RETRY_MAX_ATTEMPTS=3
CACHE_MEMORY_SIZE=10000
CACHE_DISK_DIR=/var/cache/ultra
CACHE_REDIS_URL=redis://cache.example.com:6379/0
QUEUE_MAX_SIZE=10000
QUEUE_WORKER_COUNT=10
QUEUE_STORAGE_PATH=/var/spool/ultra/request_queue.pkl
SYSTEM_AUTO_DEGRADATION=true
SYSTEM_MODE_CHECK_INTERVAL=30
```

### High-Traffic Environment

```ini
# .env.high-traffic
CIRCUIT_BREAKER_FAILURE_THRESHOLD=10
RETRY_MAX_ATTEMPTS=2
CACHE_MEMORY_SIZE=50000
CACHE_REDIS_URL=redis://cache-cluster.example.com:6379/0
QUEUE_MAX_SIZE=50000
QUEUE_WORKER_COUNT=20
DB_POOL_SIZE=50
OPENAI_MAX_CONCURRENT=200
ANTHROPIC_MAX_CONCURRENT=100
SYSTEM_AUTO_DEGRADATION=true
SYSTEM_MODE_CHECK_INTERVAL=15
```

## Configuration Management

### Loading Configuration

Configuration is loaded hierarchically:

1. Default values in code
2. Values from configuration files
3. Values from environment variables

```python
# Example configuration loading
def load_resilience_config():
    """Load resilience configuration from environment and files."""
    # Start with defaults
    config = default_resilience_config()

    # Load from configuration file if present
    config_file = os.getenv("RESILIENCE_CONFIG_FILE")
    if config_file and os.path.exists(config_file):
        with open(config_file, "r") as f:
            file_config = json.load(f)
            deep_update(config, file_config)

    # Override with environment variables
    env_overrides = {}
    for key, value in os.environ.items():
        if key.startswith("CIRCUIT_BREAKER_") or \
           key.startswith("RETRY_") or \
           key.startswith("CACHE_") or \
           key.startswith("QUEUE_") or \
           key.startswith("SYSTEM_"):
            env_key = key.lower()
            env_overrides[env_key] = parse_env_value(value)

    # Apply environment overrides
    apply_env_overrides(config, env_overrides)

    return config
```

### Configuration Validation

Validate configuration to prevent errors:

```python
def validate_resilience_config(config):
    """Validate resilience configuration."""
    errors = []

    # Validate circuit breaker config
    if config["circuit_breaker"]["failure_threshold"] < 1:
        errors.append("Circuit breaker failure threshold must be at least 1")

    if config["circuit_breaker"]["reset_timeout"] < 1:
        errors.append("Circuit breaker reset timeout must be at least 1 second")

    # Validate retry config
    if config["retry"]["max_retries"] < 0:
        errors.append("Max retries cannot be negative")

    if config["retry"]["initial_delay"] <= 0:
        errors.append("Initial delay must be positive")

    # Validate cache config
    if config["cache"]["memory_size"] < 1:
        errors.append("Memory cache size must be at least 1")

    if config["cache"]["default_ttl"] <= 0:
        errors.append("Default TTL must be positive")

    # Validate queue config
    if config["queue"]["max_size"] < 1:
        errors.append("Queue max size must be at least 1")

    if config["queue"]["worker_count"] < 1:
        errors.append("Worker count must be at least 1")

    # Return errors if any
    if errors:
        raise ConfigurationError("\n".join(errors))

    return True
```

## Conclusion

Proper configuration of resilience features is essential for optimal system performance and reliability. This guide provides a comprehensive overview of available configuration options and recommended values for different deployment scenarios. Adjust these settings based on your specific requirements and monitor system behavior to fine-tune the configuration over time.
