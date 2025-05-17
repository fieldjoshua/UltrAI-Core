# Metrics Collection

## Overview

This document outlines the metrics collection strategy for the Ultra application.

## Key Metrics

### Application Metrics

#### Request Metrics

- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Request size distribution
- Response size distribution

#### LLM Metrics

- Model usage by provider
- Token consumption
- Processing time by model
- Cost per request
- Cache hit ratio

#### Business Metrics

- Active users
- Documents processed
- Analysis patterns used
- Feature adoption
- User engagement

### System Metrics

#### Resource Utilization

- CPU usage
- Memory usage
- Disk I/O
- Network bandwidth
- Thread/process count

#### Database Metrics

- Query performance
- Connection pool usage
- Transaction rates
- Lock wait times
- Replication lag

#### Cache Metrics

- Hit/miss ratio
- Eviction rate
- Memory usage
- Key distribution
- TTL effectiveness

## Implementation

### Prometheus Setup

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ultra-api'
    static_configs:
      - targets: ['localhost:8085']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['localhost:9121']
```

### Application Instrumentation

```python
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

llm_tokens = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['provider', 'model']
)

# Decorator for timing
def track_request_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            status = 'success'
        except Exception as e:
            status = 'error'
            raise
        finally:
            duration = time.time() - start_time
            request_duration.labels(
                method=request.method,
                endpoint=request.path
            ).observe(duration)

            request_count.labels(
                method=request.method,
                endpoint=request.path,
                status=status
            ).inc()

        return result
    return wrapper
```

### Custom Business Metrics

```python
class BusinessMetrics:
    def __init__(self):
        self.analysis_counter = Counter(
            'analyses_total',
            'Total analyses performed',
            ['pattern', 'model', 'status']
        )

        self.document_size = Histogram(
            'document_size_bytes',
            'Document sizes processed',
            buckets=[1000, 10000, 100000, 1000000, 10000000]
        )

        self.user_activity = Summary(
            'user_activity_score',
            'User activity scores'
        )

    def track_analysis(self, pattern, model, status):
        self.analysis_counter.labels(
            pattern=pattern,
            model=model,
            status=status
        ).inc()

    def track_document(self, size_bytes):
        self.document_size.observe(size_bytes)

    def track_user_activity(self, user_id, score):
        self.user_activity.observe(score)
```

## Grafana Dashboards

### API Performance Dashboard

```json
{
  "dashboard": {
    "title": "API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legend": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)",
            "legend": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status='error'}[5m]) / rate(http_requests_total[5m]) * 100"
          }
        ]
      }
    ]
  }
}
```

### LLM Usage Dashboard

```json
{
  "dashboard": {
    "title": "LLM Usage",
    "panels": [
      {
        "title": "Token Usage by Provider",
        "type": "pie",
        "targets": [
          {
            "expr": "sum by (provider) (llm_tokens_total)"
          }
        ]
      },
      {
        "title": "Request Distribution",
        "type": "bar",
        "targets": [
          {
            "expr": "sum by (model) (rate(llm_requests_total[1h]))"
          }
        ]
      },
      {
        "title": "Cost Tracking",
        "type": "table",
        "targets": [
          {
            "expr": "llm_cost_total"
          }
        ]
      }
    ]
  }
}
```

## Alert Rules

### Performance Alerts

```yaml
groups:
  - name: performance
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: 'High response time detected'
          description: '95th percentile response time is {{ $value }}s'

      - alert: HighErrorRate
        expr: rate(http_requests_total{status='error'}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: 'High error rate detected'
          description: 'Error rate is {{ $value }}%'
```

### Resource Alerts

```yaml
groups:
  - name: resources
    rules:
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: 'High memory usage'
          description: 'Memory usage is {{ $value }}%'

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) > 0.85
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: 'Low disk space'
          description: 'Disk usage is {{ $value }}%'
```

## Data Export

### Metrics Export Format

```python
def export_metrics(start_time, end_time, metrics):
    export_data = {
        'period': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        },
        'metrics': {}
    }

    for metric in metrics:
        query = f"avg_over_time({metric}[{end_time - start_time}])"
        result = prometheus.query(query)
        export_data['metrics'][metric] = result

    return export_data
```

### Reporting Integration

```python
class MetricsReporter:
    def generate_daily_report(self):
        metrics = [
            'http_requests_total',
            'http_request_duration_seconds',
            'llm_tokens_total',
            'active_users'
        ]

        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)

        report_data = self.export_metrics(start_time, end_time, metrics)

        return self.format_report(report_data)
```

## Best Practices

1. **Use consistent naming conventions**
2. **Add meaningful labels**
3. **Avoid high-cardinality labels**
4. **Use appropriate metric types**
5. **Set reasonable bucket boundaries**
6. **Monitor metric volume**
7. **Test alert thresholds**
8. **Document metric meanings**
