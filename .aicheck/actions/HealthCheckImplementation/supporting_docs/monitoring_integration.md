# Health Check Monitoring Integration

This document provides examples of integrating Ultra's health check system with various monitoring tools and platforms.

## Prometheus Integration

Prometheus can scrape Ultra's health check endpoints to collect metrics on system health. Here's how to configure it:

### Prometheus Configuration

```yaml
scrape_configs:
  - job_name: 'ultra-health'
    metrics_path: '/api/health'
    scrape_interval: 60s
    static_configs:
      - targets: ['ultra-api:8000']
    json_parse:
      status:
        path: $.status
        type: string
      uptime:
        path: $.uptime
        type: float
```

### Detailed Metrics Collection

For more detailed metrics, use the `json_parse` configuration to extract specific values:

```yaml
json_parse:
  # Overall status
  status:
    path: $.status
    type: string

  # Database status
  database_status:
    path: $.services.database.status
    type: string

  # Redis status
  redis_status:
    path: $.services.redis.status
    type: string

  # Memory usage
  memory_percent:
    path: $.system.memory.percent_used
    type: float

  # Disk usage
  disk_percent:
    path: $.system.disk.percent_used
    type: float
```

### Example Prometheus Queries

```
# Check if any service is critical
ultra_health_status{status="critical"}

# Memory usage trend
rate(ultra_health_memory_percent[1h])

# Disk usage alert
ultra_health_disk_percent > 90
```

## Grafana Dashboard

Create a Grafana dashboard to visualize Ultra's health metrics:

### Dashboard JSON

```json
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "PBFA97CFB590B2093"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [
            {
              "options": {
                "critical": {
                  "color": "red",
                  "index": 2
                },
                "degraded": {
                  "color": "yellow",
                  "index": 1
                },
                "ok": {
                  "color": "green",
                  "index": 0
                }
              },
              "type": "value"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "yellow",
                "value": 1
              },
              {
                "color": "red",
                "value": 2
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        },
        "textMode": "auto"
      },
      "pluginVersion": "10.0.3",
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "PBFA97CFB590B2093"
          },
          "expr": "ultra_health_status",
          "refId": "A"
        }
      ],
      "title": "Overall Health Status",
      "type": "stat"
    }
  ],
  "refresh": "1m",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Ultra Health Dashboard",
  "uid": "ultra-health",
  "version": 1,
  "weekStart": ""
}
```

## Kubernetes Integration

### Liveness Probe

Use the basic health endpoint for Kubernetes liveness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probe

Use a more detailed health endpoint for readiness probes:

```yaml
readinessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Startup Probe

For Kubernetes 1.18+, use a startup probe to handle slower startup times:

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 5
  failureThreshold: 12 # Allow 1 minute (12 * 5s) for startup
```

## AWS CloudWatch Integration

### CloudWatch Agent Configuration

Configure the CloudWatch agent to scrape the health check endpoints:

```json
{
  "metrics": {
    "metrics_collected": {
      "statsd": {
        "service_address": ":8125",
        "metrics_collection_interval": 60
      },
      "collectd": {
        "metrics_aggregation_interval": 60
      },
      "procstat": [
        {
          "pattern": "ultra",
          "measurement": ["cpu_usage", "memory_rss"]
        }
      ],
      "http": [
        {
          "endpoint": "http://localhost:8000/api/health/system",
          "measurement": [
            {
              "name": "memory_utilization",
              "json_path": "$.details.memory.percent",
              "unit": "Percent"
            },
            {
              "name": "disk_utilization",
              "json_path": "$.details.disk.percent",
              "unit": "Percent"
            },
            {
              "name": "cpu_utilization",
              "json_path": "$.details.cpu.percent",
              "unit": "Percent"
            }
          ]
        }
      ]
    }
  }
}
```

### CloudWatch Dashboard

Create a CloudWatch dashboard to visualize the metrics:

```json
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [["Ultra", "memory_utilization"]],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "Memory Utilization",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [["Ultra", "disk_utilization"]],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "Disk Utilization",
        "period": 300
      }
    }
  ]
}
```

## Datadog Integration

### Datadog Agent Configuration

Configure the Datadog agent to monitor the health check endpoints:

```yaml
init_config:

instances:
  - url: http://localhost:8000/api/health
    timeout: 5
    headers:
      Content-Type: application/json
    collect_response_time: true
    skip_proxy: true
    checks:
      - type: value
        name: system.status
        path: $.status
        result_type: string
        expected_value: ok
      - type: value
        name: system.uptime
        path: $.uptime
        result_type: float

  - url: http://localhost:8000/api/health/system
    timeout: 5
    headers:
      Content-Type: application/json
    collect_response_time: true
    skip_proxy: true
    checks:
      - type: value
        name: system.memory.percent
        path: $.details.memory.percent
        result_type: float
      - type: value
        name: system.disk.percent
        path: $.details.disk.percent
        result_type: float
      - type: value
        name: system.cpu.percent
        path: $.details.cpu.percent
        result_type: float
```

### Datadog Dashboard

Create a Datadog dashboard with widgets for Ultra health metrics:

```json
{
  "title": "Ultra Health Dashboard",
  "layout_type": "ordered",
  "widgets": [
    {
      "definition": {
        "title": "System Status",
        "type": "query_value",
        "requests": [
          {
            "q": "avg:system.status{*}",
            "aggregator": "last"
          }
        ]
      }
    },
    {
      "definition": {
        "title": "Memory Usage",
        "type": "timeseries",
        "requests": [
          {
            "q": "avg:system.memory.percent{*}",
            "display_type": "line"
          }
        ],
        "yaxis": {
          "min": "0",
          "max": "100",
          "scale": "linear"
        }
      }
    }
  ]
}
```

## Command Line Monitoring

### Continuous Monitoring Mode

Use the `check_health.py` script in monitor mode for continuous health monitoring from the command line:

```bash
./scripts/check_health.py --monitor --interval 10
```

### Cron Job for Alerting

Create a cron job to check health and send alerts if issues are detected:

```bash
#!/bin/bash
# health_check_alert.sh

# Check health status
HEALTH=$(curl -s http://localhost:8000/health)
STATUS=$(echo $HEALTH | jq -r '.status')

# Send alert if not OK
if [ "$STATUS" != "ok" ]; then
  echo "Ultra health check failed: $STATUS" | mail -s "Ultra Health Alert" ops@example.com
fi
```

Add to crontab:

```
*/5 * * * * /path/to/health_check_alert.sh
```

## StatsD Integration

Send health metrics to StatsD for aggregation:

```python
import statsd
import requests
import time

# Configure StatsD client
statsd_client = statsd.StatsClient('localhost', 8125, prefix='ultra')

while True:
    # Get health status
    try:
        response = requests.get('http://localhost:8000/api/health/system')
        data = response.json()

        # Send metrics to StatsD
        memory_percent = data.get('details', {}).get('memory', {}).get('percent', 0)
        disk_percent = data.get('details', {}).get('disk', {}).get('percent', 0)
        cpu_percent = data.get('details', {}).get('cpu', {}).get('percent', 0)

        statsd_client.gauge('memory.percent', memory_percent)
        statsd_client.gauge('disk.percent', disk_percent)
        statsd_client.gauge('cpu.percent', cpu_percent)

    except Exception as e:
        print(f"Error getting health metrics: {e}")

    # Wait before next check
    time.sleep(60)
```
