"""
Metrics collection and monitoring using Prometheus.

This module provides a centralized metrics collection system using Prometheus client.
It defines standard metrics for API monitoring, system resources, and LLM-specific metrics.
"""

import logging
import os
import threading
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

try:
    import psutil
except ImportError:
    from app.utils.stubs import psutil

# Try to import prometheus_client, use stub if not available
try:
    from prometheus_client import Counter, Gauge, Histogram, Info, start_http_server
    from prometheus_client.core import REGISTRY
except ImportError:
    logging.warning("prometheus_client not found, using stub implementation")
    # Use the local stub implementation
    from app.utils.stubs.prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Info,
        start_http_server,
        REGISTRY,
    )

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Config

# Legacy metrics for backward compatibility
performance_metrics = {
    "start_time": datetime.now().isoformat(),
    "requests_processed": 0,
    "documents_processed": 0,
    "total_chunks_processed": 0,
    "total_processing_time": 0,
    "avg_processing_time": 0,
    "max_memory_usage": 0,
    "cache_hits": 0,
    "current_memory_usage_mb": psutil.Process().memory_info().rss / (1024 * 1024),
}

# Legacy metrics history
metrics_history = {
    "timestamps": [],
    "memory_usage": [],
    "requests_processed": [],
    "response_times": [],
}

# Legacy processing metrics
requests_processed = 0
processing_times: List[float] = []
start_time = time.time()


