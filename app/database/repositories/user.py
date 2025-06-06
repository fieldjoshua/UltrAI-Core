"""
User repository for the Ultra backend.

This module provides a repository for user-related database operations.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.database.models.user import User, UserRole
from backend.database.repositories.base import BaseRepository
from backend.utils.exceptions import ResourceAlreadyExistsException
from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("database.repository.user", "logs/database.log")


class UserRepository(BaseRepository[User]):
    """Repository for user operations"""

    def __init__(self):
        """Initialize the repository with the User model"""
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get a user by email

        Args:
            db: Database session
            email: User email

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Get a user by username

        Args:
            db: Database session
            username: Username

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, data: Dict) -> User:
        """
        Create a new user, checking for existing email/username

        Args:
            db: Database session
            data: User data

        Returns:
            Created user

        Raises:
            ResourceAlreadyExistsException: If a user with the same email or username exists
        """
        # Check if email already exists
        if self.get_by_email(db, data["email"]):
            raise ResourceAlreadyExistsException(
                resource_type="User",
                identifier=data["email"],
                message="A user with this email already exists",
            )

        # Check if username already exists (if provided)
        if data.get("username") and self.get_by_username(db, data["username"]):
            raise ResourceAlreadyExistsException(
                resource_type="User",
                identifier=data["username"],
                message="A user with this username already exists",
            )

        # Create the user
        return self.create(db, data)

    def get_by_oauth(self, db: Session, provider: str, oauth_id: str) -> Optional[User]:
        """
        Get a user by OAuth provider and ID

        Args:
            db: Database session
            provider: OAuth provider (e.g., "google", "github")
            oauth_id: OAuth user ID

        Returns:
            User if found, None otherwise
        """
        return (
            db.query(User)
            .filter(User.oauth_provider == provider, User.oauth_id == oauth_id)
            .first()
        )

    def get_admins(self, db: Session) -> List[User]:
        """
        Get all admin users

        Args:
            db: Database session

        Returns:
            List of admin users
        """
        return db.query(User).filter(User.role == UserRole.ADMIN).all()

    def get_active_users(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        Get active users with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active users
        """
        return (
            db.query(User)
            .filter(User.is_active.is_(True))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_subscription(
        self, db: Session, user_id: int, tier: str, expires_at=None
    ) -> User:
        """
        Update a user's subscription tier and expiration

        Args:
            db: Database session
            user_id: User ID
            tier: Subscription tier
            expires_at: Subscription expiration date

        Returns:
            Updated user

        Raises:
            ResourceNotFoundException: If the user is not found
        """
        user = self.get_by_id(db, user_id, raise_if_not_found=True)

        # Update subscription information
        return self.update(
            db,
            db_obj=user,
            obj_in={"subscription_tier": tier, "subscription_expires": expires_at},
        )

    def add_funds(self, db: Session, user_id: int, amount: float) -> User:
        """
        Add funds to a user's account balance

        Args:
            db: Database session
            user_id: User ID
            amount: Amount to add

        Returns:
            Updated user

        Raises:
            ResourceNotFoundException: If the user is not found
        """
        user = self.get_by_id(db, user_id, raise_if_not_found=True)

        # Update account balance, ensuring it's not None
        current_balance = (
            user.account_balance if user.account_balance is not None else 0.0
        )
        new_balance = current_balance + amount
        return self.update(db, db_obj=user, obj_in={"account_balance": new_balance})

    def deduct_funds(self, db: Session, user_id: int, amount: float) -> User:
        """
        Deduct funds from a user's account balance

        Args:
            db: Database session
            user_id: User ID
            amount: Amount to deduct

        Returns:
            Updated user

        Raises:
            ResourceNotFoundException: If the user is not found
        """
        user = self.get_by_id(db, user_id, raise_if_not_found=True)

        # Update account balance, ensuring it's not None
        current_balance = (
            user.account_balance if user.account_balance is not None else 0.0
        )
        new_balance = max(0.0, current_balance - amount)
        return self.update(db, db_obj=user, obj_in={"account_balance": new_balance})
