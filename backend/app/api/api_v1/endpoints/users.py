from typing import List
from fastapi import Depends, HTTPException, status
from uuid import UUID

from app.api.api_v1.base import BaseRouter
from app.models.user import UserCreate, UserUpdate, UserResponse, UserBase
from app.core.exceptions import NotFoundError


class UserRouter(BaseRouter):
    """Router for user-related endpoints."""

    def __init__(self):
        super().__init__(prefix="/users", tags=["users"])

    @self.get("/", response_model=UserResponse)
    async def list_users(
        self,
        query: BaseQueryModel = Depends(self.get_query_params),
    ) -> UserResponse:
        """List all users with pagination and filtering."""
        # TODO: Implement actual database query
        users = [
            UserBase(
                email="test@example.com",
                username="testuser",
                full_name="Test User",
            )
        ]
        return self.create_response(
            data=users,
            message="Users retrieved successfully",
            metadata={
                "total": len(users),
                "page": query.page,
                "page_size": query.page_size,
            },
        )

    @self.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    async def create_user(
        self,
        user: UserCreate,
    ) -> UserResponse:
        """Create a new user."""
        # TODO: Implement actual user creation
        created_user = UserBase(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
        )
        return self.create_response(
            data=created_user,
            message="User created successfully",
        )

    @self.get("/{user_id}", response_model=UserResponse)
    async def get_user(
        self,
        user_id: UUID,
    ) -> UserResponse:
        """Get a user by ID."""
        # TODO: Implement actual database query
        if user_id != UUID("00000000-0000-0000-0000-000000000000"):
            raise NotFoundError(f"User with ID {user_id} not found")

        user = UserBase(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
        )
        return self.create_response(
            data=user,
            message="User retrieved successfully",
        )

    @self.put("/{user_id}", response_model=UserResponse)
    async def update_user(
        self,
        user_id: UUID,
        user: UserUpdate,
    ) -> UserResponse:
        """Update a user."""
        # TODO: Implement actual user update
        if user_id != UUID("00000000-0000-0000-0000-000000000000"):
            raise NotFoundError(f"User with ID {user_id} not found")

        updated_user = UserBase(
            email=user.email or "test@example.com",
            username=user.username or "testuser",
            full_name=user.full_name,
        )
        return self.create_response(
            data=updated_user,
            message="User updated successfully",
        )

    @self.delete("/{user_id}", response_model=UserResponse)
    async def delete_user(
        self,
        user_id: UUID,
    ) -> UserResponse:
        """Delete a user."""
        # TODO: Implement actual user deletion
        if user_id != UUID("00000000-0000-0000-0000-000000000000"):
            raise NotFoundError(f"User with ID {user_id} not found")

        return self.create_response(
            message="User deleted successfully",
        )


router = UserRouter().router
