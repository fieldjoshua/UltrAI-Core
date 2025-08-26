"""
Request ID middleware.

Adds/propagates X-Request-ID for correlation across services and logs.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that ensures each request has an X-Request-ID header."""

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = request.headers.get(self.header_name)
        if not req_id:
            req_id = str(uuid.uuid4())
        # expose on request state for downstream use
        request.state.request_id = req_id

        response = await call_next(request)
        # echo on response
        response.headers[self.header_name] = req_id
        return response


def setup_request_id_middleware(app: ASGIApp, header_name: str = "X-Request-ID") -> None:
    """Attach the RequestIDMiddleware to the app."""
    app.add_middleware(RequestIDMiddleware, header_name=header_name)
