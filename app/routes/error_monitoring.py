"""
Error Monitoring and Status Endpoints

These endpoints provide enhanced error monitoring capabilities for the UltrAI
orchestration pipeline, complementing Aux Model's work on service status and
provider health monitoring.

Integration points:
- Provides detailed error context for 503 status responses
- Complements provider health probe data
- Supports UI error displays with actionable suggestions
"""

from typing import Optional
from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from app.services.enhanced_error_handler import enhanced_error_handler
from app.utils.logging import get_logger

logger = get_logger("error_monitoring")

router = APIRouter(prefix="/api/errors", tags=["error-monitoring"])


class ErrorSummaryResponse(BaseModel):
    """Response model for error summary endpoint."""
    provider_health: dict
    recent_errors: dict
    correlation_id: Optional[str]
    timestamp: str


class CircuitBreakerStatusResponse(BaseModel):
    """Response model for circuit breaker status."""
    provider: str
    state: str
    failure_count: int
    consecutive_failures: int
    last_failure: Optional[str]
    last_success: Optional[str] 
    next_retry: Optional[str]


@router.get(
    "/summary",
    response_model=ErrorSummaryResponse,
    summary="Get Error Summary",
    description="Get comprehensive error summary including provider health and recent errors"
)
async def get_error_summary(
    request: Request,
    correlation_id: Optional[str] = Query(None, description="Filter by correlation ID")
):
    """
    Get comprehensive error summary for monitoring and debugging.
    
    This endpoint provides:
    - Provider circuit breaker states
    - Recent error counts by severity
    - Recovery suggestions
    
    Integrates with Aux Model's status monitoring work.
    """
    try:
        summary = enhanced_error_handler.get_error_summary(correlation_id)
        
        logger.info(
            f"Error summary requested for correlation_id: {correlation_id}",
            extra={
                "correlation_id": correlation_id,
                "recent_error_count": summary["recent_errors"]["total_count"]
            }
        )
        
        return ErrorSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Error retrieving error summary: {e}", exc_info=True)
        raise


@router.get(
    "/circuit-breakers",
    response_model=list[CircuitBreakerStatusResponse],
    summary="Get Circuit Breaker Status",
    description="Get current circuit breaker states for all providers"
)
async def get_circuit_breaker_status(request: Request):
    """
    Get current circuit breaker states for all providers.
    
    This complements Aux Model's provider health probes by showing
    circuit breaker logic and failure patterns.
    """
    try:
        circuit_states = []
        for provider, state in enhanced_error_handler.circuit_breakers.items():
            circuit_states.append(CircuitBreakerStatusResponse(
                provider=provider,
                state=state.state.value,
                failure_count=state.failure_count,
                consecutive_failures=state.consecutive_failures,
                last_failure=state.last_failure_time.isoformat() if state.last_failure_time else None,
                last_success=state.last_success_time.isoformat() if state.last_success_time else None,
                next_retry=state.next_retry_time.isoformat() if state.next_retry_time else None
            ))
        
        logger.info(
            f"Circuit breaker status requested for {len(circuit_states)} providers",
            extra={"provider_count": len(circuit_states)}
        )
        
        return circuit_states
        
    except Exception as e:
        logger.error(f"Error retrieving circuit breaker status: {e}", exc_info=True)
        raise


@router.post(
    "/reset-circuit-breaker/{provider}",
    summary="Reset Circuit Breaker",
    description="Manually reset circuit breaker for a specific provider"
)
async def reset_circuit_breaker(request: Request, provider: str):
    """
    Manually reset circuit breaker for a specific provider.
    
    This can be used when provider issues are resolved externally
    and we want to resume normal operation.
    """
    try:
        if provider in enhanced_error_handler.circuit_breakers:
            circuit_state = enhanced_error_handler.circuit_breakers[provider]
            
            # Reset to healthy state
            from app.services.enhanced_error_handler import ProviderState
            circuit_state.state = ProviderState.HEALTHY
            circuit_state.consecutive_failures = 0
            circuit_state.next_retry_time = None
            
            logger.info(
                f"Circuit breaker manually reset for provider: {provider}",
                extra={"provider": provider, "action": "manual_reset"}
            )
            
            return {
                "success": True,
                "message": f"Circuit breaker reset for provider {provider}",
                "provider": provider
            }
        else:
            return {
                "success": False,
                "message": f"No circuit breaker found for provider {provider}",
                "provider": provider
            }
            
    except Exception as e:
        logger.error(f"Error resetting circuit breaker for {provider}: {e}", exc_info=True)
        raise


def create_error_monitoring_router() -> APIRouter:
    """Create and return the error monitoring router."""
    return router