"""
Middleware components for the UltraAI backend.

This module provides middleware for:
- Request validation
- Content-type checking
- Request size limiting
- Performance monitoring
- Rate limiting
"""

import time
from typing import List, Optional, Set

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from backend.utils.logging import CorrelationContext, log_performance, log_request
from backend.utils.rate_limit_middleware import setup_rate_limit_middleware


class RequestValidationMiddleware:
    """Middleware for validating incoming requests"""

    def __init__(
        self,
        app: ASGIApp,
        allowed_content_types: Optional[Set[str]] = None,
        max_content_length: Optional[int] = None,
        required_headers: Optional[List[str]] = None,
    ):
        """
        Initialize the middleware

        Args:
            app: The ASGI application
            allowed_content_types: Set of allowed content types
            max_content_length: Maximum allowed content length in bytes
            required_headers: List of required headers
        """
        self.app = app
        self.allowed_content_types = allowed_content_types or {
            "application/json",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
        }
        self.max_content_length = (
            max_content_length or 100 * 1024 * 1024
        )  # 100MB default
        self.required_headers = required_headers or []

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Process the request"""
        if scope["type"] != "http":
            # Pass through non-HTTP requests
            await self.app(scope, receive, send)
            return

        # Create request object
        request = Request(scope=scope, receive=receive)

        # Check content type for appropriate methods
        if request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "").split(";")[0].lower()

            # Check if content type is allowed
            if (
                self.allowed_content_types
                and content_type not in self.allowed_content_types
            ):
                return await self._send_error_response(
                    send,
                    f"Unsupported content type: {content_type}. Allowed types: {', '.join(self.allowed_content_types)}",
                    415,  # Unsupported Media Type
                )

            # Check content length
            content_length = request.headers.get("content-length")
            if (
                content_length
                and self.max_content_length
                and int(content_length) > self.max_content_length
            ):
                return await self._send_error_response(
                    send,
                    f"Request body too large. Maximum size: {self.max_content_length} bytes",
                    413,  # Request Entity Too Large
                )

        # Check required headers
        for header in self.required_headers:
            if header.lower() not in request.headers:
                return await self._send_error_response(
                    send,
                    f"Missing required header: {header}",
                    400,  # Bad Request
                )

        # Pass the request to the next middleware or route handler
        await self.app(scope, receive, send)

    async def _send_error_response(self, send: Send, message: str, status_code: int):
        """Send an error response"""
        # Create error response using the standard format
        error_response = {
            "status": "error",
            "message": message,
            "code": f"http_{status_code}",
            "request_id": CorrelationContext.get_correlation_id(),
        }

        # Convert to JSON
        body = JSONResponse(
            status_code=status_code,
            content=error_response,
        ).body

        # Create response headers
        headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
            (b"x-correlation-id", CorrelationContext.get_correlation_id().encode()),
        ]

        # Send response
        await send(
            {"type": "http.response.start", "status": status_code, "headers": headers}
        )
        await send({"type": "http.response.body", "body": body})


class RequestLoggingMiddleware:
    """Middleware for logging request and response information"""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
        include_request_body: bool = False,
        include_response_body: bool = False,
    ):
        """
        Initialize the middleware

        Args:
            app: The ASGI application
            exclude_paths: Paths to exclude from logging
            include_request_body: Whether to include request bodies in logs
            include_response_body: Whether to include response bodies in logs
        """
        self.app = app
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
        self.include_request_body = include_request_body
        self.include_response_body = include_response_body

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Process the request"""
        if scope["type"] != "http":
            # Pass through non-HTTP requests
            await self.app(scope, receive, send)
            return

        # Create request object
        request = Request(scope=scope)

        # Skip logging for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        # Start timer
        start_time = time.time()

        # Prepare request data for logging
        request_data = {
            "method": request.method,
            "path": str(request.url),
            "headers": dict(request.headers),
            "client_host": scope.get("client")[0] if scope.get("client") else None,
        }

        # Include request body if configured
        if self.include_request_body and request.method in ("POST", "PUT", "PATCH"):
            try:
                # Clone the receive channel to read the body
                body = await self._get_request_body(receive)
                request_data["body"] = body

                # Create a new receive channel that will return the body
                async def receive_with_body():
                    return {
                        "type": "http.request",
                        "body": body.encode(),
                        "more_body": False,
                    }

                receive = receive_with_body
            except Exception as e:
                # Log the error but continue without the body
                request_data["body_error"] = f"Could not read request body: {str(e)}"

        # Create a response interceptor to capture response details
        response_data = {"status_code": None, "headers": None, "body": None}

        async def send_interceptor(message: Message):
            if message["type"] == "http.response.start":
                response_data["status_code"] = message["status"]
                response_data["headers"] = dict(MutableHeaders(scope=message))

            elif message["type"] == "http.response.body" and self.include_response_body:
                response_data["body"] = message["body"].decode(
                    "utf-8", errors="replace"
                )

            await send(message)

            # Log the request-response after the response is fully sent
            if message["type"] == "http.response.body" and not message.get(
                "more_body", False
            ):
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Add response data to request log
                request_data["response"] = {
                    "status_code": response_data["status_code"],
                    "headers": response_data["headers"],
                    "duration_ms": duration_ms,
                }

                if self.include_response_body and response_data["body"]:
                    request_data["response"]["body"] = response_data["body"]

                # Log the request
                log_request(request_data)

                # Log performance separately
                log_performance(
                    f"{request.method} {path}",
                    duration_ms,
                    metadata={"status_code": response_data["status_code"]},
                )

        # Process the request with the intercepted send
        await self.app(scope, receive, send_interceptor)

    async def _get_request_body(self, receive: Receive) -> str:
        """Get the request body as a string"""
        body = b""
        more_body = True

        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        return body.decode("utf-8", errors="replace")


class PerformanceMiddleware:
    """Middleware for tracking performance metrics"""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        Initialize the middleware

        Args:
            app: The ASGI application
            exclude_paths: Paths to exclude from performance tracking
        """
        self.app = app
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Process the request"""
        if scope["type"] != "http":
            # Pass through non-HTTP requests
            await self.app(scope, receive, send)
            return

        # Create request object
        request = Request(scope=scope)

        # Skip tracking for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        # Start timer
        start_time = time.time()

        # Track response status
        response_status = {"code": 200}  # Default

        async def send_interceptor(message: Message):
            if message["type"] == "http.response.start":
                response_status["code"] = message["status"]

            await send(message)

            # Log performance after the response is fully sent
            if message["type"] == "http.response.body" and not message.get(
                "more_body", False
            ):
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log performance
                log_performance(
                    f"{request.method} {path}",
                    duration_ms,
                    metadata={
                        "status_code": response_status["code"],
                        "method": request.method,
                        "path": path,
                    },
                )

        # Process the request with the intercepted send
        await self.app(scope, receive, send_interceptor)


def setup_middleware(app: FastAPI) -> None:
    """
    Set up all middleware for the FastAPI application

    Args:
        app: The FastAPI application
    """
    # Add rate limiting middleware
    setup_rate_limit_middleware(app)
