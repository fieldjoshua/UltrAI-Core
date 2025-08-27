"""
Authentication route handlers for the Ultra backend.

This module provides endpoints for user registration, login, and authentication.
"""

import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models.user import User
from app.models.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service_new import AuthService
from app.middleware.auth_dependencies import get_current_user, get_auth_service
from app.utils.logging import get_logger

logger = get_logger(__name__)


# Remove duplicate - now imported from auth_dependencies


def create_router() -> APIRouter:
    """
    Create the router with all auth endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Auth"])
    
    @router.post("/register", response_model=UserResponse)
    async def register(
        user_data: UserCreate,
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(get_auth_service)
    ):
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            db: Database session
            auth_service: Authentication service
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If registration fails
        """
        try:
            user = await auth_service.register_user(db, user_data)
            return user
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    @router.post("/login", response_model=TokenResponse)
    async def login(
        login_data: UserLogin,
        db: Session = Depends(get_db),
        auth_service: AuthService = Depends(get_auth_service)
    ):
        """
        Login user and return access token.
        
        Args:
            login_data: Login credentials
            db: Database session
            auth_service: Authentication service
            
        Returns:
            Access token and user info
            
        Raises:
            HTTPException: If login fails
        """
        try:
            token_response = await auth_service.login_user(db, login_data)
            return token_response
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    @router.get("/me", response_model=UserResponse)
    async def get_me(
        current_user: User = Depends(get_current_user)
    ):
        """
        Get current user information.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Current user information
        """
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.full_name,
            role=current_user.role.value,
            subscription_tier=current_user.subscription_tier.value,
            account_balance=current_user.account_balance,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at,
        )

    return router


auth_router = create_router()  # Expose router for application