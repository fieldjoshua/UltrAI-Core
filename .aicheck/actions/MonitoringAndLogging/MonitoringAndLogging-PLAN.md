# MonitoringAndLogging Action Plan (11 of 16)

## Overview

**Status:** Planning  
**Created:** 2025-05-11  
**Last Updated:** 2025-05-11  
**Expected Completion:** 2025-05-30  

## Objective

Implement comprehensive monitoring and logging systems for the Ultra MVP to enable effective troubleshooting, performance tracking, and system health visibility in production.

## Value to Program

This action directly addresses operational requirements for the MVP by:

1. Providing visibility into system health and performance
2. Enabling quick identification and troubleshooting of issues
3. Creating structured logs for effective debugging
4. Establishing performance baselines and alerting thresholds
5. Supporting resource utilization tracking

## Success Criteria

- [ ] Implement structured logging across all components
- [ ] Create a centralized log storage and search solution
- [ ] Develop performance metrics collection for key components
- [ ] Implement health check endpoints with appropriate detail
- [ ] Create basic alerting for critical errors and performance issues
- [ ] Add resource usage monitoring (CPU, memory, network)
- [ ] Document monitoring and logging architecture

## Implementation Plan

### Phase 1: Logging Infrastructure (Days 1-3)

1. Design and implement structured logging:
   - Standardized log format
   - Log levels and categories
   - Context enrichment (request ID, user ID, etc.)
   - PII/sensitive data filtering

2. Create centralized log collection:
   - Log aggregation configuration
   - Log storage and retention policy
   - Log search and analysis capabilities

3. Implement application-specific logging:
   - Request/response logging
   - Error logging with context
   - Performance timing logs
   - Audit logging for security events

### Phase 2: Health Monitoring (Days 4-6)

1. Create health check endpoints:
   - Overall system health
   - Component-specific health
   - Dependency health (database, cache, etc.)
   - LLM provider status

2. Implement health probes:
   - Kubernetes/Docker health checks
   - Deep health checks
   - Dependency health verification

3. Develop health status dashboard:
   - Component status overview
   - Historical uptime
   - Dependency status

### Phase 3: Performance Monitoring (Days 7-9)

1. Implement performance metrics collection:
   - Response time metrics
   - Throughput metrics
   - Error rate metrics
   - Resource usage metrics

2. Create performance dashboards:
   - System performance overview
   - Component-specific performance
   - LLM provider performance
   - User experience metrics

3. Set up basic alerting:
   - Critical error alerts
   - Performance degradation alerts
   - Resource constraint alerts
   - Availability alerts

## Dependencies

- MVP Security Implementation (for secure logging)
- Error Handling Implementation (for error logging)
- System Resilience Implementation (for health monitoring)
- MVP Deployment Pipeline (for deployment metrics)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Excessive logging affecting performance | Medium | Medium | Sampling, log level tuning, async logging |
| Missing critical logs during incidents | High | Medium | Log level verification, critical path audit |
| Alert fatigue from noisy alerts | Medium | High | Careful threshold tuning, alert grouping |
| Storage costs for extensive logging | Medium | Medium | Log retention policies, sampling strategies |

## Technical Specifications

### Structured Logging

