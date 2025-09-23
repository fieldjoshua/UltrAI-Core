"""
OpenTelemetry instrumentation and custom metrics for UltrAI-Core.

This module provides:
- Distributed tracing with OpenTelemetry
- Custom metrics for stage durations, tokens, and costs
- Integration with correlation IDs from SSE spec
- Export to various backends (Jaeger, Prometheus, etc.)
"""

import os
import time
from typing import Any, Dict, Optional
from contextlib import contextmanager
from functools import wraps
import asyncio

# OpenTelemetry imports
try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.trace import Status, StatusCode
    
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    trace = None
    metrics = None

# Prometheus metrics (fallback/additional)
try:
    from prometheus_client import Counter as PrometheusCounter
    from prometheus_client import Histogram as PrometheusHistogram
    from prometheus_client import Gauge as PrometheusGauge
    from prometheus_client import Info as PrometheusInfo
    
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from app.utils.logging import get_logger, CorrelationContext

logger = get_logger(__name__)


# Service info for resource
SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "ultrai-core")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# OpenTelemetry configuration
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "true").lower() == "true"
OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
OTEL_HEADERS = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")


class TelemetryService:
    """Service for managing traces and metrics."""
    
    def __init__(self):
        self.initialized = False
        self.tracer = None
        self.meter = None
        
        # Metric instruments
        self.request_counter = None
        self.request_duration_histogram = None
        self.llm_request_counter = None
        self.llm_duration_histogram = None
        self.token_counter = None
        self.cost_counter = None
        self.stage_duration_histogram = None
        self.error_counter = None
        self.circuit_breaker_state_gauge = None
        
        # Prometheus metrics (if available)
        self.prometheus_metrics = {}
        
        if OTEL_ENABLED and TELEMETRY_AVAILABLE:
            self._initialize_opentelemetry()
        elif PROMETHEUS_AVAILABLE:
            self._initialize_prometheus()
    
    def _initialize_opentelemetry(self):
        """Initialize OpenTelemetry with OTLP exporters."""
        try:
            # Create resource
            resource = Resource.create({
                "service.name": SERVICE_NAME,
                "service.version": SERVICE_VERSION,
                "deployment.environment": ENVIRONMENT,
            })
            
            # Set up tracing
            tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(tracer_provider)
            
            # Configure OTLP exporter for traces
            otlp_exporter = OTLPSpanExporter(
                endpoint=OTEL_ENDPOINT,
                headers=self._parse_headers(OTEL_HEADERS),
                insecure=True  # For development; use secure in production
            )
            
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            self.tracer = trace.get_tracer(__name__, SERVICE_VERSION)
            
            # Set up metrics
            metric_reader = PeriodicExportingMetricReader(
                exporter=OTLPMetricExporter(
                    endpoint=OTEL_ENDPOINT,
                    headers=self._parse_headers(OTEL_HEADERS),
                    insecure=True
                ),
                export_interval_millis=10000  # Export every 10 seconds
            )
            
            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader]
            )
            metrics.set_meter_provider(meter_provider)
            
            self.meter = metrics.get_meter(__name__, SERVICE_VERSION)
            
            # Create metric instruments
            self._create_metric_instruments()
            
            # Auto-instrument libraries
            self._auto_instrument()
            
            self.initialized = True
            logger.info(f"OpenTelemetry initialized with endpoint: {OTEL_ENDPOINT}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
            self.initialized = False
    
    def _initialize_prometheus(self):
        """Initialize Prometheus metrics as fallback."""
        try:
            # Request metrics
            self.prometheus_metrics["request_total"] = PrometheusCounter(
                "ultrai_request_total",
                "Total number of requests",
                ["method", "endpoint", "status"]
            )
            
            self.prometheus_metrics["request_duration"] = PrometheusHistogram(
                "ultrai_request_duration_seconds",
                "Request duration in seconds",
                ["method", "endpoint"]
            )
            
            # LLM metrics
            self.prometheus_metrics["llm_request_total"] = PrometheusCounter(
                "ultrai_llm_request_total",
                "Total LLM requests",
                ["provider", "model", "status"]
            )
            
            self.prometheus_metrics["llm_duration"] = PrometheusHistogram(
                "ultrai_llm_duration_seconds",
                "LLM request duration",
                ["provider", "model"]
            )
            
            self.prometheus_metrics["tokens_total"] = PrometheusCounter(
                "ultrai_tokens_total",
                "Total tokens used",
                ["provider", "model", "type"]  # label indicates input or output
            )
            
            self.prometheus_metrics["cost_total"] = PrometheusCounter(
                "ultrai_cost_dollars_total",
                "Total cost in dollars",
                ["provider", "model"]
            )
            
            # Stage metrics
            self.prometheus_metrics["stage_duration"] = PrometheusHistogram(
                "ultrai_stage_duration_seconds",
                "Pipeline stage duration",
                ["stage"]
            )
            
            # Error metrics
            self.prometheus_metrics["error_total"] = PrometheusCounter(
                "ultrai_error_total",
                "Total errors",
                ["type", "provider", "stage"]
            )
            
            # Circuit breaker metrics
            self.prometheus_metrics["circuit_breaker_state"] = PrometheusGauge(
                "ultrai_circuit_breaker_state",
                "Circuit breaker state (0=closed, 1=open, 2=half-open)",
                ["provider"]
            )
            
            # System info
            self.prometheus_metrics["info"] = PrometheusInfo(
                "ultrai_build_info",
                "Build information"
            )
            self.prometheus_metrics["info"].info({
                "version": SERVICE_VERSION,
                "environment": ENVIRONMENT,
            })
            
            logger.info("Prometheus metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus metrics: {e}")
    
    def _parse_headers(self, headers_str: str) -> Dict[str, str]:
        """Parse OTLP headers from environment variable."""
        headers = {}
        if headers_str:
            for header in headers_str.split(","):
                if "=" in header:
                    key, value = header.split("=", 1)
                    headers[key.strip()] = value.strip()
        return headers
    
    def _create_metric_instruments(self):
        """Create OpenTelemetry metric instruments."""
        # Request metrics
        self.request_counter = self.meter.create_counter(
            "ultrai.request.count",
            description="Total number of requests",
            unit="1"
        )
        
        self.request_duration_histogram = self.meter.create_histogram(
            "ultrai.request.duration",
            description="Request duration",
            unit="ms"
        )
        
        # LLM metrics
        self.llm_request_counter = self.meter.create_counter(
            "ultrai.llm.request.count",
            description="Total LLM requests",
            unit="1"
        )
        
        self.llm_duration_histogram = self.meter.create_histogram(
            "ultrai.llm.duration",
            description="LLM request duration",
            unit="ms"
        )
        
        self.token_counter = self.meter.create_counter(
            "ultrai.tokens.count",
            description="Total tokens used",
            unit="1"
        )
        
        self.cost_counter = self.meter.create_counter(
            "ultrai.cost.total",
            description="Total cost",
            unit="USD"
        )
        
        # Stage metrics
        self.stage_duration_histogram = self.meter.create_histogram(
            "ultrai.stage.duration",
            description="Pipeline stage duration",
            unit="ms"
        )
        
        # Error metrics
        self.error_counter = self.meter.create_counter(
            "ultrai.error.count",
            description="Total errors",
            unit="1"
        )
        
        # Circuit breaker gauge
        self.circuit_breaker_state_gauge = self.meter.create_up_down_counter(
            "ultrai.circuit_breaker.state",
            description="Circuit breaker state changes",
            unit="1"
        )
    
    def _auto_instrument(self):
        """Auto-instrument libraries."""
        try:
            # Instrument FastAPI
            FastAPIInstrumentor.instrument(
                tracer_provider=trace.get_tracer_provider(),
                meter_provider=metrics.get_meter_provider()
            )
            
            # Instrument HTTPX (for LLM calls)
            HTTPXClientInstrumentor().instrument()
            
            # Instrument SQLAlchemy if available
            try:
                from app.database.connection import engine
                SQLAlchemyInstrumentor().instrument(
                    engine=engine,
                    service="ultrai-db"
                )
            except Exception:
                pass
            
            logger.info("Auto-instrumentation completed")
            
        except Exception as e:
            logger.error(f"Auto-instrumentation failed: {e}")
    
    @contextmanager
    def trace_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Create a trace span context manager."""
        if not self.initialized or not self.tracer:
            yield None
            return
        
        # Add correlation ID to attributes
        if attributes is None:
            attributes = {}
        
        request_id = CorrelationContext.get_correlation_id()
        if request_id:
            attributes["request.id"] = request_id
        
        with self.tracer.start_as_current_span(name, attributes=attributes) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def trace_function(self, name: Optional[str] = None):
        """Decorator to trace function execution."""
        def decorator(func):
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.trace_span(span_name):
                    return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.trace_span(span_name):
                    return func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration_ms: float):
        """Record HTTP request metrics."""
        labels = {
            "method": method,
            "endpoint": endpoint,
            "status": str(status_code),
            "status_class": f"{status_code // 100}xx"
        }
        
        if self.request_counter:
            self.request_counter.add(1, labels)
        
        if self.request_duration_histogram:
            self.request_duration_histogram.record(duration_ms, labels)
        
        if PROMETHEUS_AVAILABLE and "request_total" in self.prometheus_metrics:
            self.prometheus_metrics["request_total"].labels(
                method=method, endpoint=endpoint, status=str(status_code)
            ).inc()
            self.prometheus_metrics["request_duration"].labels(
                method=method, endpoint=endpoint
            ).observe(duration_ms / 1000.0)  # Convert to seconds
    
    def record_llm_request(
        self, 
        provider: str, 
        model: str, 
        duration_ms: float, 
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0
    ):
        """Record LLM request metrics."""
        labels = {
            "provider": provider,
            "model": model,
            "status": "success" if success else "failure"
        }
        
        # OpenTelemetry metrics
        if self.llm_request_counter:
            self.llm_request_counter.add(1, labels)
        
        if self.llm_duration_histogram:
            self.llm_duration_histogram.record(duration_ms, labels)
        
        if self.token_counter and (input_tokens > 0 or output_tokens > 0):
            self.token_counter.add(input_tokens, {**labels, "type": "input"})
            self.token_counter.add(output_tokens, {**labels, "type": "output"})
        
        if self.cost_counter and cost > 0:
            self.cost_counter.add(cost, labels)
        
        # Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            if "llm_request_total" in self.prometheus_metrics:
                self.prometheus_metrics["llm_request_total"].labels(
                    provider=provider, model=model, status="success" if success else "failure"
                ).inc()
            
            if "llm_duration" in self.prometheus_metrics:
                self.prometheus_metrics["llm_duration"].labels(
                    provider=provider, model=model
                ).observe(duration_ms / 1000.0)
            
            if "tokens_total" in self.prometheus_metrics:
                if input_tokens > 0:
                    self.prometheus_metrics["tokens_total"].labels(
                        provider=provider, model=model, type="input"
                    ).inc(input_tokens)
                if output_tokens > 0:
                    self.prometheus_metrics["tokens_total"].labels(
                        provider=provider, model=model, type="output"
                    ).inc(output_tokens)
            
            if "cost_total" in self.prometheus_metrics and cost > 0:
                self.prometheus_metrics["cost_total"].labels(
                    provider=provider, model=model
                ).inc(cost)
    
    def record_stage_duration(self, stage: str, duration_ms: float):
        """Record pipeline stage duration."""
        labels = {"stage": stage}
        
        if self.stage_duration_histogram:
            self.stage_duration_histogram.record(duration_ms, labels)
        
        if PROMETHEUS_AVAILABLE and "stage_duration" in self.prometheus_metrics:
            self.prometheus_metrics["stage_duration"].labels(stage=stage).observe(duration_ms / 1000.0)
    
    def record_error(self, error_type: str, provider: Optional[str] = None, stage: Optional[str] = None):
        """Record error metrics."""
        labels = {
            "type": error_type,
            "provider": provider or "unknown",
            "stage": stage or "unknown"
        }
        
        if self.error_counter:
            self.error_counter.add(1, labels)
        
        if PROMETHEUS_AVAILABLE and "error_total" in self.prometheus_metrics:
            self.prometheus_metrics["error_total"].labels(
                type=error_type, provider=provider or "unknown", stage=stage or "unknown"
            ).inc()
    
    def update_circuit_breaker_state(self, provider: str, state: str):
        """Update circuit breaker state metric."""
        # Map state to numeric value
        state_map = {"closed": 0, "open": 1, "half_open": 2}
        state_value = state_map.get(state.lower(), -1)
        
        if PROMETHEUS_AVAILABLE and "circuit_breaker_state" in self.prometheus_metrics:
            self.prometheus_metrics["circuit_breaker_state"].labels(provider=provider).set(state_value)
    
    @contextmanager
    def measure_stage(self, stage_name: str):
        """Context manager to measure stage duration."""
        start_time = time.time()
        span = None
        
        if self.initialized and self.tracer:
            span = self.tracer.start_span(f"stage.{stage_name}")
            span.set_attribute("stage.name", stage_name)
        
        try:
            yield span
            if span:
                span.set_status(Status(StatusCode.OK))
        except Exception as e:
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            self.record_error("stage_error", stage=stage_name)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.record_stage_duration(stage_name, duration_ms)
            if span:
                span.end()


# Global telemetry instance
telemetry = TelemetryService()