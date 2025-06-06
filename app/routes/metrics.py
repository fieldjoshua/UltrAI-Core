from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Request, Response
"""
Metrics routes for the Ultra backend.

This module provides API routes for system metrics and monitoring.
"""

from typing import Any, Dict, Union

from fastapi import APIRouter, Request, Response

# Try to import from prometheus_client, use stub if not available
try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    from prometheus_client.exposition import choose_encoder
except ImportError:
    from app.utils.stubs.prometheus_client import (
        CONTENT_TYPE_LATEST,
        exposition,
        generate_latest,
    )

    # Define choose_encoder if we're using the stub
    def choose_encoder(accept_header: str) -> tuple[Any, str]:  # type: ignore
        return exposition.choose_encoder(accept_header), CONTENT_TYPE_LATEST


from app.config import Config
from app.utils.metrics import (
    MetricsCollector,
    get_current_metrics,
    get_metrics_history,
)

# Create a metrics router
metrics_router = APIRouter(tags=["Metrics"])


class StatusResponse(BaseModel):
    """Response model for status endpoint."""

    status: str
    uptime_seconds: float
    requests_processed: int
    avg_processing_time: float
    memory_usage_mb: float


@metrics_router.get("/api/status", response_model=StatusResponse)
async def check_status() -> StatusResponse:
    """
    Get current system status and basic metrics.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    metrics = get_current_metrics()

    return StatusResponse(
        status="operational",
        uptime_seconds=metrics["uptime_seconds"],
        requests_processed=metrics["requests_processed"],
        avg_processing_time=metrics["avg_processing_time"],
        memory_usage_mb=metrics["memory_usage_mb"],
    )


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    status: str
    metrics: Dict[str, Union[float, int, str]]


@metrics_router.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    Get detailed system metrics including Prometheus endpoint.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    metrics = get_current_metrics()

    # Update system metrics to get latest values
    collector = MetricsCollector()
    collector.update_system_metrics()

    return MetricsResponse(
        status="success",
        metrics={
            "uptime_seconds": metrics["uptime_seconds"],
            "requests_processed": metrics["requests_processed"],
            "avg_processing_time": metrics["avg_processing_time"],
            "memory_usage_mb": metrics["memory_usage_mb"],
            "cache_hits": metrics["cache_hits"],
            "prometheus_endpoint": f"http://localhost:{Config.METRICS_PORT}/metrics",
        },
    )


class HistoryResponse(BaseModel):
    """Response model for metrics history endpoint."""

    status: str
    history: Dict[str, Any]


@metrics_router.get("/api/metrics/history", response_model=HistoryResponse)
async def get_history() -> HistoryResponse:
    """
    Get historical metrics data.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    history = get_metrics_history()

    return HistoryResponse(
        status="success",
        history=history,
    )


@metrics_router.get("/metrics")
async def prometheus_metrics(request: Request) -> Response:
    """
    Get metrics in Prometheus format.
    WARNING: This endpoint is for development/testing only. Do not use in production.
    """
    if not Config.METRICS_ENABLED:
        return Response(content="Metrics collection is disabled", status_code=404)

    # Get accept header for proper encoding
    accept = request.headers.get("Accept", "")

    # Generate metrics output
    encoder, content_type = choose_encoder(accept)
    metrics_data = encoder(generate_latest())

    return Response(content=metrics_data, media_type=content_type)
