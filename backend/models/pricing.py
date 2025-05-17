from typing import Optional

from pydantic import BaseModel


class TokenEstimateRequest(BaseModel):
    """Request model for token estimation"""

    prompt: str
    model: str
    requestType: str
    userId: Optional[str] = None


class PricingToggleRequest(BaseModel):
    """Request model for toggling pricing functionality"""

    enabled: bool
    reason: str


class UserAccountRequest(BaseModel):
    """Request model for creating user accounts"""

    userId: str
    tier: str
    initialBalance: float


class AddFundsRequest(BaseModel):
    """Request model for adding funds to a user account"""

    userId: str
    amount: float
    description: str = "Account deposit"
