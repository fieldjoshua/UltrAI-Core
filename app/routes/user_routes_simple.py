"""
Simple user routes without financial features.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional


# Placeholder authentication
class User(BaseModel):
    user_id: str
    is_admin: bool = False


def get_current_user() -> User:
    # In production, replace with real authentication
    return User(user_id="demo_user", is_admin=False)


def create_router() -> APIRouter:
    """
    Create the router with basic user endpoints only.
    
    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["User"])

    @router.get("/user/profile")
    async def get_profile(user: User = Depends(get_current_user)):
        """Get the user's profile."""
        return {
            "user_id": user.user_id,
            "is_admin": user.is_admin,
            "status": "active"
        }

    @router.get("/user/usage")
    async def get_usage_summary(user: User = Depends(get_current_user)):
        """Get the user's usage summary (queries only, no costs)."""
        # For now, return mock data
        return {
            "user_id": user.user_id,
            "total_queries": 0,
            "models_used": [],
            "last_query": None
        }

    return router


user_router = create_router()  # Expose router for application