# Singleton pattern for MetricsCollector
class MetricsCollector:
    """
    Singleton class for collecting and managing Prometheus metrics.

    This class centralizes all metrics collection in the application and
    provides helper methods for tracking various kinds of metrics.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsCollector, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._metrics_enabled = (
            Config.METRICS_ENABLED if hasattr(Config, "METRICS_ENABLED") else False
        )
        self._metrics_port = (
            Config.METRICS_PORT if hasattr(Config, "METRICS_PORT") else 9090
        )

        # API metrics
        self.request_counter = Counter(
            "ultra_http_requests_total",
            "Total count of HTTP requests",
            ["method", "endpoint", "status_code"],
        )

        self.request_latency = Histogram(
            "ultra_http_request_duration_seconds",
            "HTTP request latency in seconds",
            ["method", "endpoint"],
            buckets=(
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                float("inf"),
            ),
        )

        self.request_in_progress = Gauge(
            "ultra_http_requests_in_progress",
            "Number of HTTP requests in progress",
            ["method", "endpoint"],
        )

        self.request_size_bytes = Histogram(
            "ultra_http_request_size_bytes",
            "HTTP request size in bytes",
            ["method", "endpoint"],
            buckets=(10, 100, 1000, 10000, 100000, 1000000, float("inf")),
        )

        self.response_size_bytes = Histogram(
            "ultra_http_response_size_bytes",
            "HTTP response size in bytes",
            ["method", "endpoint", "status_code"],
            buckets=(10, 100, 1000, 10000, 100000, 1000000, float("inf")),
        )

        # System metrics
        self.cpu_usage = Gauge("ultra_system_cpu_usage", "CPU usage percentage")
        self.memory_usage = Gauge(
            "ultra_system_memory_usage_bytes", "Memory usage in bytes"
        )
        self.memory_percent = Gauge(
            "ultra_system_memory_usage_percent", "Memory usage percentage"
        )
        self.disk_usage = Gauge("ultra_system_disk_usage_bytes", "Disk usage in bytes")
        self.disk_percent = Gauge(
            "ultra_system_disk_usage_percent", "Disk usage percentage"
        )

        # LLM metrics
        self.llm_requests = Counter(
            "ultra_llm_requests_total",
            "Total number of LLM requests",
            ["provider", "model", "status"],
        )

        self.llm_latency = Histogram(
            "ultra_llm_request_duration_seconds",
            "LLM request latency in seconds",
            ["provider", "model"],
            buckets=(
                0.1,
                0.5,
                1.0,
                2.0,
                5.0,
                10.0,
                15.0,
                30.0,
                60.0,
                120.0,
                float("inf"),
            ),
        )

        self.llm_tokens_input = Counter(
            "ultra_llm_tokens_input_total",
            "Total number of input tokens sent to LLMs",
            ["provider", "model"],
        )

        self.llm_tokens_output = Counter(
            "ultra_llm_tokens_output_total",
            "Total number of output tokens received from LLMs",
            ["provider", "model"],
        )

        # Cache metrics
        self.cache_hits = Counter(
            "ultra_cache_hits_total", "Total number of cache hits", ["cache_name"]
        )
        self.cache_misses = Counter(
            "ultra_cache_misses_total", "Total number of cache misses", ["cache_name"]
        )
        self.cache_size = Gauge(
            "ultra_cache_size_total", "Current number of items in cache", ["cache_name"]
        )

        # Document processing metrics
        self.docs_processed = Counter(
            "ultra_documents_processed_total", "Total number of documents processed"
        )
        self.chunks_processed = Counter(
            "ultra_document_chunks_processed_total",
            "Total number of document chunks processed",
        )
        self.doc_processing_time = Histogram(
            "ultra_document_processing_duration_seconds",
            "Document processing time in seconds",
            buckets=(
                0.1,
                0.5,
                1.0,
                2.0,
                5.0,
                10.0,
                30.0,
                60.0,
                120.0,
                300.0,
                float("inf"),
            ),
        )

        # Application info
        self.app_info = Info("ultra_app_info", "Application information")
        self.app_info.info(
            {"version": os.getenv("VERSION", "dev"), "environment": Config.ENVIRONMENT}
        )

    def start_metrics_server(self):
        """Start the Prometheus metrics server if metrics are enabled."""
        if not self._metrics_enabled:
            return

        start_http_server(self._metrics_port)

    def track_llm_request(
        self,
        provider: str,
        model: str,
        start_time: float,
        token_count_input: int,
        token_count_output: int,
        status: str = "success",
    ):
        """
        Track an LLM request with its performance metrics.

        Args:
            provider: The LLM provider (e.g., 'openai', 'anthropic')
            model: The specific model used
            start_time: The start time of the request (as returned by time.time())
            token_count_input: Number of input tokens sent
            token_count_output: Number of output tokens received
            status: Status of the request ('success', 'error', 'timeout')
        """
        if not self._metrics_enabled:
            return

        duration = time.time() - start_time
        self.llm_requests.labels(provider=provider, model=model, status=status).inc()
        self.llm_latency.labels(provider=provider, model=model).observe(duration)
        self.llm_tokens_input.labels(provider=provider, model=model).inc(
            token_count_input
        )
        self.llm_tokens_output.labels(provider=provider, model=model).inc(
            token_count_output
        )

    def update_system_metrics(self):
        """Update system resource metrics (CPU, memory, disk)."""
        if not self._metrics_enabled:
            return

        self.cpu_usage.set(psutil.cpu_percent())

        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)
        self.memory_percent.set(memory.percent)

        disk = psutil.disk_usage("/")
        self.disk_usage.set(disk.used)
        self.disk_percent.set(disk.percent)

    def record_cache_operation(
        self, cache_name: str, hit: bool, size: Optional[int] = None
    ):
        """
        Record a cache operation (hit or miss).

        Args:
            cache_name: The name of the cache
            hit: True if it was a cache hit, False for a miss
            size: Optional size of the cache to update the gauge
        """
        if not self._metrics_enabled:
            return

        # Update legacy metrics
        if hit:
            global performance_metrics
            performance_metrics["cache_hits"] += 1

        # Update Prometheus metrics
        if hit:
            self.cache_hits.labels(cache_name=cache_name).inc()
        else:
            self.cache_misses.labels(cache_name=cache_name).inc()

        if size is not None:
            self.cache_size.labels(cache_name=cache_name).set(size)

    def record_document_processing(self, processing_time: float, chunk_count: int = 1):
        """
        Record document processing metrics.

        Args:
            processing_time: Time taken to process the document in seconds
            chunk_count: Number of chunks processed from this document
        """
        if not self._metrics_enabled:
            return

        # Update legacy metrics
        global performance_metrics
        performance_metrics["documents_processed"] += 1
        performance_metrics["total_chunks_processed"] += chunk_count
        performance_metrics["total_processing_time"] += processing_time

        # Update Prometheus metrics
        self.docs_processed.inc()
        self.chunks_processed.inc(chunk_count)
        self.doc_processing_time.observe(processing_time)

    def track_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
    ):
        """
        Track an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            status_code: HTTP status code
            duration: Request duration in seconds
            request_size: Size of request in bytes
            response_size: Size of response in bytes
        """
        if not self._metrics_enabled:
            return

        # Update legacy metrics
        global performance_metrics, processing_times
        performance_metrics["requests_processed"] += 1
        processing_times.append(duration)

        # Limit size of processing_times to prevent memory issues
        max_times = 1000
        if len(processing_times) > max_times:
            processing_times = processing_times[-max_times:]

        # Update Prometheus metrics
        self.request_counter.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        self.request_latency.labels(method=method, endpoint=endpoint).observe(duration)

        if request_size is not None:
            self.request_size_bytes.labels(method=method, endpoint=endpoint).observe(
                request_size
            )

        if response_size is not None:
            self.response_size_bytes.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).observe(response_size)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting HTTP metrics for FastAPI requests.

    This middleware tracks request counts, latency, and sizes for all HTTP
    requests going through the FastAPI application.
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.metrics = MetricsCollector()

    async def dispatch(self, request: Request, call_next):
        # Only track metrics if enabled
        if not Config.METRICS_ENABLED:
            return await call_next(request)

        # Get the route path for metrics labeling
        route = request.url.path
        method = request.method

        # Track in-progress requests
        self.metrics.request_in_progress.labels(method=method, endpoint=route).inc()

        # Track request size if content length is available
        content_length = request.headers.get("content-length")
        request_size = int(content_length) if content_length else None

        # Track request latency
        start_time = time.time()
        response = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            # Record request metrics
            duration = time.time() - start_time

            # Get response size if available
            response_size = None
            if response is not None:
                resp_size = response.headers.get("content-length")
                response_size = int(resp_size) if resp_size else None

            # Record metrics
            self.metrics.track_request(
                method=method,
                endpoint=route,
                status_code=status_code,
                duration=duration,
                request_size=request_size,
                response_size=response_size,
            )

            # Track in-progress requests
            self.metrics.request_in_progress.labels(method=method, endpoint=route).dec()

        return response


def setup_metrics(app: FastAPI):
    """
    Configure metrics collection for a FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    metrics = MetricsCollector()

    if Config.METRICS_ENABLED:
        # Add metrics middleware
        app.add_middleware(MetricsMiddleware)

        # Start metrics server
        metrics.start_metrics_server()

        # Start system metrics collection in a background thread
        def collect_system_metrics():
            interval = Config.SYSTEM_METRICS_INTERVAL
            while True:
                metrics.update_system_metrics()
                update_metrics_history()  # Update legacy metrics as well
                time.sleep(interval)

        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()


