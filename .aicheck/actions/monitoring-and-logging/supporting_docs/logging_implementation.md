# Logging Implementation

## Overview

This document outlines the logging implementation for the Ultra application.

## Log Structure

### Standard Log Format

```json
{
  "timestamp": "2025-05-15T10:30:00.123Z",
  "level": "INFO",
  "service": "api",
  "environment": "production",
  "request_id": "req_abc123",
  "user_id": "user_456",
  "session_id": "sess_789",
  "action": "analyze_document",
  "duration_ms": 234,
  "status": "success",
  "metadata": {
    "model": "gpt-4",
    "document_id": "doc_xyz",
    "tokens_used": 1500
  },
  "context": {
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "api_version": "v1"
  }
}
```

## Log Levels

### Level Definitions

- **TRACE**: Detailed debugging information
- **DEBUG**: Debugging information for development
- **INFO**: General operational information
- **WARN**: Warning conditions that aren't errors
- **ERROR**: Error conditions that need attention
- **FATAL**: Critical errors requiring immediate action

### Usage Guidelines

```python
# TRACE - Detailed execution flow
logger.trace(f"Entering function with params: {params}")

# DEBUG - Development debugging
logger.debug(f"Cache hit for key: {key}")

# INFO - Normal operations
logger.info(f"Analysis completed for document {doc_id}")

# WARN - Recoverable issues
logger.warning(f"Rate limit approaching: {current}/{limit}")

# ERROR - Failures requiring investigation
logger.error(f"Failed to process document: {error}")

# FATAL - System-critical failures
logger.fatal(f"Database connection lost: {error}")
```

## Implementation

### Python Logger Setup

```python
import logging
import json
from pythonjsonlogger import jsonlogger

def setup_logger(service_name):
    logger = logging.getLogger(service_name)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(service)s %(message)s',
        rename_fields={
            'levelname': 'level',
            'asctime': 'timestamp'
        }
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    return logger
```

### Node.js Logger Setup

```javascript
const winston = require('winston');
const { format } = winston;

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  defaultMeta: {
    service: 'api',
    environment: process.env.NODE_ENV,
  },
  transports: [
    new winston.transports.Console({
      format: format.combine(format.colorize(), format.simple()),
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
    }),
  ],
});
```

## Context Management

### Request Context

```python
class RequestContext:
    def __init__(self, request_id):
        self.request_id = request_id
        self.user_id = None
        self.session_id = None
        self.start_time = time.time()

    def set_user(self, user_id):
        self.user_id = user_id

    def get_log_context(self):
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'duration_ms': int((time.time() - self.start_time) * 1000)
        }
```

### Context Middleware

```python
@app.middleware("http")
async def add_logging_context(request: Request, call_next):
    request_id = str(uuid.uuid4())

    with logger.contextualize(request_id=request_id):
        logger.info(f"Request started: {request.method} {request.url}")

        response = await call_next(request)

        logger.info(f"Request completed: {response.status_code}")

        return response
```

## Sensitive Data Handling

### PII Masking

```python
def mask_sensitive_data(log_dict):
    sensitive_fields = [
        'password', 'token', 'api_key',
        'credit_card', 'ssn', 'email'
    ]

    for field in sensitive_fields:
        if field in log_dict:
            log_dict[field] = '***MASKED***'

        # Check nested fields
        for key, value in log_dict.items():
            if isinstance(value, dict):
                mask_sensitive_data(value)

    return log_dict
```

### Email Anonymization

```python
def anonymize_email(email):
    parts = email.split('@')
    if len(parts) == 2:
        username = parts[0]
        domain = parts[1]
        masked = username[:2] + '*' * (len(username) - 2) + '@' + domain
        return masked
    return '***INVALID_EMAIL***'
```

## Performance Logging

### Request Duration

```python
class PerformanceLogger:
    def log_request(self, method, endpoint, duration_ms, status):
        logger.info(
            "Request completed",
            extra={
                'method': method,
                'endpoint': endpoint,
                'duration_ms': duration_ms,
                'status': status,
                'performance': {
                    'category': self._categorize_duration(duration_ms)
                }
            }
        )

    def _categorize_duration(self, duration_ms):
        if duration_ms < 100:
            return 'fast'
        elif duration_ms < 500:
            return 'normal'
        elif duration_ms < 2000:
            return 'slow'
        else:
            return 'very_slow'
```

## Log Aggregation

### Elasticsearch Configuration

```yaml
output.elasticsearch:
  hosts: ['localhost:9200']
  index: 'logs-%{+yyyy.MM.dd}'
  template:
    name: 'logs'
    pattern: 'logs-*'
    settings:
      index.number_of_shards: 1
      index.number_of_replicas: 1
```

### Logstash Pipeline

```ruby
input {
  file {
    path => "/var/log/ultra/*.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [level] == "ERROR" {
    mutate {
      add_tag => ["alert"]
    }
  }

  date {
    match => ["timestamp", "ISO8601"]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

## Retention Policies

### Log Rotation

```python
{
    'production': {
        'max_size': '100MB',
        'max_files': 10,
        'compress': True
    },
    'development': {
        'max_size': '10MB',
        'max_files': 5,
        'compress': False
    }
}
```

### Archive Strategy

- Keep 7 days of logs locally
- Archive to S3 for 90 days
- Delete after 90 days
- Keep error logs for 1 year

## Best Practices

1. **Always use structured logging**
2. **Include correlation IDs**
3. **Log at appropriate levels**
4. **Never log sensitive data**
5. **Include relevant context**
6. **Use consistent field names**
7. **Monitor log volume**
8. **Test log queries**
