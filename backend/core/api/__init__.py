"""
API Layer Component

This module handles the essential API endpoints, authentication, and request/response handling.
"""

from typing import Dict, Optional, Any, Callable
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response model."""

    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


class APIRouter:
    """Manages API routes and endpoints."""

    def __init__(self):
        self.app = FastAPI()
        self._oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def add_route(self, path: str, method: str, handler: Callable):
        """Add a new route to the API."""
        if method.lower() == "get":
            self.app.get(path)(handler)
        elif method.lower() == "post":
            self.app.post(path)(handler)
        elif method.lower() == "put":
            self.app.put(path)(handler)
        elif method.lower() == "delete":
            self.app.delete(path)(handler)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def get_oauth2_scheme(self):
        """Get the OAuth2 scheme for dependency injection."""
        return self._oauth2_scheme

    async def get_current_user(self, token: str = Depends(get_oauth2_scheme)):
        """Get the current authenticated user."""
        # TODO: Implement user authentication
        raise NotImplementedError

    def create_response(
        self, status: str, message: str, data: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """Create a standardized API response."""
        return APIResponse(status=status, message=message, data=data)

    def handle_error(self, error: Exception) -> APIResponse:
        """Handle API errors and create appropriate responses."""
        if isinstance(error, HTTPException):
            return self.create_response(
                "error", str(error.detail), {"code": error.status_code}
            )
        return self.create_response("error", str(error), {"code": 500})
