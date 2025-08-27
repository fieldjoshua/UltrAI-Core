"""
Performance optimization middleware for FastAPI.
"""

import time
import gzip
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import io

from app.utils.logging import get_logger

logger = get_logger("performance_middleware")


class CompressionMiddleware(BaseHTTPMiddleware):
    """Middleware to compress responses for better performance."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Process the request
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # Only compress for successful responses with sufficient content
        if response.status_code != 200:
            return response
            
        # Check content type - only compress text-based responses
        content_type = response.headers.get("content-type", "")
        compressible_types = ["application/json", "text/", "application/javascript"]
        
        if not any(ct in content_type for ct in compressible_types):
            return response
        
        # For streaming responses, we need special handling
        if isinstance(response, StreamingResponse):
            return response
        
        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        # Only compress if body is large enough (>1KB)
        if len(body) < 1024:
            # Return original response
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress the body
        compressed = gzip.compress(body)
        
        # Only use compression if it actually reduces size
        if len(compressed) >= len(body):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Return compressed response
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed))
        headers.pop("content-length", None)  # Remove original length
        
        return Response(
            content=compressed,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware to add cache control headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add cache headers based on endpoint
        path = request.url.path
        
        # Static assets - cache for 1 year
        if path.startswith("/assets/") or path.endswith((".js", ".css", ".png", ".jpg", ".ico")):
            response.headers["cache-control"] = "public, max-age=31536000, immutable"
        
        # API responses - different caching strategies
        elif path.startswith("/api/"):
            if path.endswith("/available-models"):
                # Cache model list for 5 minutes
                response.headers["cache-control"] = "public, max-age=300"
            elif path.endswith("/health"):
                # Don't cache health checks
                response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
            elif request.method == "GET":
                # Cache GET requests for 1 minute
                response.headers["cache-control"] = "private, max-age=60"
            else:
                # Don't cache POST/PUT/DELETE
                response.headers["cache-control"] = "no-cache, no-store"
        
        return response


class PerformanceHeadersMiddleware(BaseHTTPMiddleware):
    """Add performance-related headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Track request timing
        start_time = time.time()
        
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        # Add other performance headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable connection keep-alive
        response.headers["Connection"] = "keep-alive"
        
        return response


def setup_performance_middleware(app):
    """Setup all performance optimization middleware."""
    
    # Add compression middleware
    app.add_middleware(CompressionMiddleware)
    
    # Add cache control
    app.add_middleware(CacheControlMiddleware)
    
    # Add performance headers
    app.add_middleware(PerformanceHeadersMiddleware)
    
    logger.info("Performance optimization middleware enabled")