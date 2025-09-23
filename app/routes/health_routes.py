"""
Route handlers for the Ultra backend.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from app.services.health_service import HealthService
from app.services.policy_service import policy_service
from app.database.connection import get_db_session
from app.database.connection import is_using_fallback


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
        # Always return at minimum { status: "ok", ... }
        health_data = health_service.get_health_status(detailed=detailed)
        # include policy version for visibility
        try:
            health_data["policy_version"] = policy_service.get_version()
        except Exception:
            pass
        return health_data

    @router.get("/health/services")
    async def services_health():
        """
        Get detailed health status of all services.

        Returns:
            dict: Detailed service health information
        """
        # Return { status: "ok", services: { db: "...", cache: "...", ... } }
        health_data = health_service.get_health_status(detailed=False)
        return {
            "status": health_data.get("status", "ok"),
            "services": health_data.get("services", {})
        }

    @router.get("/db/ping")
    async def db_ping():
        """Simple DB connectivity check using SELECT 1."""
        try:
            with get_db_session() as session:  # type: ignore
                # Execute a lightweight query
                try:
                    from app.utils.dependency_manager import sqlalchemy_dependency

                    if not sqlalchemy_dependency.is_available() or is_using_fallback():
                        # When using fallback, consider ping successful
                        return {"status": "ok", "using_fallback": True}

                    sqlalchemy = sqlalchemy_dependency.get_module()
                    session.execute(sqlalchemy.text("SELECT 1"))
                    return {"status": "ok", "using_fallback": False}
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"DB ping failed: {str(e)}",
                    )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"DB session error: {str(e)}",
            )

    # Note: Root route removed to allow frontend serving
    # API welcome available at /health instead

    return router


# Export the router for use in app/app.py
router = create_router()
