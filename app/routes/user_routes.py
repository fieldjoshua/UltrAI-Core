"""
Route handlers for the Ultra backend.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.transaction_service import TransactionService
from app.services.token_management_service import TokenManagementService

# For demonstration, use singleton instances (replace with DI in production)
transaction_service = TransactionService()
token_management_service = TokenManagementService()


# Placeholder authentication and admin check
class User(BaseModel):
    user_id: str
    is_admin: bool = False


def get_current_user() -> User:
    # In production, replace with real authentication
    return User(user_id="test_user", is_admin=True)


def admin_required(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


# Request models
class AddFundsRequest(BaseModel):
    amount: float
    description: Optional[str] = "User deposit"


class ManualDebitRequest(BaseModel):
    user_id: str
    amount: float
    description: Optional[str] = "Manual debit"


class RefundRequest(BaseModel):
    user_id: str
    amount: float
    description: Optional[str] = "Refund"


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["User"])

    @router.get("/user/balance", response_model=float)
    async def get_balance(user: User = Depends(get_current_user)):
        """Get the user's current balance."""
        return await transaction_service.get_balance(user.user_id)

    @router.get("/user/transactions")
    async def get_transaction_history(user: User = Depends(get_current_user)):
        """Get the user's transaction history."""
        history = transaction_service.get_transaction_history(user.user_id)
        return [t.__dict__ for t in history]

    @router.get("/user/token-usage")
    async def get_token_usage(user: User = Depends(get_current_user)):
        """Get the user's token usage history."""
        usage = token_management_service.get_user_usage(user.user_id)
        return [
            {
                "model": t.model,
                "input_tokens": t.input_tokens,
                "output_tokens": t.output_tokens,
                "input_cost_per_1k": t.input_cost_per_1k,
                "output_cost_per_1k": t.output_cost_per_1k,
                "timestamp": t.timestamp,
                "total_cost": t.total_cost,
            }
            for t in usage
        ]

    @router.post("/user/add-funds")
    async def add_funds(
        request: AddFundsRequest, user: User = Depends(get_current_user)
    ):
        """Add funds to the user's account."""
        transaction = await transaction_service.add_funds(
            user_id=user.user_id,
            amount=request.amount,
            description=request.description or "User deposit",
        )
        return transaction.__dict__

    @router.post("/admin/manual-debit")
    async def manual_debit(
        request: ManualDebitRequest, admin: User = Depends(get_current_user)
    ):
        admin_required(admin)
        """Manually debit a user's account (admin only)."""
        transaction = await transaction_service.deduct_cost(
            user_id=request.user_id,
            amount=request.amount,
            description=request.description or "Manual debit",
        )
        if transaction is None:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        return transaction.__dict__

    @router.post("/admin/refund")
    async def refund(request: RefundRequest, admin: User = Depends(get_current_user)):
        admin_required(admin)
        """Refund a user (admin only)."""
        # Refund is implemented as a credit
        transaction = await transaction_service.add_funds(
            user_id=request.user_id,
            amount=request.amount,
            description=request.description or "Refund",
        )
        return transaction.__dict__

    return router
