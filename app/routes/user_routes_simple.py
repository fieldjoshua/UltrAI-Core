"""
Simple user routes without financial features.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.user import User, UserRole
from app.middleware.auth_dependencies import get_current_user
from app.services.analysis_storage_service import AnalysisStorageService
from app.utils.logging import get_logger

logger = get_logger(__name__)


def create_router() -> APIRouter:
    """
    Create the router with basic user endpoints only.
    
    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["User"])

    @router.get("/user/profile")
    async def get_profile(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Get the user's profile."""
        return {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role.value,
            "subscription_tier": current_user.subscription_tier.value,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "status": "active"
        }

    @router.get("/user/usage")
    async def get_usage_summary(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Get the user's usage summary (queries only, no costs)."""
        try:
            storage_service = AnalysisStorageService()
            usage_stats = await storage_service.get_user_usage_stats(db, current_user.id)
            
            return {
                "user_id": str(current_user.id),
                "total_queries": usage_stats.get("total_queries", 0),
                "completed_queries": usage_stats.get("completed_queries", 0),
                "models_used": usage_stats.get("models_used", []),
                "last_query": usage_stats.get("last_query"),
                "subscription_tier": current_user.subscription_tier.value
            }
        except Exception as e:
            logger.error(f"Failed to get usage stats for user {current_user.id}: {e}")
            # Fall back to basic info if storage fails
            return {
                "user_id": str(current_user.id),
                "total_queries": 0,
                "completed_queries": 0,
                "models_used": [],
                "last_query": None,
                "subscription_tier": current_user.subscription_tier.value,
                "error": "Unable to retrieve usage statistics"
            }

    return router


user_router = create_router()  # Expose router for application