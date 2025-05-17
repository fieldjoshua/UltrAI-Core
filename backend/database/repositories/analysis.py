"""
Analysis repository for the Ultra backend.

This module provides data access operations for analysis-related models.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database.models.analysis import Analysis
from backend.database.repositories.base import BaseRepository
from backend.utils.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for analysis operations."""

    def __init__(self):
        """Initialize the analysis repository."""
        super().__init__(Analysis)

    def get_by_user_id(
        self, db: Session, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """Get all analyses for a specific user.

        Args:
            db: Database session
            user_id: The ID of the user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of analyses performed by the user
        """
        try:
            return (
                db.query(Analysis)
                .filter(Analysis.user_id == user_id)
                .order_by(Analysis.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving user analyses: {e}")
            raise DatabaseException(f"Failed to retrieve user analyses: {str(e)}")

    def get_by_document_id(
        self, db: Session, document_id: str, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """Get all analyses for a specific document.

        Args:
            db: Database session
            document_id: The ID of the document
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of analyses performed on the document
        """
        try:
            return (
                db.query(Analysis)
                .filter(Analysis.document_id == document_id)
                .order_by(Analysis.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving document analyses: {e}")
            raise DatabaseException(f"Failed to retrieve document analyses: {str(e)}")

    def get_by_pattern(
        self, db: Session, pattern: str, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """Get all analyses using a specific pattern.

        Args:
            db: Database session
            pattern: The pattern name
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of analyses using the specified pattern
        """
        try:
            return (
                db.query(Analysis)
                .filter(Analysis.pattern == pattern)
                .order_by(Analysis.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving analyses by pattern: {e}")
            raise DatabaseException(f"Failed to retrieve analyses by pattern: {str(e)}")

    def create_analysis(
        self,
        db: Session,
        user_id: str,
        document_id: Optional[str],
        pattern: str,
        prompt: str,
        models: List[str],
        options: Dict[str, Any],
    ) -> Analysis:
        """Create a new analysis record.

        Args:
            db: Database session
            user_id: The ID of the user
            document_id: Optional ID of the document being analyzed
            pattern: The pattern used for analysis
            prompt: The user prompt
            models: List of models used for the analysis
            options: Additional options used for the analysis

        Returns:
            The created analysis record
        """
        analysis_data = {
            "user_id": user_id,
            "document_id": document_id,
            "pattern": pattern,
            "prompt": prompt,
            "models": models,
            "options": options,
            "created_at": datetime.utcnow(),
            "status": "pending",
        }

        return self.create(db, analysis_data)

    def update_analysis_status(
        self,
        db: Session,
        analysis_id: int,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Analysis:
        """Update the status of an analysis.

        Args:
            db: Database session
            analysis_id: The ID of the analysis
            status: The new status ('completed', 'failed', etc.)
            result: Optional result data for successful analyses
            error: Optional error message for failed analyses

        Returns:
            The updated analysis record
        """
        analysis = self.get_by_id(db, analysis_id, raise_if_not_found=True)

        update_data = {"status": status, "completed_at": datetime.utcnow()}

        if result is not None:
            update_data["result"] = result

        if error is not None:
            update_data["error"] = error

        return self.update(db, db_obj=analysis, obj_in=update_data)

    def get_recent_analyses(self, db: Session, limit: int = 10) -> List[Analysis]:
        """Get the most recent analyses across all users.

        Args:
            db: Database session
            limit: Maximum number of records to return

        Returns:
            List of recent analyses
        """
        try:
            return (
                db.query(Analysis)
                .order_by(Analysis.created_at.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving recent analyses: {e}")
            raise DatabaseException(f"Failed to retrieve recent analyses: {str(e)}")

    def get_stats_by_pattern(self, db: Session) -> Dict[str, int]:
        """Get statistics on analysis usage by pattern.

        Args:
            db: Database session

        Returns:
            Dictionary mapping pattern names to usage count
        """
        try:
            result = {}
            patterns = (
                db.query(Analysis.pattern, func.count(Analysis.id))
                .group_by(Analysis.pattern)
                .all()
            )

            for pattern, count in patterns:
                result[pattern] = count

            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving analysis statistics: {e}")
            raise DatabaseException(f"Failed to retrieve analysis statistics: {str(e)}")
