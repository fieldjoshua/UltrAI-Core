from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

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
    def choose_encoder(accept_header):
        return exposition.choose_encoder(accept_header), CONTENT_TYPE_LATEST


from app.config import Config
from app.utils.metrics import (
    MetricsCollector,
    get_current_metrics,
    get_metrics_history,
)

# Create a metrics router
metrics_router = APIRouter(tags=["Metrics"])


@metrics_router.get("/api/status")
async def check_status():
    """Get API status with basic metrics"""
    metrics = get_current_metrics()

    return JSONResponse(
        content={
            "status": "operational",
            "uptime_seconds": metrics["uptime_seconds"],
            "requests_processed": metrics["requests_processed"],
            "avg_processing_time": metrics["avg_processing_time"],
            "memory_usage_mb": metrics["memory_usage_mb"],
        }
    )


@metrics_router.get("/api/metrics")
async def get_metrics():
    """Get detailed metrics about the API"""
    metrics = get_current_metrics()

    # Update system metrics to get latest values
    collector = MetricsCollector()
    collector.update_system_metrics()

    return JSONResponse(
        content={
            "status": "success",
            "metrics": {
                "uptime_seconds": metrics["uptime_seconds"],
                "requests_processed": metrics["requests_processed"],
                "avg_processing_time": metrics["avg_processing_time"],
                "memory_usage_mb": metrics["memory_usage_mb"],
                "cache_hits": metrics["cache_hits"],
                "prometheus_endpoint": f"http://localhost:{Config.METRICS_PORT}/metrics",
            },
        }
    )


@metrics_router.get("/api/metrics/history")
async def get_history():
    """Get historical metrics data"""
    history = get_metrics_history()

    return JSONResponse(content={"status": "success", "history": history})


@metrics_router.get("/metrics")
async def prometheus_metrics(request: Request):
    """
    Expose Prometheus metrics directly through the API

    This is in addition to the standalone metrics server, providing
    flexibility in how metrics are accessed.
    """
    if not Config.METRICS_ENABLED:
        return Response(content="Metrics collection is disabled", status_code=404)

    # Get accept header for proper encoding
    accept = request.headers.get("Accept", "")

    # Generate metrics output
    encoder, content_type = choose_encoder(accept)
    metrics_data = encoder(generate_latest())

    return Response(content=metrics_data, media_type=content_type)
