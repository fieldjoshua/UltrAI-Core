"""
Authentication dependencies for FastAPI routes.

This module provides reusable dependencies for authentication and authorization.
"""

import os
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.models.user import User, UserRole
from app.database.session import get_db
from app.services.auth_service_new import AuthService
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Security scheme for JWT bearer tokens
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    return AuthService(jwt_secret=jwt_secret)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from Authorization header
        db: Database session
        auth_service: Authentication service
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    user = await auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    This dependency doesn't require authentication but returns the user if authenticated.
    
    Args:
        credentials: Optional bearer token
        db: Database session
        auth_service: Authentication service
        
    Returns:
        Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_current_user(db, credentials.credentials)
        return user
    except Exception:
        return None


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_super_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify super admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Super admin user
        
    Raises:
        HTTPException: If user is not a super admin
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    return current_user


# Backward-compatible alias expected by some routes
# Old name: get_current_admin_user → now aliases to get_admin_user
get_current_admin_user = get_admin_user

class RateLimitDependency:
    """
    Rate limiting dependency based on user tier.
    
    This is a placeholder for actual rate limiting implementation.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
    
    async def __call__(self, current_user: Optional[User] = Depends(get_current_user_optional)):
        """Check rate limit for current user."""
        # TODO: Implement actual rate limiting
        # For now, just return without limiting
        pass


# Pre-configured rate limiters for different tiers
rate_limit_free = RateLimitDependency(requests_per_minute=10)
rate_limit_basic = RateLimitDependency(requests_per_minute=60)
rate_limit_premium = RateLimitDependency(requests_per_minute=300)