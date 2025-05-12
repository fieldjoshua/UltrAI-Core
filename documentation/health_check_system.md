# Health Check System Documentation

Ultra includes a comprehensive health check system that provides detailed information about the status of various components, dependencies, and services. This document explains the health check architecture and how to use the health check endpoints.

## Overview

The health check system monitors the following aspects of the Ultra platform:

- **Core services**: Database, caching, storage, and authentication
- **External dependencies**: LLM providers (OpenAI, Anthropic, Google AI)
- **System resources**: Memory, disk, and CPU usage
- **Network connectivity**: Connection to external APIs
- **Dependencies availability**: Required and optional Python modules

The system provides both simple checks for load balancers and detailed diagnostics for operators and developers.

## Health Check Endpoints

### Basic Health Check

```
GET /health
```

This endpoint returns a minimal health check response, designed for load balancers and monitoring systems. It reports the overall status of critical components and the system uptime.

**Example Response:**
```json
{
  "status": "ok",
  "uptime": 3600
}
```

Possible status values:
- `ok`: All critical systems are functioning normally
- `degraded`: Some non-critical systems are experiencing issues
- `critical`: Critical systems are failing

### API Health Check

```
GET /api/health
```

This endpoint provides a more detailed health check response, including API version, environment, and instance ID.

**Query Parameters:**
- `detail`: Set to `true` to include detailed status of all services
- `service`: Check only a specific service (e.g., `database`, `redis`, `openai`)
- `type`: Filter services by type (e.g., `database`, `cache`, `llm_provider`)
- `include_system`: Set to `true` to include system resource metrics

**Example Response (Basic):**
```json
{
  "status": "ok",
  "api_version": "0.1.0",
  "environment": "development",
  "instance_id": "web-1",
  "uptime": 3600
}
```

**Example Response (With Detail):**
```json
{
  "status": "ok",
  "api_version": "0.1.0",
  "environment": "development",
  "instance_id": "web-1",
  "uptime": 3600,
  "dependencies": {
    "sqlalchemy": {
      "name": "SQLAlchemy",
      "is_available": true,
      "is_required": true,
      "module_name": "sqlalchemy"
    },
    "redis": {
      "name": "Redis",
      "is_available": true,
      "is_required": false,
      "module_name": "redis"
    }
  },
  "features": {
    "database": true,
    "redis_cache": true,
    "jwt_auth": true
  },
  "services": {
    "database": {
      "status": "ok",
      "message": "Database connection successful",
      "details": {
        "connected": true,
        "using_fallback": false,
        "host": "localhost",
        "port": "5432",
        "database": "ultra"
      }
    },
    "redis": {
      "status": "ok",
      "message": "Redis connection successful",
      "details": {
        "enabled": true,
        "type": "RedisCache",
        "redis_available": true
      }
    }
  }
}
```

### System Health Check

```
GET /api/health/system
```

This endpoint provides detailed information about system resources such as memory, disk, and CPU usage.

**Example Response:**
```json
{
  "status": "ok",
  "message": "System resources OK",
  "details": {
    "memory": {
      "total_gb": 16.0,
      "available_gb": 8.5,
      "used_gb": 7.5,
      "percent": 46.9
    },
    "disk": {
      "total_gb": 512.0,
      "free_gb": 256.0,
      "used_gb": 256.0,
      "percent": 50.0
    },
    "cpu": {
      "percent": 25.3,
      "cores": 4,
      "logical_cores": 8
    }
  },
  "timestamp": "2025-05-01T12:00:00Z"
}
```

### Dependencies Status

```
GET /api/health/dependencies
```

This endpoint provides detailed information about Python module dependencies.

**Example Response:**
```json
{
  "dependencies": {
    "sqlalchemy": {
      "name": "SQLAlchemy",
      "is_available": true,
      "is_required": true,
      "module_name": "sqlalchemy"
    },
    "redis": {
      "name": "Redis",
      "is_available": true,
      "is_required": false,
      "module_name": "redis"
    },
    "jwt": {
      "name": "PyJWT",
      "is_available": true,
      "is_required": false,
      "module_name": "jwt"
    }
  },
  "features": {
    "database": true,
    "redis_cache": true,
    "jwt_auth": true
  },
  "all_required_available": true
}
```

### Services Status

```
GET /api/health/services
```

This endpoint provides detailed information about all registered services.

**Query Parameters:**
- `service_type`: Filter services by type (e.g., `database`, `cache`, `llm_provider`)
- `force_check`: Set to `true` to force a fresh health check, bypassing the cache

**Example Response:**
```json
{
  "services": {
    "database": {
      "status": "ok",
      "message": "Database connection successful",
      "details": {
        "connected": true,
        "using_fallback": false
      },
      "timestamp": "2025-05-01T12:00:00Z"
    },
    "redis": {
      "status": "ok",
      "message": "Redis connection successful",
      "details": {
        "enabled": true,
        "type": "RedisCache",
        "redis_available": true
      },
      "timestamp": "2025-05-01T12:00:00Z"
    }
  }
}
```

