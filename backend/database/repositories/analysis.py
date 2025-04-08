"""
Analysis repository for the Ultra backend.

This module provides repository for analysis-related database operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.database.models.analysis import Analysis, AnalysisStatus
from backend.database.repositories.base import BaseRepository
from backend.utils.logging import get_logger

logger = get_logger("database.analysis_repository", "logs/database.log")


class AnalysisRepository(BaseRepository[Analysis]):
    """Repository for analysis operations"""

    def __init__(self):
        super().__init__(Analysis)

    def get_by_uuid(self, db: Session, uuid: str) -> Optional[Analysis]:
        """
        Get an analysis by its UUID

        Args:
            db: Database session
            uuid: Analysis UUID

        Returns:
            The analysis if found, None otherwise
        """
        try:
            return db.query(Analysis).filter(Analysis.uuid == uuid).first()
        except Exception as e:
            logger.error(f"Error getting analysis with UUID {uuid}: {str(e)}")
            return None

    def get_user_analyses(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """
        Get analyses for a specific user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user analyses
        """
        return (
            db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(desc(Analysis.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_cached_analysis(
        self, db: Session, cache_key: str
    ) -> Optional[Analysis]:
        """
        Get an analysis by its cache key

        Args:
            db: Database session
            cache_key: Cache key

        Returns:
            The analysis if found and cached, None otherwise
        """
        try:
            return (
                db.query(Analysis)
                .filter(
                    Analysis.cache_key == cache_key,
                    Analysis.is_cached.is_(True),
                    Analysis.status == AnalysisStatus.COMPLETED
                )
                .first()
            )
        except Exception as e:
            logger.error(f"Error getting cached analysis with key {cache_key}: {str(e)}")
            return None

    def update_status(
        self,
        db: Session,
        analysis_id: int,
        status: AnalysisStatus,
        error_message: Optional[str] = None
    ) -> Analysis:
        """
        Update analysis status

        Args:
            db: Database session
            analysis_id: Analysis ID
            status: New status
            error_message: Optional error message

        Returns:
            The updated analysis
        """
        analysis = self.get_by_id(db, analysis_id, raise_if_not_found=True)

        update_data = {"status": status}
        if error_message is not None:
            update_data["error_message"] = error_message

        if status == AnalysisStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()

        return self.update(db, db_obj=analysis, obj_in=update_data)

    def update_result(
        self,
        db: Session,
        analysis_id: int,
        result: Dict[str, Any],
        ultra_response: Optional[str] = None,
        model_times: Optional[Dict[str, float]] = None,
        token_counts: Optional[Dict[str, int]] = None,
        total_tokens: Optional[int] = None,
        total_time_seconds: Optional[float] = None,
        estimated_cost: Optional[float] = None
    ) -> Analysis:
        """
        Update analysis result

        Args:
            db: Database session
            analysis_id: Analysis ID
            result: Analysis result data
            ultra_response: Ultra's processed response
            model_times: Timing data for each model
            token_counts: Token usage data for each model
            total_tokens: Total tokens used
            total_time_seconds: Total processing time
            estimated_cost: Estimated cost of the analysis

        Returns:
            The updated analysis
        """
        analysis = self.get_by_id(db, analysis_id, raise_if_not_found=True)

        update_data = {
            "result": result,
            "status": AnalysisStatus.COMPLETED,
            "completed_at": datetime.utcnow()
        }

        if ultra_response is not None:
            update_data["ultra_response"] = ultra_response
        if model_times is not None:
            update_data["model_times"] = model_times
        if token_counts is not None:
            update_data["token_counts"] = token_counts
        if total_tokens is not None:
            update_data["total_tokens"] = total_tokens
        if total_time_seconds is not None:
            update_data["total_time_seconds"] = total_time_seconds
        if estimated_cost is not None:
            update_data["estimated_cost"] = estimated_cost

        return self.update(db, db_obj=analysis, obj_in=update_data)

    def set_as_cached(
        self,
        db: Session,
        analysis_id: int,
        cache_key: str
    ) -> Analysis:
        """
        Mark an analysis as cached

        Args:
            db: Database session
            analysis_id: Analysis ID
            cache_key: Cache key for the analysis

        Returns:
            The updated analysis
        """
        analysis = self.get_by_id(db, analysis_id, raise_if_not_found=True)

        update_data = {
            "is_cached": True,
            "cache_key": cache_key
        }

        return self.update(db, db_obj=analysis, obj_in=update_data)