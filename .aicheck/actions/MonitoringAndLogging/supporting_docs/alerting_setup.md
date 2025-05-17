# Alerting Setup

## Overview

This document outlines the alerting configuration for the Ultra application monitoring system.

## Alert Categories

### Critical Alerts (P1)

- Service down
- Database connection lost
- All LLM providers unavailable
- Authentication service failure
- Data corruption detected

### High Priority (P2)

- Error rate > 5%
- Response time > 5s (p95)
- Memory usage > 90%
- Disk space < 10%
- Failed deployments

### Medium Priority (P3)

- Error rate > 1%
- Response time > 2s (p95)
- Cache hit rate < 50%
- Queue depth high
- Certificate expiry warning

### Low Priority (P4)

- Deprecated API usage
- Configuration drift
- Performance degradation trend
- Unusual usage patterns
- Maintenance windows

## Alert Configuration

### Prometheus Alert Rules

```yaml
groups:
  - name: critical_alerts
    interval: 30s
    rules:
      - alert: ServiceDown
        expr: up{job="ultra-api"} == 0
        for: 1m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: 'Ultra API service is down'
          description: 'The Ultra API service has been down for more than 1 minute'
          runbook: 'https://docs.ultra.ai/runbooks/service-down'

      - alert: DatabaseConnectionLost
        expr: mysql_up == 0 or pg_up == 0
        for: 30s
        labels:
          severity: critical
          team: platform
        annotations:
          summary: 'Database connection lost'
          description: 'Cannot connect to database {{ $labels.instance }}'
          runbook: 'https://docs.ultra.ai/runbooks/database-connection'
```

### High Priority Alerts

```yaml
groups:
  - name: high_priority_alerts
    interval: 1m
    rules:
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) > 0.05
        for: 5m
        labels:
          severity: high
          team: platform
        annotations:
          summary: 'High error rate detected'
          description: 'Error rate is {{ $value | humanizePercentage }}'
          dashboard: 'https://grafana.ultra.ai/d/api-errors'

      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 5
        for: 5m
        labels:
          severity: high
          team: platform
        annotations:
          summary: 'High response time'
          description: '95th percentile response time is {{ $value }}s'
```

## Notification Channels

### Slack Configuration

```yaml
receivers:
  - name: 'slack-critical'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-critical'
        title: 'Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
        send_resolved: true
        color: 'danger'

  - name: 'slack-warning'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts-warning'
        title: 'Warning Alert'
        text: '{{ .CommonAnnotations.summary }}'
        send_resolved: true
        color: 'warning'
```

### PagerDuty Integration

```yaml
receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
        client: 'Prometheus'
        client_url: 'https://prometheus.ultra.ai'
        description: '{{ .CommonAnnotations.summary }}'
        details:
          firing: '{{ .GroupLabels.alertname }}'
          num_firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
```

### Email Configuration

```yaml
receivers:
  - name: 'email-team'
    email_configs:
      - to: 'platform-team@ultra.ai'
        from: 'alerts@ultra.ai'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@ultra.ai'
        auth_password: 'YOUR_EMAIL_PASSWORD'
        headers:
          Subject: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
        html: |
          <h2>{{ .CommonAnnotations.summary }}</h2>
          <p>{{ .CommonAnnotations.description }}</p>
          <p><a href="{{ .CommonAnnotations.runbook }}">Runbook</a></p>
```

## Routing Rules

```yaml
route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'default'

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true

    - match:
        severity: critical
      receiver: 'slack-critical'

    - match:
        severity: high
      receiver: 'slack-warning'

    - match:
        severity: medium
      receiver: 'email-team'

    - match:
        alertname: DeploymentFailed
      receiver: 'deployment-channel'
```

## Alert Suppression

### Maintenance Windows

```yaml
inhibit_rules:
  - source_match:
      alertname: 'MaintenanceMode'
    target_match_re:
      severity: 'warning|medium|low'
    equal: ['environment']

  - source_match:
      alertname: 'ServiceDown'
    target_match:
      alertname: 'HighErrorRate'
    equal: ['service']
```

### Alert Grouping

```yaml
route:
  group_by: ['alertname', 'service', 'environment']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
```

## On-Call Policies

### Escalation Policy

```json
{
  "name": "Platform Team Escalation",
  "escalation_rules": [
    {
      "escalation_delay_in_minutes": 0,
      "targets": [
        {
          "type": "user",
          "id": "primary_oncall_user_id"
        }
      ]
    },
    {
      "escalation_delay_in_minutes": 15,
      "targets": [
        {
          "type": "user",
          "id": "secondary_oncall_user_id"
        }
      ]
    },
    {
      "escalation_delay_in_minutes": 30,
      "targets": [
        {
          "type": "user",
          "id": "team_lead_user_id"
        }
      ]
    }
  ]
}
```

### On-Call Schedule

```json
{
  "name": "Platform Team Rotation",
  "time_zone": "America/New_York",
  "rotation_virtual_start": "2025-01-01T09:00:00",
  "rotation_turn_length_seconds": 604800,
  "users": [
    { "user": { "id": "user1" }, "position": 0 },
    { "user": { "id": "user2" }, "position": 1 },
    { "user": { "id": "user3" }, "position": 2 }
  ]
}
```

## Alert Testing

### Test Alert Command

```bash
# Test critical alert
amtool alert add \
  alertname="TestCriticalAlert" \
  severity="critical" \
  instance="test-instance" \
  --annotation=summary="This is a test critical alert"

# Test specific receiver
amtool config routes test \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --tree \
  --verify.receivers=slack-critical \
  severity=critical alertname=ServiceDown
```

### Silence Management

```bash
# Create silence
amtool silence add \
  alertname="HighCPU" \
  instance="server1" \
  --duration="2h" \
  --comment="Planned maintenance"

# List active silences
amtool silence query

# Expire silence
amtool silence expire SILENCE_ID
```

## Alert Documentation

### Runbook Template

```markdown
# Alert: ServiceDown

## Description

The Ultra API service is not responding to health checks.

## Impact

- Users cannot access the application
- API requests will fail
- Background jobs may be affected

## Detection

- Prometheus up metric == 0
- Health check endpoint returns non-200

## Response

1. Check service status: `systemctl status ultra-api`
2. Check logs: `tail -f /var/log/ultra/api.log`
3. Restart if needed: `systemctl restart ultra-api`
4. Check for deployment issues
5. Escalate if not resolved in 15 minutes

## Prevention

- Ensure proper health checks
- Monitor deployment success
- Test in staging first
```

## Best Practices

1. **Keep alerts actionable**
2. **Avoid alert fatigue**
3. **Document all alerts**
4. **Test alert paths regularly**
5. **Review and tune thresholds**
6. **Maintain runbooks**
7. **Practice incident response**
8. **Track alert metrics**
