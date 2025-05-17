# Monitoring and Metrics Integration Guide

This document describes the implementation of the monitoring and metrics system in the Ultra application, using Prometheus for metrics collection and visualization.

## Overview

The monitoring system provides comprehensive visibility into the application's performance, resource usage, and operational health. It includes:

1. **API Metrics**: Request counts, latencies, status codes, request/response sizes
2. **System Resource Metrics**: CPU, memory, disk usage
3. **LLM Provider Metrics**: Request counts, token usage, response times
4. **Cache Metrics**: Hit/miss ratios, cache sizes
5. **Document Processing Metrics**: Document counts, chunk counts, processing times

## Implementation Details

### Prometheus Integration

The system uses Prometheus for metrics collection and aggregation. Prometheus metrics are exposed in two ways:

1. A dedicated metrics server on a configurable port (default: 8081)
2. A `/metrics` endpoint on the main API server

This provides flexibility for different monitoring setups.

### Metrics Types

The metrics implementation uses standard Prometheus metric types:

- **Counters**: Monotonically increasing counters for events like requests, tokens, cache hits
- **Gauges**: Point-in-time measurements like CPU usage, memory consumption
- **Histograms**: Distribution of values like request durations, with configurable buckets

### Key Components

#### 1. `MetricsCollector` Class

The `MetricsCollector` class in `backend/utils/metrics.py` acts as a central registry for all metrics. It's implemented as a singleton to ensure metrics are consistently registered and accessed across the application.

```python
class MetricsCollector:
    """Singleton class for collecting and managing Prometheus metrics."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsCollector, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
```

#### 2. API Metrics Middleware

The `MetricsMiddleware` class integrates with FastAPI to automatically track HTTP request metrics:

```python
class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP metrics for FastAPI requests."""

    async def dispatch(self, request: Request, call_next):
        # Track request metrics...
```

#### 3. LLM Adapter Metrics

LLM usage metrics are collected through:

1. Direct implementation in adapter classes (like `AnthropicAdapter`)
2. A wrapper-based approach with `MetricsAdapterWrapper` that can be applied to any adapter

The wrapper approach allows adding metrics without modifying existing adapters:

```python
class MetricsAdapterWrapper(BaseAdapter):
    """Wrapper for BaseAdapter that adds metrics tracking."""

    def __init__(self, wrapped_adapter: BaseAdapter):
        """Initialize with a wrapped adapter."""
        self.adapter = wrapped_adapter
        # ...
```

#### 4. Health Check Integration

System metrics are integrated with the health check system to combine operational health monitoring with performance metrics.

## Configuration

Metrics collection can be configured through environment variables:

```
# Prometheus metrics configuration
ENABLE_METRICS=true          # Enable/disable metrics collection
METRICS_PORT=8081            # Port for the standalone metrics server
SYSTEM_METRICS_INTERVAL=15   # Interval (seconds) for system metrics collection
```

## Metric Naming Convention

Metrics follow a consistent naming convention:

- `ultra_http_*`: API-related metrics
- `ultra_system_*`: System resource metrics
- `ultra_llm_*`: LLM provider metrics
- `ultra_cache_*`: Cache-related metrics
- `ultra_documents_*`: Document processing metrics

## Available Metrics

### API Metrics

| Metric Name                           | Type      | Description                         | Labels                              |
| ------------------------------------- | --------- | ----------------------------------- | ----------------------------------- |
| `ultra_http_requests_total`           | Counter   | Total count of HTTP requests        | `method`, `endpoint`, `status_code` |
| `ultra_http_request_duration_seconds` | Histogram | HTTP request latency in seconds     | `method`, `endpoint`                |
| `ultra_http_requests_in_progress`     | Gauge     | Number of HTTP requests in progress | `method`, `endpoint`                |
| `ultra_http_request_size_bytes`       | Histogram | HTTP request size in bytes          | `method`, `endpoint`                |
| `ultra_http_response_size_bytes`      | Histogram | HTTP response size in bytes         | `method`, `endpoint`, `status_code` |

### System Metrics

| Metric Name                         | Type  | Description             | Labels |
| ----------------------------------- | ----- | ----------------------- | ------ |
| `ultra_system_cpu_usage`            | Gauge | CPU usage percentage    | -      |
| `ultra_system_memory_usage_bytes`   | Gauge | Memory usage in bytes   | -      |
| `ultra_system_memory_usage_percent` | Gauge | Memory usage percentage | -      |
| `ultra_system_disk_usage_bytes`     | Gauge | Disk usage in bytes     | -      |
| `ultra_system_disk_usage_percent`   | Gauge | Disk usage percentage   | -      |

### LLM Metrics

| Metric Name                          | Type      | Description                    | Labels                        |
| ------------------------------------ | --------- | ------------------------------ | ----------------------------- |
| `ultra_llm_requests_total`           | Counter   | Total number of LLM requests   | `provider`, `model`, `status` |
| `ultra_llm_request_duration_seconds` | Histogram | LLM request latency in seconds | `provider`, `model`           |
| `ultra_llm_tokens_input_total`       | Counter   | Total number of input tokens   | `provider`, `model`           |
| `ultra_llm_tokens_output_total`      | Counter   | Total number of output tokens  | `provider`, `model`           |

### Cache Metrics

| Metric Name                | Type    | Description                      | Labels       |
| -------------------------- | ------- | -------------------------------- | ------------ |
| `ultra_cache_hits_total`   | Counter | Total number of cache hits       | `cache_name` |
| `ultra_cache_misses_total` | Counter | Total number of cache misses     | `cache_name` |
| `ultra_cache_size_total`   | Gauge   | Current number of items in cache | `cache_name` |

### Document Processing Metrics

| Metric Name                                  | Type      | Description                               | Labels |
| -------------------------------------------- | --------- | ----------------------------------------- | ------ |
| `ultra_documents_processed_total`            | Counter   | Total number of documents processed       | -      |
| `ultra_document_chunks_processed_total`      | Counter   | Total number of document chunks processed | -      |
| `ultra_document_processing_duration_seconds` | Histogram | Document processing time in seconds       | -      |

## Visualization and Dashboards

The collected metrics can be visualized using Grafana, which can be connected to the Prometheus server. Sample Grafana dashboards will be provided separately.

## Future Enhancements

1. **More Detailed LLM Metrics**: Additional breakdowns by prompt types, completion qualities
2. **Business Metrics**: Token costs, usage patterns, user activity
3. **Alerting Integration**: Setting up alerts for critical metrics thresholds
4. **Distributed Tracing**: Adding OpenTelemetry integration for request tracing

## Conclusion

This monitoring and metrics implementation provides comprehensive visibility into the Ultra application's performance and resource usage. The Prometheus integration offers a standard, scalable approach to metrics collection that can be easily extended for future requirements.
