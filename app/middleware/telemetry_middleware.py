"""
Telemetry middleware for automatic request tracing and metrics.

This middleware:
- Traces all HTTP requests with OpenTelemetry
- Records request metrics (count, duration, status)
- Propagates correlation IDs
- Handles errors gracefully
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.telemetry_service import telemetry
from app.utils.logging import get_logger, CorrelationContext

logger = get_logger(__name__)


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware for request telemetry."""

    def __init__(self, app: ASGIApp):
        """Initialize telemetry middleware."""
        super().__init__(app)
        logger.info("Telemetry middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with telemetry.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response with telemetry recorded
        """
        # Skip telemetry for metrics endpoint to avoid recursion
        if request.url.path == "/api/metrics":
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract request attributes
        method = request.method
        path = request.url.path
        request_id = request.headers.get("X-Request-ID", CorrelationContext.get_correlation_id())
        
        # Create span attributes
        span_attributes = {
            "http.method": method,
            "http.url": str(request.url),
            "http.scheme": request.url.scheme,
            "http.host": request.url.hostname,
            "http.target": path,
            "http.user_agent": request.headers.get("User-Agent", "unknown"),
            "request.id": request_id,
        }
        
        # Add user info if available
        if hasattr(request.state, "user_id"):
            span_attributes["user.id"] = request.state.user_id
        if hasattr(request.state, "auth_method"):
            span_attributes["auth.method"] = request.state.auth_method
        
        # Start trace span
        with telemetry.trace_span(f"{method} {path}", span_attributes) as span:
            try:
                # Process request
                response = await call_next(request)
                
                # Update span with response info
                if span:
                    span.set_attribute("http.status_code", response.status_code)
                    span.set_attribute("http.response.size", 
                                     int(response.headers.get("content-length", 0)))
                
                # Record metrics
                duration_ms = (time.time() - start_time) * 1000
                telemetry.record_request(method, path, response.status_code, duration_ms)
                
                # Log request completion
                logger.info(
                    f"{method} {path} completed",
                    extra={
                        "requestId": request_id,
                        "method": method,
                        "path": path,
                        "status": response.status_code,
                        "duration_ms": duration_ms,
                    }
                )
                
                return response
                
            except Exception as e:
                # Record error
                duration_ms = (time.time() - start_time) * 1000
                telemetry.record_request(method, path, 500, duration_ms)
                telemetry.record_error("request_error", stage="middleware")
                
                logger.error(
                    f"Request failed: {method} {path}",
                    extra={
                        "requestId": request_id,
                        "method": method,
                        "path": path,
                        "error": str(e),
                        "duration_ms": duration_ms,
                    },
                    exc_info=True
                )
                
                raise


def setup_telemetry_middleware(app: ASGIApp) -> None:
    """
    Set up telemetry middleware for the application.

    Args:
        app: FastAPI application
    """
    app.add_middleware(TelemetryMiddleware)
    logger.info("Telemetry middleware added to application")