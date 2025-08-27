"""
Authentication service for user management.

This module provides user registration, login, and authentication functionality.
"""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.database.models.user import User, UserRole, SubscriptionTier
from app.models.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for user authentication and management."""
    
    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256", jwt_expiry_hours: int = 24):
        """
        Initialize authentication service.
        
        Args:
            jwt_secret: Secret key for JWT encoding
            jwt_algorithm: Algorithm for JWT encoding
            jwt_expiry_hours: JWT token expiry in hours
        """
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.jwt_expiry_hours = jwt_expiry_hours
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def create_access_token(self, user_id: int, email: str, role: str) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: User ID
            email: User email
            role: User role
            
        Returns:
            JWT token
        """
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def decode_access_token(self, token: str) -> Optional[dict]:
        """
        Decode and verify a JWT access token.
        
        Args:
            token: JWT token
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    async def register_user(self, db: Session, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If email or username already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if username already exists (if provided)
        if user_data.username:
            existing_username = db.query(User).filter(
                User.username == user_data.username
            ).first()
            if existing_username:
                raise ValueError("Username already taken")
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=self.hash_password(user_data.password),
            role=UserRole.USER,
            subscription_tier=SubscriptionTier.FREE,
            account_balance=0.0,
            is_verified=False,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"New user registered: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role.value,
            subscription_tier=user.subscription_tier.value,
            account_balance=user.account_balance,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )
    
    async def login_user(self, db: Session, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and return access token.
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            Access token and user info
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email or username
        user = db.query(User).filter(
            (User.email == login_data.email_or_username) |
            (User.username == login_data.email_or_username)
        ).first()
        
        if not user:
            raise ValueError("Invalid email/username or password")
        
        # Verify password
        if not self.verify_password(login_data.password, user.hashed_password):
            raise ValueError("Invalid email/username or password")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = self.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.jwt_expiry_hours * 3600,
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role=user.role.value,
                subscription_tier=user.subscription_tier.value,
                account_balance=user.account_balance,
                is_verified=user.is_verified,
                created_at=user.created_at,
            )
        )
    
    async def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """
        Get current user from access token.
        
        Args:
            db: Database session
            token: JWT access token
            
        Returns:
            User if token is valid, None otherwise
        """
        payload = self.decode_access_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        return user
    
    async def update_user_balance(
        self, 
        db: Session, 
        user_id: int, 
        amount: float, 
        operation: str = "add"
    ) -> float:
        """
        Update user account balance.
        
        Args:
            db: Database session
            user_id: User ID
            amount: Amount to add or subtract
            operation: "add" or "subtract"
            
        Returns:
            New balance
            
        Raises:
            ValueError: If insufficient balance for subtraction
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        if operation == "add":
            user.account_balance += amount
        elif operation == "subtract":
            if user.account_balance < amount:
                raise ValueError("Insufficient balance")
            user.account_balance -= amount
        else:
            raise ValueError("Invalid operation")
        
        db.commit()
        
        logger.info(f"User {user_id} balance updated: {operation} ${amount:.2f}")
        
        return user.account_balance