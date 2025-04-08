import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import jwt
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth_service")

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_key_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))  # 1 hour by default
USER_FILE = os.getenv("USER_FILE", "user_data.json")


class AuthService:
    """Service for handling user authentication and management"""

    def __init__(self, user_file: str = USER_FILE):
        """Initialize the authentication service"""
        self.user_file = user_file
        self.users = self._load_users()

    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from file"""
        if os.path.exists(self.user_file):
            try:
                with open(self.user_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading user data: {str(e)}")
                return {}
        return {}

    def _save_users(self) -> None:
        """Save users to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.user_file), exist_ok=True)
            with open(self.user_file, "w") as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")

    def create_user(
        self, user_id: str, email: str, password: str, name: Optional[str] = None, tier: str = "basic"
    ) -> Dict[str, Any]:
        """Create a new user"""
        # Check if user already exists
        if user_id in self.users:
            return {"error": f"User with ID {user_id} already exists"}

        # Check if email is already used
        for existing_user in self.users.values():
            if existing_user.get("email") == email:
                return {"error": f"Email {email} is already registered"}

        # Hash the password
        hashed_password = pwd_context.hash(password)

        # Create the user
        user = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "password_hash": hashed_password,
            "tier": tier,
            "created_at": datetime.now().isoformat(),
            "balance": 0.0,
            "settings": {}
        }

        # Save the user
        self.users[user_id] = user
        self._save_users()

        # Return user info (excluding password)
        return {k: v for k, v in user.items() if k != "password_hash"}

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user by email and password"""
        # Find user by email
        user = None
        for u in self.users.values():
            if u.get("email") == email:
                user = u
                break

        if not user:
            return None

        # Verify password
        if not pwd_context.verify(password, user["password_hash"]):
            return None

        # Update last login time
        user["last_login"] = datetime.now().isoformat()
        self._save_users()

        # Return user info (excluding password)
        return {k: v for k, v in user.items() if k != "password_hash"}

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = self.users.get(user_id)
        if not user:
            return None

        # Return user info (excluding password)
        return {k: v for k, v in user.items() if k != "password_hash"}

    def update_user(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """Update user information"""
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User with ID {user_id} not found"}

        user = self.users[user_id]

        # Update allowed fields
        allowed_fields = ["name", "email", "tier", "settings"]
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                user[field] = value

        # Special handling for password
        if "password" in kwargs and kwargs["password"]:
            user["password_hash"] = pwd_context.hash(kwargs["password"])

        # Save changes
        self._save_users()

        # Return updated user (excluding password)
        return {k: v for k, v in user.items() if k != "password_hash"}

    def create_access_token(self, user_id: str) -> Dict[str, Any]:
        """Create a JWT access token for the user"""
        # Check if user exists
        if user_id not in self.users:
            return {"error": f"User with ID {user_id} not found"}

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
            "user_id": user_id
        }

    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the user ID if valid"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")

            # Check if user exists
            if user_id not in self.users:
                return None

            return user_id
        except jwt.PyJWTError:
            return None


# Create a global instance
auth_service = AuthService()