"""
Base repository class for the Ultra backend.

This module provides a base repository class with common CRUD operations
that can be extended by specific repository implementations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import exc
from sqlalchemy.orm import Session

from backend.utils.exceptions import DatabaseException, ResourceNotFoundException
from backend.utils.logging import get_logger

# Create a generic type variable for the model
T = TypeVar("T")

# Set up logger
logger = get_logger("database.repository", "logs/database.log")


class BaseRepository(Generic[T]):
    """Base repository for database operations"""

    def __init__(self, model: Type[T]):
        """
        Initialize the repository with a model class

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def create(self, db: Session, obj_in: Dict[str, Any]) -> T:
        """
        Create a new instance of the model

        Args:
            db: Database session
            obj_in: Dictionary with model attributes

        Returns:
            The created model instance

        Raises:
            DatabaseException: If an error occurs during creation
        """
        try:
            obj = self.model(**obj_in)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except exc.SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise DatabaseException(
                message=f"Error creating {self.model.__name__}",
                operation="create",
                details={"error": str(e)},
            )

    def get(self, db: Session, id: int) -> Optional[T]:
        """
        Get a model instance by ID

        Args:
            db: Database session
            id: Model ID

        Returns:
            The model instance if found, None otherwise
        """
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} with ID {id}: {str(e)}")
            raise DatabaseException(
                message=f"Error retrieving {self.model.__name__}",
                operation="get",
                details={"id": id, "error": str(e)},
            )

    def get_by_id(
        self, db: Session, id: int, raise_if_not_found: bool = False
    ) -> Optional[T]:
        """
        Get a model instance by ID, with option to raise exception if not found

        Args:
            db: Database session
            id: Model ID
            raise_if_not_found: Whether to raise an exception if the model is not found

        Returns:
            The model instance if found, None otherwise

        Raises:
            ResourceNotFoundException: If the model is not found and raise_if_not_found is True
        """
        obj = self.get(db, id)
        if obj is None and raise_if_not_found:
            raise ResourceNotFoundException(
                resource_type=self.model.__name__,
                resource_id=str(id),
            )
        return obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get multiple model instances with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        try:
            return db.query(self.model).offset(skip).limit(limit).all()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {str(e)}")
            raise DatabaseException(
                message=f"Error retrieving {self.model.__name__} list",
                operation="get_multi",
                details={"skip": skip, "limit": limit, "error": str(e)},
            )

    def update(self, db: Session, *, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """
        Update a model instance

        Args:
            db: Database session
            db_obj: Model instance to update
            obj_in: Dictionary with updated attributes

        Returns:
            The updated model instance
        """
        try:
            # Update model attributes
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except exc.SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise DatabaseException(
                message=f"Error updating {self.model.__name__}",
                operation="update",
                details={"id": db_obj.id, "error": str(e)},
            )

    def delete(self, db: Session, *, id: int) -> T:
        """
        Delete a model instance by ID

        Args:
            db: Database session
            id: Model ID

        Returns:
            The deleted model instance

        Raises:
            ResourceNotFoundException: If the model is not found
        """
        try:
            obj = db.query(self.model).get(id)
            if obj is None:
                raise ResourceNotFoundException(
                    resource_type=self.model.__name__,
                    resource_id=str(id),
                )

            db.delete(obj)
            db.commit()
            return obj
        except ResourceNotFoundException:
            raise
        except exc.SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {str(e)}")
            raise DatabaseException(
                message=f"Error deleting {self.model.__name__}",
                operation="delete",
                details={"id": id, "error": str(e)},
            )

    def count(self, db: Session) -> int:
        """
        Count the total number of model instances

        Args:
            db: Database session

        Returns:
            The total count
        """
        try:
            return db.query(self.model).count()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise DatabaseException(
                message=f"Error counting {self.model.__name__}",
                operation="count",
                details={"error": str(e)},
            )
