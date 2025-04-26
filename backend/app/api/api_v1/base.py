from typing import Any, Callable, TypeVar, cast
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.models.base import BaseQueryModel, BaseResponseModel

T = TypeVar("T", bound=BaseModel)


class BaseRouter:
    """Base router with common functionality for all API routers."""

    def __init__(self, prefix: str, tags: list[str]):
        self.router = APIRouter(prefix=prefix, tags=tags)

    def get_query_params(self) -> BaseQueryModel:
        """Get query parameters from request."""
        return BaseQueryModel(
            page=Query(1, ge=1),
            page_size=Query(10, ge=1, le=100),
            sort_by=Query(None),
            sort_order=Query("asc", pattern="^(asc|desc)$"),
            search=Query(None),
            filters=Query({}),
        )

    def create_response(
        self,
        data: Any = None,
        message: str = None,
        metadata: dict = None,
    ) -> BaseResponseModel:
        """Create a standardized API response."""
        return BaseResponseModel(
            success=True,
            message=message,
            data=data,
            metadata=metadata or {},
        )

    def get(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator for GET endpoints."""
        return self.router.get(*args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator for POST endpoints."""
        return self.router.post(*args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator for PUT endpoints."""
        return self.router.put(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator for DELETE endpoints."""
        return self.router.delete(*args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator for PATCH endpoints."""
        return self.router.patch(*args, **kwargs)
