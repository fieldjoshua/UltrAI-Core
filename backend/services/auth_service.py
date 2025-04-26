"""
Authentication service for the Ultra backend.

This module provides the service for user authentication and token generation.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models.user import User
from backend.database.repositories.user import UserRepository
from backend.utils.exceptions import AuthenticationException

# Configure logging
logger = logging.getLogger("auth_service")

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(
    os.getenv("JWT_EXPIRATION_MINUTES", "60")
)  # 1 hour by default


class AuthService:
    """Service for handling user authentication and token management"""

    def __init__(self):
        """Initialize the authentication service"""
        self.user_repository = UserRepository()

    def create_user(
        self,
        db: Session,
        email: str,
        password: str,
        username: Optional[str] = None,
        name: Optional[str] = None,
        tier: str = "basic",
    ) -> Dict[str, Any]:
        """
        Create a new user

        Args:
            db: Database session
            email: User email
            password: User password
            username: User username
            name: User's full name
            tier: Subscription tier

        Returns:
            Dict with user data or error message
        """
        try:
            # Check if email already exists
            if self.user_repository.get_by_email(db, email):
                return {"error": f"Email {email} is already registered"}

            # Check if username already exists
            if username and self.user_repository.get_by_username(db, username):
                return {"error": f"Username {username} is already taken"}

            # Hash the password
            hashed_password = pwd_context.hash(password)

            # Create the user
            user_data = {
                "email": email,
                "username": username,
                "full_name": name,
                "hashed_password": hashed_password,
                "subscription_tier": tier,
                "is_active": True,
                "is_verified": False,  # Require email verification
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "account_balance": 0.0,
            }

            user = self.user_repository.create(db, user_data)

            # Return user info (excluding password)
            return {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "name": user.full_name,
                "tier": user.subscription_tier.value,
                "created_at": user.created_at.isoformat(),
                "is_verified": user.is_verified,
            }
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {"error": f"Error creating user: {str(e)}"}

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            User if authentication succeeds, None otherwise
        """
        # Find user by email
        user = self.user_repository.get_by_email(db, email)

        if not user:
            return None

        # Verify password
        if not pwd_context.verify(password, user.hashed_password):
            return None

        # Check if user is active
        if not user.is_active:
            return None

        # Update last login time
        self.user_repository.update(
            db, db_obj=user, obj_in={"last_login": datetime.utcnow()}
        )

        return user

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        return self.user_repository.get(db, user_id)

    def create_access_token(self, user_id: Union[int, str]) -> Dict[str, Any]:
        """
        Create a JWT access token for the user

        Args:
            user_id: User ID

        Returns:
            Dict with token data
        """
        # Ensure user_id is a string for JWT
        user_id = str(user_id)

        # Define token expiration
        expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

        # Define token payload
        payload = {
            "sub": user_id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
        }

        # Create token
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_MINUTES * 60,  # seconds
            "user_id": user_id,
        }

    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify a JWT token and return the user ID if valid

        Args:
            token: JWT token

        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            return user_id
        except jwt.PyJWTError as e:
            logger.error(f"Token verification error: {str(e)}")
            return None

    async def get_current_user(
        self, token: str, db: Session = Depends(get_db)
    ) -> Optional[User]:
        """
        Get the current user from a token

        Args:
            token: JWT token
            db: Database session

        Returns:
            User if token is valid, None otherwise

        Raises:
            AuthenticationException: If authentication fails
        """
        user_id = self.verify_token(token)
        if not user_id:
            raise AuthenticationException(message="Invalid token")

        # Convert user_id to int (it's stored as string in the token)
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise AuthenticationException(message="Invalid user ID")

        user = self.get_user(db, user_id_int)
        if not user:
            raise AuthenticationException(message="User not found")

        if not user.is_active:
            raise AuthenticationException(message="User account is disabled")

        return user


# Create a global instance
auth_service = AuthService()
