from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.config import Config
from app.services.health_service import HealthService
from app.utils.logging import get_logger

"""
Health check routes for the Ultra backend.

This module provides API routes for health checks, including ping, application health,
service health, LLM provider health, and circuit breaker status.
"""

logger = get_logger("health_routes")

# Default query parameters
DEFAULT_DETAIL = False
DEFAULT_DETAIL_QUERY = Query(
    DEFAULT_DETAIL, description="Include detailed health information"
)


def create_router(health_service: HealthService) -> APIRouter:
    """
    Create the health check router with dependencies.

    Args:
        health_service: The health service instance to use for health checks

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["health"])

    @router.get("/ping", summary="Simple ping endpoint")
    async def ping():
        """
        Get ping.
        WARNING: This endpoint is for development/testing only. Do not use in production.
        """
        return {"status": "ok", "message": "pong"}

    @router.get(
        "/health",
        summary="Get application health status",
        response_model=Dict[str, Any],
    )
    async def get_health(detail: bool = DEFAULT_DETAIL_QUERY):
        """
        Get the health status of the application.

        - **detail**: Set to true to include detailed information about services and system.

        Returns a health status object with overall status and service information.
        """
        try:
            # Log the health check
            logger.info(f"Health check requested with detail={detail}")

            # Try to get health status, but provide basic response if service fails
            try:
                # Get health status
                health_status = health_service.get_health_status(detailed=detail)

                # Add orchestrator router debug info if detailed
                if detail:
                    try:
                        # from app.routes.orchestrator_routes import orchestrator_router  # TODO: Fix import if/when module exists
                        pass  # Orchestrator router import skipped due to unresolved module
                        # health_status["orchestrator_debug"] = {
                        #     "router_imported": True,
                        #     "route_count": len(orchestrator_router.routes),
                        #     "routes": [
                        #         f"{getattr(route, 'methods', 'UNKNOWN')} {getattr(route, 'path', 'UNKNOWN')}"
                        #         for route in orchestrator_router.routes
                        #     ],
                        # }
                    except Exception as e:
                        health_status["orchestrator_debug"] = {
                            "router_imported": False,
                            "import_error": str(e),
                        }

                return health_status
            except Exception as service_error:
                # If health service fails, return basic health status
                logger.warning(
                    f"Health service error: {str(service_error)}, returning basic status"
                )
                return {
                    "status": "degraded",
                    "message": "Health service unavailable, but API is running",
                    "environment": Config.ENVIRONMENT,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(service_error) if detail else None,
                }
        except Exception as e:
            logger.error(f"Error retrieving health status: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving health status: {str(e)}",
            )

    @router.get(
        "/health/{service_name}",
        summary="Check specific service health",
        response_model=Dict[str, Any],
    )
    async def get_service_health(service_name: str):
        """
        Get check service health.
        WARNING: This endpoint is for development/testing only. Do not use in production.
        """
        try:
            # Log the service health check
            logger.info(f"Service health check requested for {service_name}")

            # Check service status
            service_status, message = health_service.check_service_status(service_name)

            # Return service status
            return {
                "service": service_name,
                "status": service_status,
                "message": message,
                "environment": Config.ENVIRONMENT,
            }
        except Exception as e:
            logger.error(f"Error checking service {service_name} health: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking service health: {str(e)}",
            )

    @router.get(
        "/health/llm/providers",
        summary="Check LLM provider health",
        response_model=Dict[str, Any],
    )
    async def get_llm_providers_health():
        """
        Get check llm providers health.
        WARNING: This endpoint is for development/testing only. Do not use in production.
        """
        try:
            # Log the LLM providers health check
            logger.info("LLM providers health check requested")

            # Get provider details from health service
            providers_status = health_service._check_llm_provider_connectivity()

            # Count available providers
            available_count = sum(
                1
                for _, provider_status in providers_status.items()
                if provider_status.get("status") == "healthy"
            )

            # Determine overall status
            if available_count > 0:
                overall_status = "healthy"
                status_message = f"{available_count} LLM providers available"
            elif providers_status:
                overall_status = "degraded"
                status_message = "No LLM providers available"
            else:
                overall_status = "unavailable"
                status_message = "No LLM providers configured"

            # Return comprehensive status
            return {
                "status": overall_status,
                "message": status_message,
                "providers_count": len(providers_status),
                "available_count": available_count,
                "providers": providers_status,
                "environment": Config.ENVIRONMENT,
                "mock_mode": Config.USE_MOCK or Config.MOCK_MODE,
            }
        except Exception as e:
            logger.error(f"Error checking LLM providers health: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking LLM providers health: {str(e)}",
            )

    @router.get(
        "/health/circuit-breakers",
        summary="Check circuit breaker status",
        response_model=Dict[str, Any],
    )
    async def get_circuit_breakers_health():
        """
        Get check circuit breakers.
        WARNING: This endpoint is for development/testing only. Do not use in production.
        """
        try:
            # Log the circuit breakers check
            logger.info("Circuit breakers status check requested")

            # Get circuit breaker status from health service
            health_status = health_service.get_health_status(detailed=True)
            circuit_breakers = health_status.get("service_details", {}).get(
                "circuit_breakers", {}
            )

            # Return circuit breaker status
            return {
                "status": "ok",
                "circuit_breakers": circuit_breakers,
                "environment": Config.ENVIRONMENT,
            }
        except Exception as e:
            logger.error(f"Error checking circuit breakers: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error checking circuit breakers: {str(e)}",
            )

    return router
