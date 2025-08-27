# UltraAI Core Monitoring Setup

This directory contains the monitoring and observability configuration for UltraAI Core.

## Quick Start

### Local Development

1. Start the monitoring stack:
```bash
docker-compose up -d
```

2. Access the services:
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Loki**: http://localhost:3100

3. The UltraAI dashboard will be automatically provisioned in Grafana.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  UltraAI Core   │────▶│   Prometheus    │────▶│     Grafana     │
│   /api/metrics  │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               ▲
         │                                               │
         ▼                                               │
┌─────────────────┐     ┌─────────────────┐            │
│                 │     │                 │             │
│   Application   │────▶│      Loki       │─────────────┘
│      Logs       │     │                 │
└─────────────────┘     └─────────────────┘
```

## Components

### Prometheus
- Scrapes metrics from `/api/metrics` endpoint
- Evaluates alerting rules
- Stores time-series data

### Grafana
- Visualizes metrics from Prometheus
- Displays logs from Loki
- Pre-configured dashboard for UltraAI metrics

### Loki
- Aggregates application logs
- Provides log querying and filtering
- Integrated with Grafana for visualization

### Alertmanager
- Handles alerts from Prometheus
- Routes alerts to appropriate channels
- Manages alert silencing and grouping

## Metrics

### Application Metrics
- `http_requests_total` - Total HTTP requests by status and method
- `http_request_duration_seconds` - Request latency histogram
- `llm_requests_total` - LLM API calls by provider and model
- `llm_cost_total` - Cumulative cost by provider and model
- `llm_tokens_total` - Token usage by type and model
- `pipeline_stage_duration_seconds` - Pipeline stage execution time
- `rate_limit_exceeded_total` - Rate limit violations

### System Metrics
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage
- `python_gc_objects_collected_total` - Garbage collection stats
- `database_connections_active` - Active DB connections
- `redis_connected_clients` - Redis client connections

## Alerting Rules

### Critical Alerts
- **ServiceDown**: Service unreachable for 2+ minutes
- **HighErrorRate**: Error rate > 5% for 5+ minutes
- **LLMProviderFailure**: LLM provider error rate > 10%
- **DatabaseConnectionPoolExhausted**: DB connections > 90%

### Warning Alerts
- **HighLatency**: 95th percentile latency > 1s
- **HighLLMCost**: Hourly cost > $10
- **HighMemoryUsage**: Memory usage > 80%
- **RateLimitingActive**: > 10 violations/minute
- **RedisUnavailable**: Redis down for 2+ minutes
- **LongRunningPipeline**: Stage duration > 30s

## Log Format

Application logs follow structured JSON format:
```json
{
  "timestamp": "2024-01-20T10:30:45.123456",
  "level": "INFO",
  "logger": "app.services.orchestration",
  "message": "Pipeline completed successfully",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "extra": {
    "duration": 2.5,
    "models_used": ["gpt-4", "claude-3"],
    "cost": 0.05
  }
}
```

## Dashboard Customization

### Adding New Panels

1. Access Grafana at http://localhost:3001
2. Navigate to the UltraAI dashboard
3. Click "Add panel"
4. Configure your query and visualization
5. Save the dashboard

### Exporting Dashboard

1. Go to Dashboard settings
2. Click "JSON Model"
3. Copy the JSON
4. Save to `grafana/dashboards/your-dashboard.json`

## Production Considerations

### Retention Policies
- Prometheus: 15 days (configurable)
- Loki: 7 days (configurable)
- Consider external storage for long-term retention

### High Availability
- Run multiple Prometheus instances
- Use Prometheus federation for aggregation
- Configure Loki with S3 backend
- Use Grafana Cloud for managed solution

### Security
- Enable authentication in Grafana
- Use TLS for all connections
- Restrict metrics endpoint access
- Implement RBAC for dashboards

## Troubleshooting

### Prometheus Not Scraping
1. Check target status: http://localhost:9090/targets
2. Verify network connectivity
3. Check application logs for metric generation errors

### No Data in Grafana
1. Verify datasource configuration
2. Check Prometheus is receiving data
3. Validate dashboard queries

### Missing Logs
1. Check Loki is running: `docker-compose ps`
2. Verify log shipping configuration
3. Check application log format

### Alert Not Firing
1. Check alert rules in Prometheus
2. Verify alerting conditions are met
3. Check Alertmanager configuration