def track_llm_metrics(provider: str, model: str):
    """
    Decorator for tracking LLM request metrics.

    Args:
        provider: The LLM provider name
        model: The model name

    Returns:
        Decorator function for wrapping LLM API calls
    """
    metrics = MetricsCollector()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not Config.METRICS_ENABLED:
                return await func(*args, **kwargs)

            start_time = time.time()
            token_count_input = kwargs.get("token_count_input", 0)
            if (
                not token_count_input
                and len(args) > 0
                and hasattr(args[0], "token_count")
            ):
                token_count_input = args[0].token_count

            try:
                result = await func(*args, **kwargs)

                # Try to get output token count
                token_count_output = 0
                if hasattr(result, "token_count"):
                    token_count_output = result.token_count
                elif isinstance(result, dict) and "token_count" in result:
                    token_count_output = result["token_count"]

                # Record metrics
                metrics.track_llm_request(
                    provider=provider,
                    model=model,
                    start_time=start_time,
                    token_count_input=token_count_input,
                    token_count_output=token_count_output,
                    status="success",
                )
                return result

            except Exception as e:
                # Record error metrics
                metrics.track_llm_request(
                    provider=provider,
                    model=model,
                    start_time=start_time,
                    token_count_input=token_count_input,
                    token_count_output=0,
                    status="error",
                )
                raise e

        return wrapper

    return decorator


# Decorator for tracking document processing
def track_document_processing(func):
    """Decorator to track document processing metrics."""
    metrics = MetricsCollector()

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)

        # Get chunk count if available in result
        chunk_count = 1
        if hasattr(result, "chunk_count"):
            chunk_count = result.chunk_count
        elif isinstance(result, dict) and "chunk_count" in result:
            chunk_count = result["chunk_count"]
        elif isinstance(result, list):
            chunk_count = len(result)

        # Record metrics
        processing_time = time.time() - start_time
        metrics.record_document_processing(processing_time, chunk_count)

        return result

    return wrapper


# Helper for tracking cache operations (for backward compatibility)
def track_cache_operation(cache_name: str, hit: bool, size: Optional[int] = None):
    """
    Helper function to record cache hits and misses.

    Args:
        cache_name: The name of the cache
        hit: True if it was a cache hit, False for a miss
        size: Optional current size of the cache
    """
    metrics = MetricsCollector()
    metrics.record_cache_operation(cache_name, hit, size)


# Legacy functions for backward compatibility
def update_metrics_history() -> None:
    """Update the metrics history with current values"""
    global metrics_history, performance_metrics

    # Update current memory usage
    current_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    performance_metrics["current_memory_usage_mb"] = current_memory

    # Add current values to history
    metrics_history["timestamps"].append(datetime.now().isoformat())
    metrics_history["memory_usage"].append(current_memory)
    metrics_history["requests_processed"].append(
        performance_metrics["requests_processed"]
    )

    # Calculate average processing time if we have data
    if processing_times:
        performance_metrics["avg_processing_time"] = sum(processing_times) / len(
            processing_times
        )

    # Limit history size to prevent memory issues
    max_history = 100
    if len(metrics_history["timestamps"]) > max_history:
        for key in metrics_history:
            metrics_history[key] = metrics_history[key][-max_history:]


def get_current_metrics() -> Dict[str, Any]:
    """Get the current metrics for the API status endpoint"""
    return {
        "uptime_seconds": time.time() - start_time,
        "requests_processed": performance_metrics["requests_processed"],
        "avg_processing_time": performance_metrics["avg_processing_time"],
        "memory_usage_mb": performance_metrics["current_memory_usage_mb"],
        "cache_hits": performance_metrics["cache_hits"],
    }


def get_metrics_history() -> Dict[str, Any]:
    """Get the metrics history for the API history endpoint"""
    return metrics_history
