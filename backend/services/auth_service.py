"""
Authentication service for the Ultra backend.

This module provides a comprehensive service for user authentication, including
registration, login, token management, API key handling, and password reset functionality.
"""

import base64
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import jwt
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models.user import ApiKey, SubscriptionTier, User
from backend.database.repositories.user import UserRepository
from backend.models.auth import TokenResponse, UserCreate
from backend.utils.exceptions import AuthenticationException
from backend.utils.logging import get_logger
from backend.utils.password import check_password_strength, verify_password

# Configure logging
logger = get_logger("auth_service", "logs/auth.log")

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key_change_in_production")
JWT_REFRESH_SECRET = os.getenv(
    "JWT_REFRESH_SECRET", "refresh_secret_key_change_in_production"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(
    os.getenv("JWT_EXPIRATION_MINUTES", "15")
)  # 15 minutes by default
JWT_REFRESH_DAYS = int(os.getenv("JWT_REFRESH_DAYS", "7"))  # 7 days by default


class AuthService:
    """Service for handling user authentication and token management"""

    def __init__(self, user_repository: Optional[UserRepository] = None):
        """
        Initialize the authentication service

        Args:
            user_repository: User repository instance (created if not provided)
        """
        self.user_repository = user_repository or UserRepository()
        logger.info("Authentication service initialized")

    def create_user(
        self,
        db: Session,
        email: str,
        password: str,
        username: Optional[str] = None,
        name: Optional[str] = None,
        tier: str = "basic",
        auto_verify: bool = False,
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
            auto_verify: Whether to automatically verify the user's email

        Returns:
            Dict with user data or error message
        """
        try:
            # Check if email already exists
            if self.user_repository.get_by_email(db, email):
                logger.warning(
                    f"Registration failed: Email {email} is already registered"
                )
                return {"error": f"Email {email} is already registered"}

            # Check if username already exists
            if username and self.user_repository.get_by_username(db, username):
                logger.warning(
                    f"Registration failed: Username {username} is already taken"
                )
                return {"error": f"Username {username} is already taken"}

            # Check password strength
            is_strong, error_message = check_password_strength(password)
            if not is_strong:
                logger.warning(
                    f"Registration failed: Password not strong enough - {error_message}"
                )
                return {"error": error_message}

            # Hash the password
            hashed_password = pwd_context.hash(password)

            # Create the user
            user_data = {
                "email": email,
                "username": username,
                "full_name": name,
                "hashed_password": hashed_password,
                "subscription_tier": SubscriptionTier.BASIC if tier == "basic" else tier,
                "is_verified": auto_verify,  # Require email verification
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "account_balance": 0.0,
                "last_login": datetime.utcnow() if auto_verify else None,
            }

            user = self.user_repository.create_user(db, user_data)

            # Return user info (excluding password)
            logger.info(f"User registered successfully: {user.email}")
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
    ) -> Tuple[Optional[User], Optional[TokenResponse]]:
        """
        Authenticate a user and generate tokens

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            Tuple of (user, token_response) if authenticated, (None, None) otherwise
        """
        # Find user by email
        user = self.user_repository.get_by_email(db, email)

        if not user:
            logger.warning(f"Authentication failed: User not found with email {email}")
            return None, None

        # Verify password
        if not pwd_context.verify(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for user {email}")
            return None, None

        # Skip is_active check - User model doesn't have this field

        # Update last login time
        user = self.user_repository.update(
            db, db_obj=user, obj_in={"last_login": datetime.utcnow()}
        )

        # Generate tokens
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        token_response = TokenResponse(
            status="success",
            access_token=access_token["access_token"],
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_MINUTES * 60,  # seconds
        )

        logger.info(f"User authenticated successfully: {user.email}")
        return user, token_response

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        return self.user_repository.get_by_id(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email

        Args:
            db: Database session
            email: User email

        Returns:
            User if found, None otherwise
        """
        return self.user_repository.get_by_email(db, email)

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
            "type": "access",
            "jti": secrets.token_hex(8),  # Add unique token ID
        }

        # Create token
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": JWT_EXPIRATION_MINUTES * 60,  # seconds
            "user_id": user_id,
        }

    def create_refresh_token(self, user_id: Union[int, str]) -> str:
        """
        Create a JWT refresh token for the user

        Args:
            user_id: User ID

        Returns:
            Refresh token string
        """
        # Ensure user_id is a string for JWT
        user_id = str(user_id)

        # Define token expiration
        expires_at = datetime.utcnow() + timedelta(days=JWT_REFRESH_DAYS)

        # Define token payload
        payload = {
            "sub": user_id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_hex(8),  # Add unique token ID
        }

        # Create token
        token = jwt.encode(payload, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return the payload if valid

        Args:
            token: JWT token

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            # First try with access token secret
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                return payload
            except jwt.PyJWTError:
                # If that fails, try with refresh token secret
                try:
                    payload = jwt.decode(
                        token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM]
                    )
                    return payload
                except jwt.PyJWTError as e:
                    logger.error(f"Token verification error: {str(e)}")
                    return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            return None

    def verify_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a refresh token and return the payload if valid

        Args:
            refresh_token: Refresh token

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                refresh_token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM]
            )

            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                logger.warning("Invalid token type for refresh token")
                return None

            return payload
        except jwt.PyJWTError as e:
            logger.error(f"Refresh token verification error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying refresh token: {str(e)}")
            return None

    def refresh_tokens(
        self, db: Session, refresh_token: str
    ) -> Optional[TokenResponse]:
        """
        Refresh an access token using a refresh token

        Args:
            db: Database session
            refresh_token: Refresh token

        Returns:
            TokenResponse with new tokens if successful, None otherwise
        """
        # Validate refresh token
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            logger.warning("Token refresh failed: Invalid refresh token")
            return None

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token refresh failed: Missing user ID in token")
            return None

        # Check if user exists
        try:
            user_id_int = int(user_id)
        except ValueError:
            logger.warning(f"Token refresh failed: Invalid user ID format - {user_id}")
            return None

        user = self.get_user(db, user_id_int)
        if not user:
            logger.warning(f"Token refresh failed: User not found with ID {user_id}")
            return None

        # Skip is_active check - User model doesn't have this field

        # Generate new tokens
        access_token = self.create_access_token(user.id)
        new_refresh_token = self.create_refresh_token(user.id)

        token_response = TokenResponse(
            status="success",
            access_token=access_token["access_token"],
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_MINUTES * 60,  # seconds
        )

        logger.info(f"Tokens refreshed successfully for user {user.email}")
        return token_response

    async def get_current_user(self, token: str, db: Session = Depends(get_db)) -> User:
        """
        Get the current user from a token

        Args:
            token: JWT token
            db: Database session

        Returns:
            User if token is valid

        Raises:
            AuthenticationException: If authentication fails
        """
        payload = self.verify_token(token)
        if not payload:
            raise AuthenticationException(message="Invalid token")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException(message="Invalid token payload")

        # Convert user_id to int (it's stored as string in the token)
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise AuthenticationException(message="Invalid user ID")

        user = self.get_user(db, user_id_int)
        if not user:
            raise AuthenticationException(message="User not found")

        # Skip is_active check - User model doesn't have this field

        return user

    def change_password(
        self, db: Session, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """
        Change a user's password

        Args:
            db: Database session
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully, False otherwise

        Raises:
            ValueError: If the current password is invalid or the new password is not strong enough
        """
        # Get user
        user = self.user_repository.get_by_id(db, user_id, raise_if_not_found=True)

        # Verify current password
        if not pwd_context.verify(current_password, user.hashed_password):
            logger.warning(
                f"Password change failed: Invalid current password for user {user.email}"
            )
            return False

        # Check password strength
        is_strong, error_message = check_password_strength(new_password)
        if not is_strong:
            logger.warning(
                f"Password change failed: New password not strong enough - {error_message}"
            )
            raise ValueError(error_message)

        # Hash the new password
        hashed_password = pwd_context.hash(new_password)

        # Update user
        self.user_repository.update(
            db, db_obj=user, obj_in={"hashed_password": hashed_password}
        )

        logger.info(f"Password changed successfully for user {user.email}")
        return True

    def create_api_key(
        self, db: Session, user_id: int, name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create an API key for a user

        Args:
            db: Database session
            user_id: User ID
            name: API key name

        Returns:
            Dict with API key details if successful, None otherwise
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(db, user_id, raise_if_not_found=True)

            # Generate API key
            key_bytes = secrets.token_bytes(32)
            key = f"ultra_{base64.urlsafe_b64encode(key_bytes).decode('ascii')}"

            # Create API key
            api_key = ApiKey(
                user_id=user.id,
                name=name,
                key=key,
                created_at=datetime.utcnow(),
                is_active=True,
            )

            # Add to database
            db.add(api_key)
            db.commit()
            db.refresh(api_key)

            logger.info(f"API key '{name}' created for user {user.email}")

            # Return API key details
            return {
                "id": api_key.id,
                "name": api_key.name,
                "key": api_key.key,  # Only return key on creation
                "created_at": api_key.created_at.isoformat(),
                "is_active": api_key.is_active,
            }
        except Exception as e:
            logger.error(f"Error creating API key: {str(e)}")
            return None

    def get_api_keys(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all API keys for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of API key details
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(db, user_id, raise_if_not_found=True)

            # Get API keys
            api_keys = db.query(ApiKey).filter(ApiKey.user_id == user.id).all()

            # Return API key details (excluding the actual key)
            return [
                {
                    "id": api_key.id,
                    "name": api_key.name,
                    "created_at": api_key.created_at.isoformat(),
                    "last_used_at": (
                        api_key.last_used_at.isoformat()
                        if api_key.last_used_at
                        else None
                    ),
                    "is_active": api_key.is_active,
                }
                for api_key in api_keys
            ]
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            return []

    def revoke_api_key(self, db: Session, key_id: int, user_id: int) -> bool:
        """
        Revoke an API key

        Args:
            db: Database session
            key_id: API key ID
            user_id: User ID (for authorization)

        Returns:
            True if key revoked successfully, False otherwise
        """
        try:
            # Get API key
            api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
            if not api_key:
                logger.warning(f"API key revocation failed: Key {key_id} not found")
                return False

            # Check if key belongs to user
            if api_key.user_id != user_id:
                logger.warning(
                    f"API key revocation failed: Key {key_id} doesn't belong to user {user_id}"
                )
                return False

            # Revoke key
            api_key.is_active = False
            db.add(api_key)
            db.commit()

            logger.info(f"API key '{api_key.name}' revoked for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error revoking API key: {str(e)}")
            return False

    def verify_api_key(self, db: Session, key: str) -> Optional[User]:
        """
        Verify an API key and return the associated user

        Args:
            db: Database session
            key: API key

        Returns:
            User if key is valid, None otherwise
        """
        try:
            # Get API key
            api_key = (
                db.query(ApiKey)
                .filter(ApiKey.key == key, ApiKey.is_active.is_(True))
                .first()
            )
            if not api_key:
                logger.warning(
                    f"API key verification failed: Key not found or inactive"
                )
                return None

            # Update last used timestamp
            api_key.last_used_at = datetime.utcnow()
            db.add(api_key)
            db.commit()

            # Get user
            user = self.user_repository.get_by_id(db, api_key.user_id)
            if not user:
                logger.warning(
                    f"API key verification failed: User {api_key.user_id} not found"
                )
                return None

            logger.info(f"API key '{api_key.name}' verified for user {user.email}")
            return user
        except Exception as e:
            logger.error(f"Error verifying API key: {str(e)}")
            return None

    def update_user_profile(
        self, db: Session, user_id: int, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a user's profile

        Args:
            db: Database session
            user_id: User ID
            profile_data: Profile data to update

        Returns:
            Dict with updated user data or error message
        """
        try:
            # Get user
            user = self.user_repository.get_by_id(db, user_id, raise_if_not_found=True)

            # Filter out sensitive fields
            safe_profile_data = {
                k: v
                for k, v in profile_data.items()
                if k in ["full_name", "username", "email"]
            }

            # Special handling for email updates
            if "email" in safe_profile_data:
                # Check if email already exists
                existing_user = self.user_repository.get_by_email(
                    db, safe_profile_data["email"]
                )
                if existing_user and existing_user.id != user_id:
                    return {
                        "error": f"Email {safe_profile_data['email']} is already registered"
                    }

            # Special handling for username updates
            if "username" in safe_profile_data:
                # Check if username already exists
                existing_user = self.user_repository.get_by_username(
                    db, safe_profile_data["username"]
                )
                if existing_user and existing_user.id != user_id:
                    return {
                        "error": f"Username {safe_profile_data['username']} is already taken"
                    }

            # Update user
            updated_user = self.user_repository.update(
                db, db_obj=user, obj_in=safe_profile_data
            )

            # Return updated user info
            return {
                "user_id": updated_user.id,
                "email": updated_user.email,
                "username": updated_user.username,
                "name": updated_user.full_name,
                "tier": updated_user.subscription_tier.value,
                "updated_at": updated_user.updated_at.isoformat(),
                "is_verified": updated_user.is_verified,
            }
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return {"error": f"Error updating user profile: {str(e)}"}


# Create a global instance
auth_service = AuthService()
