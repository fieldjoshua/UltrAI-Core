from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.utils.metrics import get_current_metrics, get_metrics_history

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

    return JSONResponse(
        content={
            "status": "success",
            "metrics": {
                "uptime_seconds": metrics["uptime_seconds"],
                "requests_processed": metrics["requests_processed"],
                "avg_processing_time": metrics["avg_processing_time"],
                "memory_usage_mb": metrics["memory_usage_mb"],
                "cache_hits": metrics["cache_hits"],
            },
        }
    )


@metrics_router.get("/api/metrics/history")
async def get_history():
    """Get historical metrics data"""
    history = get_metrics_history()

    return JSONResponse(
        content={
            "status": "success",
            "history": history
        }
    )