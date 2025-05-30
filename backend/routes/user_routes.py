"""
User routes for the Ultra backend.

This module provides API routes for user management and authentication.
"""

import logging
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from backend.services.auth_service import auth_service

# Create a router
user_router = APIRouter(tags=["Users"])

# Configure logging
logger = logging.getLogger("user_routes")


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> Optional[str]:
    """
    Dependency to get the current user ID from the authorization header
    Returns None if no valid token is provided
    """
    if not authorization:
        return None

    # Extract token from header (Bearer token)
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None

    # Verify token
    user_id = auth_service.verify_token(token)
    return user_id


# Use Annotated for dependency injection to avoid linter warnings
CurrentUser = Annotated[Optional[str], Depends(get_current_user)]


@user_router.post("/api/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # If no user_id provided, generate one
        if not user.user_id:
            user.user_id = str(uuid4())

        result = auth_service.create_user(
            db=db,
            email=user.email,
            password=user.password,
            username=user.username,
            name=user.name,
            tier=user.tier,
        )

        if "error" in result:
            return JSONResponse(
                status_code=400, content={"status": "error", "message": result["error"]}
            )

        return result
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")


@user_router.post("/api/login", response_model=TokenResponse)
async def login_user(login: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return an access token"""
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, login.email, login.password)

        if not user:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Invalid email or password"},
            )

        # Create access token
        token = auth_service.create_access_token(user.id)

        if "error" in token:
            return JSONResponse(
                status_code=500, content={"status": "error", "message": token["error"]}
            )

        return token
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")


@user_router.get("/api/user/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser, db: Session = Depends(get_db)
):
    """Get the profile of the currently authenticated user"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Authentication required"},
        )

    try:
        # Convert user_id to int (it's stored as string in the token)
        user_id = int(current_user)
    except ValueError:
        return JSONResponse(
            status_code=400, content={"status": "error", "message": "Invalid user ID"}
        )

    user = auth_service.get_user(db, user_id)

    if not user:
        return JSONResponse(
            status_code=404, content={"status": "error", "message": "User not found"}
        )

    # Convert SQLAlchemy model to Pydantic response
    return {
        "user_id": str(user.id),
        "email": user.email,
        "username": user.username,
        "name": user.full_name,
        "tier": user.subscription_tier.value,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "balance": user.account_balance,
        "settings": {},  # This would come from a settings table
        "is_verified": user.is_verified,
        "oauth_provider": user.oauth_provider,
    }


@user_router.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str, current_user: CurrentUser, db: Session = Depends(get_db)
):
    """Get a user profile by ID (requires authentication)"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Authentication required"},
        )

    # In a real app, you might check permissions here
    # (e.g., only admins can view other user profiles)

    try:
        # Convert user_id string to int
        user_id_int = int(user_id)
    except ValueError:
        return JSONResponse(
            status_code=400, content={"status": "error", "message": "Invalid user ID"}
        )

    user = auth_service.get_user(db, user_id_int)

    if not user:
        return JSONResponse(
            status_code=404, content={"status": "error", "message": "User not found"}
        )

    # Convert SQLAlchemy model to Pydantic response
    return {
        "user_id": str(user.id),
        "email": user.email,
        "username": user.username,
        "name": user.full_name,
        "tier": user.subscription_tier.value,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "balance": user.account_balance,
        "settings": {},  # This would come from a settings table
        "is_verified": user.is_verified,
        "oauth_provider": user.oauth_provider,
    }


@user_router.put("/api/user/me", response_model=UserResponse)
async def update_user_profile(user_update: UserUpdate, current_user: CurrentUser):
    """Update the current user's profile"""
    if not current_user:
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Authentication required"},
        )

    result = auth_service.update_user(
        user_id=current_user, **user_update.dict(exclude_unset=True)
    )

    if "error" in result:
        return JSONResponse(
            status_code=400, content={"status": "error", "message": result["error"]}
        )

    return result