```python
import logging
import json
import uuid
import time
from contextvars import ContextVar
from datetime import datetime
from typing import Dict, Any, Optional

# Context variables for request tracking
request_id_var = ContextVar("request_id", default=None)
user_id_var = ContextVar("user_id", default=None)

class StructuredLogFormatter(logging.Formatter):
    """Formatter for structured JSON logs."""
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add context from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        elif request_id_var.get() is not None:
            log_data["request_id"] = request_id_var.get()
            
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        elif user_id_var.get() is not None:
            log_data["user_id"] = user_id_var.get()
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields from record
        if hasattr(record, "extra"):
            for key, value in record.extra.items():
                if key not in log_data:
                    log_data[key] = value
                    
        return json.dumps(log_data)

class LoggingMiddleware:
    """Middleware for request logging and context tracking."""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("api.request")
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Generate request ID if not provided
        request_id = None
        headers = dict(scope.get("headers", []))
        if b"x-request-id" in headers:
            request_id = headers[b"x-request-id"].decode("utf-8")
        else:
            request_id = str(uuid.uuid4())
            
        # Store request ID in context
        request_id_var.set(request_id)
        
        # Track timing
        start_time = time.time()
        
        # Process request and capture response
        response_started = False
        status_code = None
        
        async def wrapped_send(message):
            nonlocal response_started, status_code
            
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                
                # Add request ID to response headers
                headers = message.get("headers", [])
                headers.append((b"X-Request-ID", request_id.encode("utf-8")))
                message["headers"] = headers
                
            await send(message)
            
        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as e:
            self.logger.exception(
                f"Unhandled exception during request: {str(e)}",
                extra={
                    "request_id": request_id,
                    "path": scope.get("path", ""),
                    "method": scope.get("method", ""),
                    "exception": str(e)
                }
            )
            raise
        finally:
            # Calculate request duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log request completion
            self.logger.info(
                f"{scope.get('method', 'UNKNOWN')} {scope.get('path', '')} completed in {duration_ms}ms with status {status_code}",
                extra={
                    "request_id": request_id,
                    "path": scope.get("path", ""),
                    "method": scope.get("method", ""),
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "client_ip": scope.get("client", ("unknown", 0))[0]
                }
            )

def configure_logging(level=logging.INFO, enable_json=True):
    """Configure application-wide logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # Create console handler
    console_handler = logging.StreamHandler()
    
    if enable_json:
        console_handler.setFormatter(StructuredLogFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
            )
        )
        
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

### Health Checking

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import time

router = APIRouter()

class ServiceHealth(BaseModel):
    """Health status of a service."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    details: Optional[Dict] = None
    last_checked: str

class SystemHealth(BaseModel):
    """Overall system health."""
    status: str  # "healthy", "degraded", "unhealthy"
    services: List[ServiceHealth]
    uptime_seconds: int
    version: str

class LLMProviderHealth(BaseModel):
    """Health status of an LLM provider."""
    name: str
    status: str  # "available", "limited", "unavailable"
    latency_ms: Optional[float] = None
    quota_remaining: Optional[float] = None
    details: Optional[Dict] = None

class LLMProvidersHealth(BaseModel):
    """Health status of all LLM providers."""
    status: str  # "healthy", "degraded", "unhealthy"
    providers: List[LLMProviderHealth]

# Health check dependencies
async def check_database():
    """Check database health."""
    try:
        # Perform database ping
        start_time = time.time()
        await database.ping()
        latency_ms = (time.time() - start_time) * 1000
        
        return ServiceHealth(
            name="database",
            status="healthy",
            details={"latency_ms": latency_ms},
            last_checked=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ServiceHealth(
            name="database",
            status="unhealthy",
            details={"error": str(e)},
            last_checked=datetime.utcnow().isoformat()
        )

async def check_redis():
    """Check Redis health."""
    try:
        # Perform Redis ping
        start_time = time.time()
        await redis.ping()
        latency_ms = (time.time() - start_time) * 1000
        
        return ServiceHealth(
            name="redis",
            status="healthy",
            details={"latency_ms": latency_ms},
            last_checked=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ServiceHealth(
            name="redis",
            status="unhealthy",
            details={"error": str(e)},
            last_checked=datetime.utcnow().isoformat()
        )

async def check_llm_providers():
    """Check LLM provider health."""
    providers = []
    
    for provider_name, provider in llm_providers.items():
        try:
            # Check provider health
            start_time = time.time()
            status = await provider.check_health()
            latency_ms = (time.time() - start_time) * 1000
            
            providers.append(LLMProviderHealth(
                name=provider_name,
                status="available" if status["available"] else "unavailable",
                latency_ms=latency_ms,
                quota_remaining=status.get("quota_remaining"),
                details=status.get("details")
            ))
        except Exception as e:
            providers.append(LLMProviderHealth(
                name=provider_name,
                status="unavailable",
                details={"error": str(e)}
            ))
    
    # Overall status is healthy if at least one provider is available
    overall_status = "healthy"
    if not any(p.status == "available" for p in providers):
        overall_status = "unhealthy"
    elif sum(1 for p in providers if p.status == "available") < len(providers):
        overall_status = "degraded"
        
    return LLMProvidersHealth(
        status=overall_status,
        providers=providers
    )

# Health check endpoints
@router.get("/health", response_model=SystemHealth)
async def health_check(
    db: ServiceHealth = Depends(check_database),
    redis: ServiceHealth = Depends(check_redis)
):
    """Get overall system health."""
    services = [db, redis]
    
    # System is healthy if all services are healthy
    if all(service.status == "healthy" for service in services):
        status = "healthy"
    elif any(service.status == "unhealthy" for service in services):
        status = "unhealthy"
    else:
        status = "degraded"
        
    return SystemHealth(
        status=status,
        services=services,
        uptime_seconds=int(time.time() - app_start_time),
        version=app_version
    )

@router.get("/health/database")
async def database_health():
    """Get database health."""
    return await check_database()

@router.get("/health/redis")
async def redis_health():
    """Get Redis health."""
    return await check_redis()

@router.get("/health/llm-providers", response_model=LLMProvidersHealth)
async def llm_providers_health():
    """Get LLM provider health."""
    return await check_llm_providers()
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import APIRouter, Response

router = APIRouter()

# Define metrics
REQUEST_COUNT = Counter(
    "ultra_request_total",
    "Total request count",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "ultra_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

ACTIVE_REQUESTS = Gauge(
    "ultra_active_requests",
    "Number of active requests"
)

LLM_REQUEST_COUNT = Counter(
    "ultra_llm_request_total",
    "Total LLM request count",
    ["provider", "model", "status"]
)

LLM_REQUEST_LATENCY = Histogram(
    "ultra_llm_request_latency_seconds",
    "LLM request latency in seconds",
    ["provider", "model"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

LLM_TOKEN_COUNT = Counter(
    "ultra_llm_token_total",
    "Total LLM token count",
    ["provider", "model", "direction"]  # direction: "input" or "output"
)

CACHE_HIT_COUNT = Counter(
    "ultra_cache_hit_total",
    "Total cache hit count",
    ["cache_type"]  # "memory", "redis", etc.
)

CACHE_MISS_COUNT = Counter(
    "ultra_cache_miss_total",
    "Total cache miss count",
    ["cache_type"]  # "memory", "redis", etc.
)

class MetricsMiddleware:
    """Middleware for collecting request metrics."""
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        path = scope["path"]
        method = scope["method"]
        
        # Skip metrics endpoint to avoid recursion
        if path == "/metrics":
            return await self.app(scope, receive, send)
            
        # Track request count and latency
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        # Process request and capture status code
        status_code = 500  # Default to error status
        
        async def wrapped_send(message):
            nonlocal status_code
            
            if message["type"] == "http.response.start":
                status_code = message["status"]
                
            await send(message)
            
        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            # Update metrics
            duration = time.time() - start_time
            ACTIVE_REQUESTS.dec()
            
            # Use normalized path to avoid cardinality explosion
            normalized_path = normalize_path(path)
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=normalized_path,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)

def normalize_path(path):
    """Normalize path to prevent cardinality explosion."""
    # Replace numeric IDs with placeholders
    # /users/123/profile -> /users/{id}/profile
    parts = path.split('/')
    normalized_parts = []
    
    for part in parts:
        if part.isdigit():
            normalized_parts.append('{id}')
        else:
            normalized_parts.append(part)
            
    return '/'.join(normalized_parts)

@router.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Alerting Configuration

```yaml
# alerting-rules.yml
groups:
  - name: ultra-alerts
    rules:
      # Error rate alerts
      - alert: HighErrorRate
        expr: sum(rate(ultra_request_total{status_code=~"5.."}[5m])) / sum(rate(ultra_request_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: Error rate is above 5% for the past 5 minutes
          
      # Latency alerts
      - alert: HighLatency
        expr: histogram_quantile(0.95, sum(rate(ultra_request_latency_seconds_bucket[5m])) by (le)) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: 95th percentile latency is above 2 seconds for the past 5 minutes
          
      # LLM provider alerts
      - alert: LLMProviderUnavailable
        expr: sum(ultra_llm_provider_available) by (provider) == 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: LLM provider unavailable
          description: LLM provider {{ $labels.provider }} is unavailable for the past 10 minutes
          
      # Resource usage alerts
      - alert: HighCPUUsage
        expr: sum(rate(process_cpu_seconds_total[5m])) by (instance) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage
          description: CPU usage is above 80% for the past 5 minutes on {{ $labels.instance }}
          
      - alert: HighMemoryUsage
        expr: sum(process_resident_memory_bytes) by (instance) / node_memory_MemTotal_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High memory usage
          description: Memory usage is above 80% for the past 5 minutes on {{ $labels.instance }}
```

## Implementation Details

### Log Management Configuration

We'll implement log management using a combination of:

1. **Application Logging**:
   - Structured JSON logging
   - Consistent log format across components
   - Log level configuration for different environments

2. **Log Shipping**:
   - Docker logging driver configuration
   - Log aggregation service integration
   - Secure log transmission

3. **Log Retention and Search**:
   - Log retention policies by log type
   - Full-text search capability
   - Log filtering and visualization

### Dashboard Configuration

We'll create the following dashboards:

1. **System Overview Dashboard**:
   - System health status
   - Key performance metrics
   - Error rates
   - Resource usage

2. **API Performance Dashboard**:
   - Request volume
   - Response times
   - Error rates by endpoint
   - Cache performance

3. **LLM Performance Dashboard**:
   - Provider availability
   - Response times by model
   - Token usage
   - Error rates by provider

4. **User Experience Dashboard**:
   - End-to-end request times
   - UI performance metrics
   - User error rates
   - Session metrics

## Documentation Plan

The following documentation will be created:
- Monitoring and logging architecture overview
- Log format and retention policy documentation
- Metrics collection documentation
- Dashboard and alerting documentation
- Troubleshooting guide using logs and metrics