### LLM Providers Health

```
GET /api/health/llm
```

This endpoint provides detailed information about LLM provider connection status.

**Query Parameters:**
- `provider`: Check only a specific provider (e.g., `openai`, `anthropic`, `google`)
- `force_check`: Set to `true` to force a fresh health check, bypassing the cache

**Example Response:**
```json
{
  "status": "ok",
  "providers": {
    "openai": {
      "status": "ok",
      "message": "OpenAI API connection successful",
      "provider": "openai",
      "dependency_available": true,
      "api_key_configured": true,
      "duration_ms": 355,
      "timestamp": "2025-05-01T12:00:00Z"
    },
    "anthropic": {
      "status": "ok",
      "message": "Anthropic API connection successful",
      "provider": "anthropic",
      "dependency_available": true,
      "api_key_configured": true,
      "duration_ms": 420,
      "timestamp": "2025-05-01T12:00:00Z"
    },
    "google": {
      "status": "unavailable",
      "message": "No API key found for google",
      "provider": "google",
      "api_key_configured": false,
      "timestamp": "2025-05-01T12:00:00Z"
    }
  }
}
```

### Info Endpoint

```
GET /info
```

This endpoint provides basic information about the API, including version, environment, and platform.

**Example Response:**
```json
{
  "api_version": "0.1.0",
  "environment": "development",
  "platform": "Linux-5.10.0-x86_64",
  "python_version": "3.10.5",
  "hostname": "web-1"
}
```

### Ping Endpoint

```
GET /ping
```

This endpoint provides a simple ping/pong response for load balancers and monitoring.

**Example Response:**
```json
{
  "message": "pong"
}
```

## Health Status Values

The health check system uses the following status values:

- **ok**: Service or component is functioning normally
- **degraded**: Service is functioning but with reduced capabilities (e.g., using fallback)
- **critical**: Service has failed and it affects core functionality
- **unavailable**: Service is not available (e.g., API key missing)
- **unknown**: Service status cannot be determined

## Service Types

Services are categorized by type:

- **database**: Database connections
- **cache**: Caching services
- **auth**: Authentication services
- **llm_provider**: LLM API providers
- **storage**: File storage services
- **network**: Network connectivity
- **system**: System resources
- **external_api**: Other external APIs
- **custom**: Custom services

## Architecture

The health check system is built around a registry of health check functions. Each service registers a health check function that returns detailed status information.

The health check system includes:

1. **Health Check Registry**: Central registry of all health checks
2. **Health Check Functions**: Functions that check specific services
3. **Caching Layer**: Cache health check results to avoid repeated checks
4. **API Endpoints**: Expose health check results via HTTP

## Monitoring Integration

The health check endpoints are designed to integrate with monitoring systems:

### Prometheus Integration

For Prometheus monitoring, you can use the `/api/health` endpoint with a scraper that extracts metrics from the JSON response. Example Prometheus configuration:

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

### Kubernetes Liveness and Readiness Probes

For Kubernetes, you can use the health check endpoints as liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Best Practices

1. **Use `/health` for load balancers**: The basic endpoint is fast and lightweight
2. **Use `/api/health` for detailed status**: When you need more information
3. **Use service-specific endpoints for diagnostics**: When troubleshooting specific issues
4. **Set appropriate caching**: Health checks are cached to reduce load, use `force_check=true` when you need fresh data
5. **Monitor trends**: Track degraded services over time to identify patterns

## Troubleshooting

### Common Issues

1. **Database Status "degraded"**: Check database connection parameters and network connectivity
2. **Redis Status "degraded"**: Check Redis server availability and connection parameters
3. **LLM Provider Status "unavailable"**: Check API keys and network connectivity
4. **System Status "critical"**: Check system resources, you may need to scale up

### Debugging

For detailed debugging, use the service-specific endpoints with `force_check=true` to get fresh data:

```
GET /api/health/services?service_type=database&force_check=true
```

## Extending the Health Check System

You can add custom health checks for your own services by registering them with the health check registry:

```python
from backend.utils.health_check import health_check_registry, HealthCheck, ServiceType

def check_my_service():
    # Your health check logic here
    return {
        "status": "ok",
        "message": "My service is working",
        "details": {...},
        "timestamp": datetime.utcnow().isoformat(),
    }

health_check_registry.register(HealthCheck(
    name="my_service",
    service_type=ServiceType.CUSTOM,
    check_fn=check_my_service,
    description="My custom service",
    is_critical=False,
))
```

## Health Check Environment Variables

The health check system can be configured using the following environment variables:

- `HEALTH_CHECK_CACHE_TTL`: Cache time-to-live in seconds (default: 60)
- `HEALTH_CHECK_TIMEOUT`: Timeout for health checks in seconds (default: 5)
- `HEALTH_CHECK_DISABLE_CACHE`: Set to "true" to disable caching (default: false)