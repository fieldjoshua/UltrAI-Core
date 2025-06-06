"""
Error handling middleware for the Ultra backend.

This module provides global error handling middleware that catches
and formats all exceptions in a consistent way.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.error_handling import handle_error

# Set up logging
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors globally.

    This middleware catches all exceptions and formats them into
    consistent JSON responses using the error handling system.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and handle any errors that occur.

        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain

        Returns:
            Response: The response to send back to the client
        """
        try:
            # Process the request
            response = await call_next(request)
            return response

        except Exception as error:
            # Log the error
            logger.error(
                f"Error processing request {request.method} {request.url.path}: {str(error)}",
                exc_info=True,
            )

            # Handle the error and return formatted response
            return handle_error(error)
