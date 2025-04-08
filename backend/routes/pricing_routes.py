import logging
from typing import Optional, Dict, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.models.pricing import TokenEstimateRequest, PricingToggleRequest, UserAccountRequest, AddFundsRequest

# Create a pricing router
pricing_router = APIRouter(tags=["Pricing"])

# Configure logging
logger = logging.getLogger("pricing_routes")

# Import pricing integration
try:
    from backend.services.pricing_integration import PricingIntegration
    pricing_integration = PricingIntegration()
    from backend.services.pricing_integration import check_request_authorization, track_request_cost

except ImportError:
    logger.warning("PricingIntegration not available, using mock")
    # Create a mock pricing integration
    class MockPricingIntegration:
        def __init__(self):
            self.pricing_enabled = False

        def estimate_request_cost(self, **kwargs) -> Dict[str, Any]:
            return {
                "estimated_cost": 0.01,
                "tier": "free",
                "has_sufficient_balance": True,
                "cost_details": {
                    "base_cost": 0.01,
                    "markup_cost": 0,
                    "discount_amount": 0,
                    "feature_costs": {},
                },
            }

        def create_user_account(self, user_id: str, tier: str = "basic", initial_balance: float = 0.0) -> Dict[str, Any]:
            return {
                "id": user_id,
                "tier": tier,
                "balance": initial_balance,
                "created_at": "mock-timestamp"
            }

        def add_funds(self, user_id: str, amount: float, description: str = "Deposit") -> Dict[str, Any]:
            return {
                "user_id": user_id,
                "amount": amount,
                "description": description,
                "transaction_id": "mock-transaction",
                "timestamp": "mock-timestamp"
            }

        def check_balance(self, user_id: str) -> Dict[str, Any]:
            return {
                "user_id": user_id,
                "balance": 100.0,
                "tier": "basic"
            }

        def get_user_usage_summary(self, user_id: str) -> Dict[str, Any]:
            return {
                "user_id": user_id,
                "total_tokens": 0,
                "total_cost": 0.0,
                "usage_by_model": {}
            }

        def get_session_summary(self, session_id: str) -> Dict[str, Any]:
            return {
                "session_id": session_id,
                "start_time": "mock-timestamp",
                "total_tokens": 0,
                "total_cost": 0.0
            }

    pricing_integration = MockPricingIntegration()

    # Define mock functions for pricing
    async def check_request_authorization(**kwargs):
        return {"authorized": True, "details": {}}

    async def track_request_cost(**kwargs):
        return {"status": "success", "cost": 0.01}


# Token usage estimate endpoint
@pricing_router.post("/api/estimate-tokens")
async def estimate_tokens(request: TokenEstimateRequest):
    """Estimate token usage and costs for a request"""
    # Simple token estimation logic
    estimated_tokens = len(request.prompt.split()) * 4  # Simple estimate

    # Get cost estimate if pricing is enabled
    cost_estimate = {"cost": 0, "details": {}}

    if request.userId:
        estimate = pricing_integration.estimate_request_cost(
            user_id=request.userId,
            model=request.model,
            estimated_tokens=estimated_tokens,
            request_type=request.requestType,
        )

        cost_estimate = {
            "cost": estimate["estimated_cost"],
            "tier": estimate["tier"],
            "has_sufficient_balance": estimate.get("has_sufficient_balance", True),
            "details": {
                "base_cost": estimate["cost_details"].get("base_cost", 0),
                "markup": estimate["cost_details"].get("markup_cost", 0),
                "discount": estimate["cost_details"].get("discount_amount", 0),
                "features": estimate["cost_details"].get("feature_costs", {}),
            },
        }

    return {
        "prompt_length": len(request.prompt),
        "estimated_tokens": estimated_tokens,
        "model": request.model,
        "requestType": request.requestType,
        "pricing_enabled": pricing_integration.pricing_enabled,
        "cost_estimate": cost_estimate,
    }


# Pricing toggle endpoint (admin only)
@pricing_router.post("/api/admin/pricing/toggle")
async def toggle_pricing(request: PricingToggleRequest):
    """Toggle pricing functionality (admin only)"""
    # In a real system, you would add authentication/authorization here
    prev_state = pricing_integration.pricing_enabled
    pricing_integration.pricing_enabled = request.enabled

    logger.info(
        f"Pricing {'enabled' if request.enabled else 'disabled'}, reason: {request.reason}"
    )

    return {
        "status": "success",
        "pricing_enabled": pricing_integration.pricing_enabled,
        "previous_state": prev_state,
        "message": f"Pricing has been {'enabled' if request.enabled else 'disabled'}",
    }


# User account management endpoints
@pricing_router.post("/api/user/create")
async def create_user(request: UserAccountRequest):
    """Create a new user account"""
    result = pricing_integration.create_user_account(
        user_id=request.userId,
        tier=request.tier,
        initial_balance=request.initialBalance,
    )

    if "error" in result:
        return JSONResponse(
            status_code=400, content={"status": "error", "message": result["error"]}
        )

    return {"status": "success", "user": result}


@pricing_router.post("/api/user/add-funds")
async def add_funds(request: AddFundsRequest):
    """Add funds to a user account"""
    result = pricing_integration.add_funds(
        user_id=request.userId, amount=request.amount, description=request.description
    )

    if "error" in result:
        return JSONResponse(
            status_code=400, content={"status": "error", "message": result["error"]}
        )

    return {"status": "success", "transaction": result}


@pricing_router.get("/api/user/{user_id}/balance")
async def get_user_balance(user_id: str):
    """Get the current balance for a user"""
    result = pricing_integration.check_balance(user_id)

    if "error" in result:
        return JSONResponse(
            status_code=404, content={"status": "error", "message": result["error"]}
        )

    return {"status": "success", "balance": result}


@pricing_router.get("/api/user/{user_id}/usage")
async def get_user_usage(user_id: str):
    """Get usage summary for a user"""
    result = pricing_integration.get_user_usage_summary(user_id)

    if "error" in result and "No usage data" not in result["error"]:
        return JSONResponse(
            status_code=404, content={"status": "error", "message": result["error"]}
        )

    return {"status": "success", "usage": result}


@pricing_router.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get details for a specific session"""
    result = pricing_integration.get_session_summary(session_id)

    if "error" in result:
        return JSONResponse(
            status_code=404, content={"status": "error", "message": result["error"]}
        )

    return {"status": "success", "session": result}


# Background tasks
async def track_token_usage_background(
    user_id: str,
    model: str,
    token_count: int,
    request_type: str = "completion",
    session_id: Optional[str] = None,
):
    """Background task to track token usage"""
    if callable(track_request_cost):
        await track_request_cost(
            price_integration=pricing_integration,
            user_id=user_id,
            model=model,
            token_count=token_count,
            request_type=request_type,
            session_id=session_id,
        )