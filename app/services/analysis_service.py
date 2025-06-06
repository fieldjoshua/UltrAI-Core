"""Analysis service for the Ultra backend.

This module provides services for analysis-related operations, including
creation, retrieval, and management of analysis records.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.repositories import AnalysisRepository
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for analysis operations."""

    def __init__(self):
        """Initialize the analysis service."""
        self.analysis_repo = AnalysisRepository()
        self.document_service = DocumentService()

    def get_user_analyses(
        self, db: Session, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get analyses for a specific user.

        Args:
            db: Database session
            user_id: The ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user analyses with metadata
        """
        analyses = self.analysis_repo.get_by_user_id(db, user_id, skip, limit)

        # Convert to dictionary with enhanced metadata
        result = []
        for analysis in analyses:
            analysis_dict = self._format_analysis(analysis)
            result.append(analysis_dict)

        return result

    def get_document_analyses(
        self, db: Session, document_id: str, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get analyses for a specific document.

        Args:
            db: Database session
            document_id: The ID of the document
            user_id: Optional user ID for access control

        Returns:
            List of analyses for the document

        Raises:
            PermissionError: If the user doesn't have access to the document
        """
        # Check document access if user_id is provided
        if user_id:
            self.document_service.get_document_by_id(db, document_id, user_id)

        analyses = self.analysis_repo.get_by_document_id(db, document_id)

        # Convert to dictionary with enhanced metadata
        result = []
        for analysis in analyses:
            analysis_dict = self._format_analysis(analysis)
            result.append(analysis_dict)

        return result

    def create_analysis(
        self,
        db: Session,
        user_id: str,
        document_id: Optional[str],
        pattern: str,
        prompt: str,
        models: List[str],
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new analysis.

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

        Raises:
            PermissionError: If the user doesn't have access to the document
        """
        # Check document access if document_id is provided
        if document_id:
            self.document_service.get_document_by_id(db, document_id, user_id)

        analysis = self.analysis_repo.create_analysis(
            db, user_id, document_id, pattern, prompt, models, options
        )

        return self._format_analysis(analysis)

    def update_analysis_status(
        self,
        db: Session,
        analysis_id: int,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the status of an analysis.

        Args:
            db: Database session
            analysis_id: The ID of the analysis
            status: The new status ('completed', 'failed', etc.)
            result: Optional result data for successful analyses
            error: Optional error message for failed analyses
            user_id: Optional user ID for access control

        Returns:
            The updated analysis record

        Raises:
            PermissionError: If the user doesn't have access to the analysis
        """
        # Get the analysis and check ownership if user_id is provided
        analysis = self.analysis_repo.get_by_id(
            db, analysis_id, raise_if_not_found=True
        )
        if user_id and analysis.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to update analysis {analysis_id} owned by {analysis.user_id}"
            )
            raise PermissionError("User does not have access to this analysis")

        updated_analysis = self.analysis_repo.update_analysis_status(
            db, analysis_id, status, result, error
        )

        return self._format_analysis(updated_analysis)

    def get_analysis_by_id(
        self, db: Session, analysis_id: int, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get an analysis by its ID.

        Args:
            db: Database session
            analysis_id: The ID of the analysis
            user_id: Optional user ID for access control

        Returns:
            The analysis with metadata

        Raises:
            PermissionError: If the user doesn't have access to the analysis
        """
        analysis = self.analysis_repo.get_by_id(
            db, analysis_id, raise_if_not_found=True
        )

        # Check if the user has access to this analysis
        if user_id and analysis.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access analysis {analysis_id} owned by {analysis.user_id}"
            )
            raise PermissionError("User does not have access to this analysis")

        return self._format_analysis(analysis)

    def get_pattern_stats(self, db: Session) -> Dict[str, Any]:
        """Get statistics on analysis usage by pattern.

        Args:
            db: Database session

        Returns:
            Dictionary with pattern usage statistics
        """
        pattern_counts = self.analysis_repo.get_stats_by_pattern(db)

        # Calculate total analyses and percentages
        total = sum(pattern_counts.values())

        stats = {
            "total_analyses": total,
            "pattern_counts": pattern_counts,
            "pattern_percentages": {},
        }

        if total > 0:
            for pattern, count in pattern_counts.items():
                stats["pattern_percentages"][pattern] = round((count / total) * 100, 2)

        return stats

    def _format_analysis(self, analysis) -> Dict[str, Any]:
        """Format an analysis model into a dictionary with enhanced metadata.

        Args:
            analysis: The analysis model instance

        Returns:
            Dictionary with analysis data
        """
        return {
            "id": analysis.id,
            "user_id": analysis.user_id,
            "document_id": analysis.document_id,
            "pattern": analysis.pattern,
            "prompt": analysis.prompt,
            "models": analysis.models,
            "status": analysis.status,
            "created_at": (
                analysis.created_at.isoformat() if analysis.created_at else None
            ),
            "completed_at": (
                analysis.completed_at.isoformat() if analysis.completed_at else None
            ),
            "result": analysis.result,
            "error": analysis.error,
            "options": analysis.options,
        }
