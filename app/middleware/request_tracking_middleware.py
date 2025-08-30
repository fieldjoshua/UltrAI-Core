"""
Request tracking middleware for comprehensive request ID management.

This middleware ensures that every request has a unique ID that follows it
through all services, making debugging and log correlation much easier.
"""

import uuid
import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from app.utils.logging import CorrelationContext, get_logger, log_request, log_performance

logger = get_logger("request_tracking")


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking requests with unique IDs throughout the system."""
    
    # Standard header names for request tracking
    REQUEST_ID_HEADER = "X-Request-ID"
    CORRELATION_ID_HEADER = "X-Correlation-ID"
    TRACE_ID_HEADER = "X-Trace-ID"
    
    def __init__(self, app, service_name: str = "ultrai-orchestrator"):
        """
        Initialize request tracking middleware.
        
        Args:
            app: FastAPI application
            service_name: Name of this service for tracking
        """
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with tracking.
        
        Args:
            request: Incoming request
            call_next: Next middleware or endpoint
            
        Returns:
            Response with tracking headers
        """
        start_time = time.time()
        
        # Extract or generate request ID
        request_id = self._get_or_create_request_id(request)
        
        # Extract or generate correlation ID (for distributed tracing)
        correlation_id = self._get_or_create_correlation_id(request)
        
        # Set IDs in context for logging
        CorrelationContext.set_correlation_id(correlation_id)
        
        # Add IDs to request state for access in endpoints
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        request.state.service_name = self.service_name
        
        # Log request start
        self._log_request_start(request, request_id, correlation_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add tracking headers to response
            response.headers[self.REQUEST_ID_HEADER] = request_id
            response.headers[self.CORRELATION_ID_HEADER] = correlation_id
            response.headers["X-Service-Name"] = self.service_name
            
            # Log request completion
            duration_ms = (time.time() - start_time) * 1000
            self._log_request_complete(
                request, response, request_id, correlation_id, duration_ms
            )
            
            return response
            
        except Exception as e:
            # Log request failure
            duration_ms = (time.time() - start_time) * 1000
            self._log_request_error(
                request, e, request_id, correlation_id, duration_ms
            )
            raise
        finally:
            # Clear correlation context
            CorrelationContext.clear_correlation_id()
    
    def _get_or_create_request_id(self, request: Request) -> str:
        """Get request ID from headers or generate new one."""
        # Check multiple possible headers
        for header in [self.REQUEST_ID_HEADER, "Request-ID", "X-Amzn-Trace-Id"]:
            request_id = request.headers.get(header)
            if request_id:
                return request_id
        
        # Generate new request ID
        return f"req_{uuid.uuid4().hex[:16]}"
    
    def _get_or_create_correlation_id(self, request: Request) -> str:
        """Get correlation ID from headers or generate new one."""
        # Check for existing correlation ID
        for header in [self.CORRELATION_ID_HEADER, "Correlation-ID", self.TRACE_ID_HEADER]:
            correlation_id = request.headers.get(header)
            if correlation_id:
                return correlation_id
        
        # Use request ID as correlation ID if no correlation ID provided
        return request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
    
    def _log_request_start(
        self, 
        request: Request, 
        request_id: str, 
        correlation_id: str
    ) -> None:
        """Log the start of a request."""
        log_data = {
            "event": "request_start",
            "request_id": request_id,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "service": self.service_name,
            "headers": {
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "authorization": "Bearer ***" if request.headers.get("authorization") else None
            }
        }
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra=log_data
        )
        
        # Also log to request logger
        log_request(log_data)
    
    def _log_request_complete(
        self,
        request: Request,
        response: Response,
        request_id: str,
        correlation_id: str,
        duration_ms: float
    ) -> None:
        """Log the completion of a request."""
        log_data = {
            "event": "request_complete",
            "request_id": request_id,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "service": self.service_name
        }
        
        logger.info(
            f"Request completed: {request.method} {request.url.path} - "
            f"{response.status_code} in {duration_ms:.2f}ms",
            extra=log_data
        )
        
        # Log performance metrics
        log_performance(
            f"{request.method} {request.url.path}",
            duration_ms,
            {
                "status_code": response.status_code,
                "request_id": request_id
            }
        )
    
    def _log_request_error(
        self,
        request: Request,
        error: Exception,
        request_id: str,
        correlation_id: str,
        duration_ms: float
    ) -> None:
        """Log request error."""
        log_data = {
            "event": "request_error",
            "request_id": request_id,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_ms": duration_ms,
            "service": self.service_name
        }
        
        logger.error(
            f"Request failed: {request.method} {request.url.path} - "
            f"{type(error).__name__}: {str(error)}",
            extra=log_data,
            exc_info=error
        )


class RequestIDInjector:
    """Helper class to inject request IDs into outgoing HTTP requests."""
    
    @staticmethod
    def inject_headers(
        headers: dict,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> dict:
        """
        Inject tracking headers into outgoing request headers.
        
        Args:
            headers: Existing headers dictionary
            request_id: Request ID to inject
            correlation_id: Correlation ID to inject
            
        Returns:
            Updated headers dictionary
        """
        if request_id:
            headers[RequestTrackingMiddleware.REQUEST_ID_HEADER] = request_id
        
        if correlation_id:
            headers[RequestTrackingMiddleware.CORRELATION_ID_HEADER] = correlation_id
        elif not correlation_id and request_id:
            # Use request ID as correlation ID if not provided
            headers[RequestTrackingMiddleware.CORRELATION_ID_HEADER] = request_id
        
        return headers
    
    @staticmethod
    def from_request(request: Request, headers: dict) -> dict:
        """
        Extract tracking IDs from request and inject into headers.
        
        Args:
            request: FastAPI request object
            headers: Headers dictionary to update
            
        Returns:
            Updated headers dictionary
        """
        request_id = getattr(request.state, "request_id", None)
        correlation_id = getattr(request.state, "correlation_id", None)
        
        return RequestIDInjector.inject_headers(headers, request_id, correlation_id)