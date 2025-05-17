# Monitoring and Logging System

This document provides an overview of the monitoring and logging architecture for the Ultra backend.

## Overview

The monitoring and logging system consists of several components working together to provide comprehensive observability:

1. **Structured Logging** - JSON-formatted logs with context tracking
2. **Health Checks** - Component-level monitoring for system health assessment
3. **Circuit Breakers** - Preventing cascading failures when components fail
4. **Performance Metrics** - Tracking key performance indicators
5. **Request Tracing** - Following requests through the system
6. **Error Tracking** - Centralized error reporting and analysis

## Components

### Structured Logging

All logs are captured in JSON format to make them machine-readable and searchable. Key features include:

- **Context Tracking** - Every log entry includes request ID, user ID, and correlation ID
- **Log Categories** - Logs are categorized as REQUEST, RESPONSE, ERROR, etc.
- **PII Redaction** - Sensitive information is automatically redacted from logs
- **Performance Metrics** - Operation duration is included with logs
- **Log Sampling** - High-volume endpoints can be sampled at configurable rates

Location: `backend/utils/structured_logging.py`

Usage example:

```python
from backend.utils.structured_logging import get_enhanced_logger, LogCategory

logger = get_enhanced_logger(__name__)

# Basic logging
logger.info("Processing item", extra={"item_id": item_id})

# Performance logging
logger.performance("database_query", duration_ms=query_time)

# Error logging
try:
    # Some operation
    pass
except Exception as e:
    logger.error("Operation failed", exc_info=e)
```

### Health Checks

The health check system monitors the health of various components:

- **Database** - Connectivity and query execution
- **Redis** - Cache availability
- **LLM Providers** - API connectivity status
- **System Resources** - CPU, memory, and disk utilization

Health checks provide both summary health status and detailed component-level information. They're available through:

- `/health` - Overall health status
- `/health/details` - Detailed health information
- `/health/{service_name}` - Status of a specific service
- `/health/llm/providers` - Status of connected LLM providers
- `/health/circuit-breakers` - Circuit breaker status

Location: `backend/utils/health_check.py`

### Circuit Breakers

Circuit breakers prevent cascading failures by temporarily disabling services that are failing repeatedly. They support:

- **Automatic Tripping** - Open circuit after configurable number of failures
- **Automatic Recovery** - Half-open state to test service recovery
- **Configurable Thresholds** - Adjustable failure counts and timeouts
- **Status Monitoring** - Current state available through API

Location: `backend/utils/health_check.py` (CircuitBreaker class)

### Performance Metrics

Performance metrics are collected at various levels:

- **Request Level** - Duration of HTTP requests
- **Operation Level** - Duration of specific operations
- **Component Level** - Performance of database queries, API calls, etc.

Metrics can be accessed through:

- Structured logs containing performance information
- `/metrics` endpoint for Prometheus-compatible metrics

### Request Tracing

Requests are traced through the system using:

- **Request ID** - Unique identifier for each request
- **Correlation ID** - Identifier that follows a request across components
- **Context Propagation** - Request context available throughout the lifecycle

## Configuration

The monitoring system is configurable through environment variables:

```
# Logging configuration
LOG_LEVEL=INFO                 # Log level (DEBUG, INFO, WARNING, ERROR)
LOG_JSON=true                  # Enable JSON-formatted logs
LOG_DIR=logs                   # Directory for log files
LOG_HEADERS=false              # Include headers in request logs

# Health check configuration
HEALTH_CHECK_CACHE_TTL=60      # Cache health check results for 60 seconds
HEALTH_CHECK_TIMEOUT=5         # Timeout for health checks in seconds

# Metrics configuration
ENABLE_METRICS=true            # Enable metrics collection

# Sampling rates
REQUEST_SAMPLE_RATE_DEFAULT=1.0  # Default sample rate (1.0 = log everything)
```

## Directory Structure

Key files in the monitoring system:

```
backend/
  utils/
    health_check.py           # Health check system implementation
    structured_logging.py     # Enhanced structured logging
    monitoring.py             # Integration of all monitoring components
  routes/
    health_routes.py          # FastAPI endpoints for health checks
    metrics.py                # FastAPI endpoints for metrics
documentation/
  monitoring_and_logging.md   # This documentation
```

## Integration with External Systems

The monitoring system can integrate with external observability tools:

- **Logging** - JSON logs can be ingested by ELK Stack, Datadog, etc.
- **Metrics** - Prometheus-compatible metrics for collection
- **Error Tracking** - Sentry integration for error reporting
- **Tracing** - OpenTelemetry support for distributed tracing

## Best Practices

When writing code for Ultra, follow these monitoring and logging best practices:

1. **Use the Enhanced Logger** - Always use `get_enhanced_logger` instead of `print` or standard logging
2. **Include Context** - Add relevant context to logs (user IDs, operation IDs, etc.)
3. **Categorize Logs** - Use appropriate log categories from `LogCategory`
4. **Error Handling** - Log exceptions with `exc_info=e` to include stack traces
5. **Performance Monitoring** - Use `@with_performance_logging` decorator for critical functions
6. **Request Context** - Use `@with_request_context` decorator for request handlers
7. **Health Checks** - Register health checks for new components that support external services

## Troubleshooting

Common issues and solutions:

1. **Missing Context** - If logs are missing context, ensure request middleware is properly configured
2. **High Log Volume** - Use sampling for high-volume endpoints
3. **False Health Alarms** - Adjust health check thresholds or check intervals
4. **Circuit Breaker Issues** - Review circuit breaker configuration in health_check.py

## Future Improvements

Planned enhancements:

1. **Log Aggregation** - Centralized log storage and search
2. **Advanced Metrics** - More detailed performance metrics
3. **Alerting** - Alerting on critical errors and performance issues
4. **Dashboards** - Visualization of system health and performance
5. **Anomaly Detection** - Automatic detection of unusual patterns
