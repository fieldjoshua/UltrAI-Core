import psutil
import time
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.utils.metrics import start_time, get_current_metrics

# Create a health router
health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def basic_health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "uptime": time.time() - start_time}


@health_router.get("/api/health", tags=["Health"])
async def api_health_check():
    """API health check endpoint with more information"""
    return {"status": "healthy", "uptime": time.time() - start_time}


@health_router.get("/api/system/health")
async def get_health():
    """Detailed system health information"""
    # Get system information
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')

    # Get metrics from metrics module
    metrics = get_current_metrics()

    return JSONResponse(
        content={
            "status": "operational",
            "uptime_seconds": metrics["uptime_seconds"],
            "memory": {
                "total_gb": round(memory_info.total / (1024**3), 2),
                "available_gb": round(memory_info.available / (1024**3), 2),
                "percent_used": memory_info.percent,
                "application_mb": round(metrics["memory_usage_mb"], 2),
            },
            "disk": {
                "total_gb": round(disk_info.total / (1024**3), 2),
                "free_gb": round(disk_info.free / (1024**3), 2),
                "percent_used": disk_info.percent,
            },
            "requests": {
                "processed": metrics["requests_processed"],
                "avg_time": metrics.get("avg_processing_time", 0),
            },
        }
    )