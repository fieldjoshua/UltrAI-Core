"""
Database middleware for the Ultra backend.

This module provides middleware for attaching database sessions to requests
and ensuring proper cleanup of database resources.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.database.connection import get_db_session
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("database_middleware", "logs/database.log")


class DatabaseMiddleware(BaseHTTPMiddleware):
    """Middleware for attaching database sessions to requests"""

    def __init__(self, app: ASGIApp):
        """
        Initialize database middleware

        Args:
            app: ASGI application
        """
        super().__init__(app)

    async def dispatch(self, request, call_next):
        """
        Process the request with a database session

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response
        """
        # Create a database session
        try:
            with get_db_session() as session:
                # Attach the session to the request state
                request.state.db = session

                # Process the request
                response = await call_next(request)

                return response
        except Exception as e:
            logger.error(f"Database middleware error: {str(e)}")
            # Let the exception propagate to error handlers
            raise
