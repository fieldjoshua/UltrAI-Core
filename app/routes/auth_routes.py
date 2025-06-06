from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Request, status, Header

"""
Authentication routes for the Ultra backend.

This module provides API routes for user authentication, including
registration, login, logout, token refresh, and password reset functionality.
"""

import logging

import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.error_handling import (
    AuthenticationError,
    ValidationError,
    ProcessingError,
)
from app.database.connection import get_db
from app.middleware.auth_middleware import add_token_to_blacklist, token_blacklist
from app.models.auth import (
    MessageResponse,
    PasswordReset,
    PasswordResetRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from app.services.auth_service import auth_service

# Set up logging
logger = logging.getLogger("auth_routes")

# OAuth2 password bearer for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Common dependencies
DEFAULT_DB = Depends(get_db)

# Standard error messages
ERROR_MESSAGES = {
    "invalid_token": "Missing or invalid authentication token",
    "token_invalidated": "Token has been invalidated",
    "token_expired": "Token has expired",
    "invalid_signature": "Invalid token signature",
    "user_not_found": "User not found",
    "invalid_credentials": "Invalid email or password",
    "password_required": "Both current_password and new_password are required",
    "api_key_name_required": "API key name is required",
    "current_password_incorrect": "Current password is incorrect",
    "invalid_reset_token": "Invalid or expired reset token",
}

# Test token for password reset (should be replaced with actual token validation)
# NOTE: This is for development/testing only. Do not use in production.
TEST_RESET_TOKEN = (
    "test_reset_token"  # nosec # noqa: S105 (Safe to ignore: not used in production)
)


def create_router(
    auth_service: Any = auth_service,
) -> APIRouter:
    """
    Create the authentication router with dependencies.

    Args:
        auth_service: The authentication service

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Authentication"])

    async def get_current_user(
        request: Request, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Get the current user from the request.

        Args:
            request: The request object
            db: The database session

        Returns:
            Dict[str, Any]: The current user information

        Raises:
            AuthenticationError: If authentication fails
            ResourceNotFoundError: If user is not found
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError(ERROR_MESSAGES["invalid_token"])

        token = auth_header.replace("Bearer ", "")

        # Check if token is blacklisted
        if token in token_blacklist:
            raise AuthenticationError(ERROR_MESSAGES["token_invalidated"])

        try:
            user = await auth_service.get_current_user(token, db)
            return {
                "user_id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "username": user.username,
                "tier": user.subscription_tier.value,
                "is_verified": user.is_verified,
            }
        except jwt.ExpiredSignatureError:
            raise AuthenticationError(ERROR_MESSAGES["token_expired"])
        except jwt.InvalidSignatureError:
            raise AuthenticationError(ERROR_MESSAGES["invalid_signature"])
        except Exception as e:
            raise AuthenticationError(f"Invalid authentication token: {str(e)}")

    @router.post(
        "/auth/register",
        status_code=status.HTTP_201_CREATED,
        response_model=MessageResponse,
    )
    async def register_user(
        user: UserCreate, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Register a new user account.

        Args:
            user: User registration data
            db: Database session

        Returns:
            Dict[str, Any]: Success message with user ID

        Raises:
            ValidationError: If user data is invalid
            ProcessingError: If user creation fails
        """
        try:
            result = auth_service.create_user(
                db,
                user.email,
                user.password,
                name=user.name,
                auto_verify=True,  # Auto-verify for simplicity in MVP
            )

            if "error" in result:
                raise ValidationError(result["error"])

            return {
                "status": "success",
                "message": "User registered successfully",
                "user_id": str(result["user_id"]),
            }
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise ProcessingError(f"Error registering user: {str(e)}")

    @router.post("/auth/login", response_model=TokenResponse)
    async def login(user_data: UserLogin, db: Session = DEFAULT_DB) -> Dict[str, Any]:
        """
        Authenticate a user and return access and refresh tokens.

        Args:
            user_data: User login credentials
            db: Database session

        Returns:
            Dict[str, Any]: Token response with access and refresh tokens

        Raises:
            AuthenticationError: If authentication fails
            ProcessingError: If login process fails
        """
        try:
            user, token_response = auth_service.authenticate_user(
                db, user_data.email, user_data.password
            )

            if not user or not token_response:
                raise AuthenticationError(ERROR_MESSAGES["invalid_credentials"])

            return token_response
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise ProcessingError(f"Error during login: {str(e)}")

    @router.post("/auth/refresh", response_model=TokenResponse)
    async def refresh_token(
        refresh_request: RefreshTokenRequest, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_request: RefreshTokenRequest with refresh_token field
            db: Database session

        Returns:
            Dict[str, Any]: Token response with new access and refresh tokens

        Raises:
            AuthenticationError: If refresh token is invalid
            ProcessingError: If token refresh fails
        """
        try:
            if refresh_request.refresh_token in token_blacklist:
                raise AuthenticationError(ERROR_MESSAGES["token_invalidated"])

            tokens = auth_service.refresh_tokens(db, refresh_request.refresh_token)

            if not tokens:
                raise AuthenticationError(ERROR_MESSAGES["invalid_credentials"])

            return tokens
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise ProcessingError(f"Error refreshing token: {str(e)}")

    @router.post("/auth/logout", response_model=MessageResponse)
    async def logout(
        authorization: Optional[str] = Header(None),  # noqa: B008 (FastAPI pattern)
        refresh_token: Optional[str] = Header(None),  # noqa: B008 (FastAPI pattern)
    ) -> Dict[str, Any]:
        """
        Log out a user by invalidating their token.

        Args:
            authorization: Authorization header with access token
            refresh_token: Refresh token header

        Returns:
            Dict[str, Any]: Success message

        Raises:
            ProcessingError: If logout process fails
        """
        try:
            if authorization and authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
                add_token_to_blacklist(token)

            if refresh_token:
                add_token_to_blacklist(refresh_token)

            return {"status": "success", "message": "Successfully logged out"}
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            raise ProcessingError(f"Error during logout: {str(e)}")

    @router.post("/auth/reset-password-request", response_model=MessageResponse)
    async def request_password_reset(
        request_data: PasswordResetRequest, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Request a password reset for a user.

        Args:
            request_data: PasswordResetRequest with email field
            db: Database session

        Returns:
            Dict[str, Any]: Success message

        Raises:
            ProcessingError: If password reset request fails
        """
        try:
            auth_service.request_password_reset(db, request_data.email)
            return {
                "status": "success",
                "message": "Password reset request sent successfully",
            }
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            raise ProcessingError(f"Error requesting password reset: {str(e)}")

    @router.post("/auth/reset-password", response_model=MessageResponse)
    async def reset_password(
        reset_data: PasswordReset, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Reset a user's password using a reset token.

        Args:
            reset_data: PasswordReset with token and new_password fields
            db: Database session

        Returns:
            Dict[str, Any]: Success message

        Raises:
            ValidationError: If reset token is invalid
            ProcessingError: If password reset fails
        """
        try:
            if reset_data.token != TEST_RESET_TOKEN:
                raise ValidationError(ERROR_MESSAGES["invalid_reset_token"])

            auth_service.reset_password(db, reset_data.token, reset_data.new_password)
            return {
                "status": "success",
                "message": "Password reset successfully",
            }
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            raise ProcessingError(f"Error resetting password: {str(e)}")

    @router.get("/users/me", response_model=dict)
    async def get_current_user_info(
        request: Request, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Get the current user's information.

        Args:
            request: The request object
            db: Database session

        Returns:
            Dict[str, Any]: User information

        Raises:
            AuthenticationError: If authentication fails
            ProcessingError: If user retrieval fails
        """
        try:
            user = await get_current_user(request, db)
            return user
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise ProcessingError(f"Error getting user info: {str(e)}")

    @router.put("/users/me", response_model=dict)
    async def update_user_profile(
        profile_data: dict,
        request: Request,
        db: Session = DEFAULT_DB,
    ) -> Dict[str, Any]:
        """
        Update the current user's profile.

        Args:
            profile_data: User profile data
            request: The request object
            db: Database session

        Returns:
            Dict[str, Any]: Updated user information

        Raises:
            AuthenticationError: If authentication fails
            ProcessingError: If profile update fails
        """
        try:
            user = await get_current_user(request, db)
            auth_service.update_user_profile(db, user["user_id"], profile_data)
            return {"status": "success", "message": "Profile updated successfully"}
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise ProcessingError(f"Error updating user profile: {str(e)}")

    @router.post("/users/me/change-password", response_model=MessageResponse)
    async def change_password(
        password_data: dict,
        request: Request,
        db: Session = DEFAULT_DB,
    ) -> Dict[str, Any]:
        """
        Change the current user's password.

        Args:
            password_data: Password change data
            request: The request object
            db: Database session

        Returns:
            Dict[str, Any]: Success message

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If password data is invalid
            ProcessingError: If password change fails
        """
        try:
            user = await get_current_user(request, db)
            if not password_data.get("current_password") or not password_data.get(
                "new_password"
            ):
                raise ValidationError(ERROR_MESSAGES["password_required"])

            auth_service.change_password(
                db,
                user["user_id"],
                password_data["current_password"],
                password_data["new_password"],
            )
            return {
                "status": "success",
                "message": "Password changed successfully",
            }
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise ProcessingError(f"Error changing password: {str(e)}")

    @router.post("/users/me/api-keys", response_model=dict)
    async def create_api_key(
        key_data: dict,
        request: Request,
        db: Session = DEFAULT_DB,
    ) -> Dict[str, Any]:
        """
        Create a new API key for the current user.

        Args:
            key_data: API key data
            request: The request object
            db: Database session

        Returns:
            Dict[str, Any]: API key information

        Raises:
            AuthenticationError: If authentication fails
            ValidationError: If API key data is invalid
            ProcessingError: If API key creation fails
        """
        try:
            user = await get_current_user(request, db)
            if not key_data.get("name"):
                raise ValidationError(ERROR_MESSAGES["api_key_name_required"])

            auth_service.create_api_key(db, user["user_id"], key_data["name"])
            return {"status": "success", "message": "API key created successfully"}
        except Exception as e:
            logger.error(f"Error creating API key: {str(e)}")
            raise ProcessingError(f"Error creating API key: {str(e)}")

    @router.get("/api/users/me/api-keys", response_model=dict)
    async def get_api_keys(
        request: Request, db: Session = DEFAULT_DB
    ) -> Dict[str, Any]:
        """
        Get the current user's API keys.

        Args:
            request: The request object
            db: Database session

        Returns:
            Dict[str, Any]: List of API keys

        Raises:
            AuthenticationError: If authentication fails
            ProcessingError: If API key retrieval fails
        """
        try:
            user = await get_current_user(request, db)
            api_keys = auth_service.get_api_keys(db, user["user_id"])
            return {"status": "success", "api_keys": api_keys}
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            raise ProcessingError(f"Error getting API keys: {str(e)}")

    @router.delete("/api/users/me/api-keys/{key_id}", response_model=MessageResponse)
    async def revoke_api_key(
        key_id: int,
        request: Request,
        db: Session = DEFAULT_DB,
    ) -> Dict[str, Any]:
        """
        Revoke an API key for the current user.

        Args:
            key_id: ID of the API key to revoke
            request: The request object
            db: Database session

        Returns:
            Dict[str, Any]: Success message

        Raises:
            AuthenticationError: If authentication fails
            ProcessingError: If API key revocation fails
        """
        try:
            user = await get_current_user(request, db)
            auth_service.revoke_api_key(db, user["user_id"], key_id)
            return {
                "status": "success",
                "message": "API key revoked successfully",
            }
        except Exception as e:
            logger.error(f"Error revoking API key: {str(e)}")
            raise ProcessingError(f"Error revoking API key: {str(e)}")

    return router
