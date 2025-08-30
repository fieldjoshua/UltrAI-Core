"""
Request ID middleware.

Adds/propagates X-Request-ID for correlation across services and logs.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging import CorrelationContext, get_logger

logger = get_logger("request_id_middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that ensures each request has an X-Request-ID header."""

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name
        self.correlation_header = "X-Correlation-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or create request ID
        req_id = request.headers.get(self.header_name)
        if not req_id:
            req_id = f"req_{uuid.uuid4().hex[:16]}"
        
        # Get or create correlation ID
        correlation_id = request.headers.get(self.correlation_header)
        if not correlation_id:
            correlation_id = request.headers.get("X-Trace-ID", req_id)
        
        # Set in request state for downstream use
        request.state.request_id = req_id
        request.state.correlation_id = correlation_id
        
        # Set correlation context for logging
        CorrelationContext.set_correlation_id(correlation_id)
        
        logger.debug(
            f"Processing request: {request.method} {request.url.path}",
            extra={
                "request_id": req_id,
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path
            }
        )
        
        try:
            response = await call_next(request)
            
            # Add tracking headers to response
            response.headers[self.header_name] = req_id
            response.headers[self.correlation_header] = correlation_id
            
            return response
        finally:
            # Clear correlation context
            CorrelationContext.clear_correlation_id()


def setup_request_id_middleware(app: ASGIApp, header_name: str = "X-Request-ID") -> None:
    """Attach the RequestIDMiddleware to the app."""
    app.add_middleware(RequestIDMiddleware, header_name=header_name)
