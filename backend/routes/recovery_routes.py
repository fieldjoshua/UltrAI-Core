"""Manual recovery endpoints for admin operations.

This module provides API endpoints for manually triggering recovery
operations and monitoring recovery status.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..middleware.auth_middleware import require_admin, require_auth
from ..models.base_models import BaseResponse
from ..utils.circuit_breaker import circuit_manager
from ..utils.recovery_workflows import RecoveryWorkflow

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/recovery", tags=["recovery"])

# Recovery workflow instance (would be injected via dependency)
recovery_workflow: RecoveryWorkflow = None


def get_recovery_workflow() -> RecoveryWorkflow:
    """Dependency to get recovery workflow instance."""
    global recovery_workflow
    if not recovery_workflow:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Recovery workflow not initialized",
        )
    return recovery_workflow


@router.get("/status", response_model=BaseResponse)
async def get_recovery_status(
    current_user=Depends(require_admin),
    workflow: RecoveryWorkflow = Depends(get_recovery_workflow),
) -> BaseResponse:
    """Get current recovery status and history.

    Requires admin authentication.
    """
    try:
        status_data = workflow.get_recovery_status()

        return BaseResponse(
            success=True,
            data={
                "recovery_status": status_data,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error fetching recovery status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recovery status",
        )


@router.post("/trigger", response_model=BaseResponse)
async def trigger_recovery(
    recovery_request: Dict[str, Any],
    current_user=Depends(require_admin),
    workflow: RecoveryWorkflow = Depends(get_recovery_workflow),
) -> BaseResponse:
    """Manually trigger a recovery action.

    Requires admin authentication.

    Request body:
    {
        "error_type": "CIRCUIT_OPEN",
        "service_name": "openai",
        "context": {
            "additional": "data"
        }
    }
    """
    try:
        error_type = recovery_request.get("error_type")
        if not error_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="error_type is required"
            )

        context = recovery_request.get("context", {})
        context["service_name"] = recovery_request.get("service_name")
        context["manual_trigger"] = True
        context["triggered_by"] = current_user.get("username")

        # Trigger recovery
        success = await workflow.handle_failure(error_type, context)

        return BaseResponse(
            success=success,
            data={
                "recovery_triggered": True,
                "success": success,
                "error_type": error_type,
                "service_name": context.get("service_name"),
                "timestamp": datetime.now().isoformat(),
            },
            message="Recovery triggered successfully" if success else "Recovery failed",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering recovery: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger recovery",
        )


@router.post("/circuit-breaker/reset", response_model=BaseResponse)
async def reset_circuit_breaker(
    reset_request: Dict[str, str], current_user=Depends(require_admin)
) -> BaseResponse:
    """Manually reset a circuit breaker.

    Requires admin authentication.

    Request body:
    {
        "service_name": "openai"
    }
    """
    try:
        service_name = reset_request.get("service_name")
        if not service_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="service_name is required",
            )

        # Reset circuit breaker
        success = await circuit_manager.reset_breaker(service_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit breaker not found for service: {service_name}",
            )

        return BaseResponse(
            success=True,
            data={
                "service_name": service_name,
                "action": "reset",
                "timestamp": datetime.now().isoformat(),
            },
            message=f"Circuit breaker reset for service: {service_name}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting circuit breaker: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset circuit breaker",
        )


@router.get("/circuit-breaker/status", response_model=BaseResponse)
async def get_circuit_breaker_status(
    current_user=Depends(require_admin),
) -> BaseResponse:
    """Get status of all circuit breakers.

    Requires admin authentication.
    """
    try:
        all_statuses = circuit_manager.get_all_statuses()

        return BaseResponse(
            success=True,
            data={
                "circuit_breakers": all_statuses,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error fetching circuit breaker status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch circuit breaker status",
        )


@router.post("/cache/clear", response_model=BaseResponse)
async def clear_cache(
    current_user=Depends(require_admin),
    workflow: RecoveryWorkflow = Depends(get_recovery_workflow),
) -> BaseResponse:
    """Clear application cache.

    Requires admin authentication.
    """
    try:
        # Trigger cache recovery with clear flag
        context = {
            "clear_cache": True,
            "manual_trigger": True,
            "triggered_by": current_user.get("username"),
        }

        success = await workflow.handle_failure("CACHE_CLEAR_REQUESTED", context)

        return BaseResponse(
            success=success,
            data={
                "action": "cache_clear",
                "success": success,
                "timestamp": datetime.now().isoformat(),
            },
            message="Cache cleared successfully" if success else "Cache clear failed",
        )

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cache",
        )


@router.post("/database/reconnect", response_model=BaseResponse)
async def reconnect_database(
    current_user=Depends(require_admin),
    workflow: RecoveryWorkflow = Depends(get_recovery_workflow),
) -> BaseResponse:
    """Manually reconnect to database.

    Requires admin authentication.
    """
    try:
        # Trigger database recovery
        context = {"manual_trigger": True, "triggered_by": current_user.get("username")}

        success = await workflow.handle_failure("DB_RECONNECT_REQUESTED", context)

        return BaseResponse(
            success=success,
            data={
                "action": "database_reconnect",
                "success": success,
                "timestamp": datetime.now().isoformat(),
            },
            message=(
                "Database reconnected successfully"
                if success
                else "Database reconnection failed"
            ),
        )

    except Exception as e:
        logger.error(f"Error reconnecting database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reconnect database",
        )


@router.get("/history", response_model=BaseResponse)
async def get_recovery_history(
    limit: int = 50,
    error_type: str = None,
    current_user=Depends(require_admin),
    workflow: RecoveryWorkflow = Depends(get_recovery_workflow),
) -> BaseResponse:
    """Get recovery history with optional filtering.

    Requires admin authentication.
    """
    try:
        history = workflow.recovery_history[-limit:]

        # Filter by error type if specified
        if error_type:
            history = [h for h in history if h["error_type"] == error_type]

        return BaseResponse(
            success=True,
            data={
                "history": history,
                "count": len(history),
                "timestamp": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"Error fetching recovery history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recovery history",
        )


@router.get("/stats", response_model=BaseResponse)
async def get_recovery_stats(
    current_user=Depends(require_admin),
    workflow: RecoveryWorkflow = Depends(get_recovery_workflow),
) -> BaseResponse:
    """Get recovery statistics.

    Requires admin authentication.
    """
    try:
        stats = workflow._calculate_stats()

        return BaseResponse(
            success=True, data={"stats": stats, "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        logger.error(f"Error calculating recovery stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate recovery stats",
        )
