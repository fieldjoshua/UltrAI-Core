"""
Route handlers for the Ultra backend.
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
except ImportError:

    def generate_latest(*args, **kwargs):
        return b"# Prometheus client not installed. No metrics available."

    CONTENT_TYPE_LATEST = "text/plain"


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Metrics"])

    @router.get("/metrics", response_class=PlainTextResponse)
    async def metrics():
        """Prometheus metrics endpoint."""
        data = generate_latest()
        return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)

    return router


metrics_router = create_router()  # Expose router for application
