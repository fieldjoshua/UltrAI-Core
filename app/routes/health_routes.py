"""
Route handlers for the Ultra backend.
"""

from fastapi import APIRouter
from typing import Optional

from app.services.health_service import HealthService


def create_router(health_service: Optional[HealthService] = None) -> APIRouter:
    """
    Create the router with all endpoints.

    Args:
        health_service: Optional HealthService instance. If not provided, a new one will be created.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Health"])

    # Create health service if not provided
    if health_service is None:
        health_service = HealthService()

    @router.get("/health")
    async def health_check(detailed: bool = False):
        """
        Health check endpoint.

        Args:
            detailed: Whether to include detailed health information

        Returns:
            dict: Health status information
        """
        return health_service.get_health_status(detailed=detailed)

    @router.get("/health/services")
    async def services_health():
        """
        Get detailed health status of all services.

        Returns:
            dict: Detailed service health information
        """
        return health_service.get_health_status(detailed=True)

    @router.get("/", include_in_schema=False)
    async def root():
        """Root welcome endpoint."""
        return {"message": "Welcome to the Ultra API! See /docs for usage."}

    return router


# Export the router for use in app/app.py
router = create_router()
