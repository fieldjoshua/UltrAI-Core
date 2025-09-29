"""
Analysis Storage Service

This service handles storing and retrieving analysis sessions from the database.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models.analysis import Analysis, AnalysisResult, AnalysisStatus, AnalysisType, OutputFormat
from app.database.session import get_db
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AnalysisStorageService:
    """Service for storing analysis sessions and results."""

    async def create_analysis_session(
        self,
        db: Session,
        user_id: int,
        prompt: str,
        selected_models: List[str],
        analysis_type: AnalysisType = AnalysisType.STANDARD,
        ultra_model: str = "gpt-4",
        output_format: OutputFormat = OutputFormat.TEXT,
        pattern: Optional[str] = None,
        ala_carte_options: Optional[List[str]] = None,
    ) -> Analysis:
        """
        Create a new analysis session in the database.
        
        Args:
            db: Database session
            user_id: ID of the user running the analysis
            prompt: The input prompt for analysis
            selected_models: List of model names used
            analysis_type: Type of analysis
            ultra_model: The lead model for ultra synthesis
            output_format: Desired output format
            pattern: Analysis pattern if applicable
            ala_carte_options: Additional options selected
            
        Returns:
            Created Analysis object
        """
        try:
            analysis = Analysis(
                uuid=str(uuid.uuid4()),
                user_id=user_id,
                prompt=prompt,
                analysis_type=analysis_type,
                pattern=pattern,
                ultra_model=ultra_model,
                ala_carte_options=ala_carte_options or [],
                output_format=output_format,
                selected_models=selected_models,
                status=AnalysisStatus.PROCESSING,
                created_at=datetime.utcnow()
            )
            
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
            logger.info(f"Created analysis session {analysis.uuid} for user {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to create analysis session: {e}")
            db.rollback()
            raise

    async def complete_analysis_session(
        self,
        db: Session,
        analysis_id: int,
        ultra_response: str,
        model_results: Dict[str, Any],
        total_time_seconds: float,
        total_tokens: Optional[int] = None,
        estimated_cost: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> Analysis:
        """
        Complete an analysis session with results.
        
        Args:
            db: Database session
            analysis_id: ID of the analysis to complete
            ultra_response: Final synthesized response
            model_results: Dictionary of model results
            total_time_seconds: Total execution time
            total_tokens: Total tokens used
            estimated_cost: Estimated cost
            error_message: Error message if analysis failed
            
        Returns:
            Updated Analysis object
        """
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ValueError(f"Analysis {analysis_id} not found")
            
            # Update analysis with results
            analysis.ultra_response = ultra_response
            analysis.result = model_results
            analysis.total_time_seconds = total_time_seconds
            analysis.total_tokens = total_tokens
            analysis.estimated_cost = estimated_cost
            analysis.completed_at = datetime.utcnow()
            
            if error_message:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = error_message
            else:
                analysis.status = AnalysisStatus.COMPLETED
            
            # Store individual model results
            for model_name, result_data in model_results.items():
                if isinstance(result_data, dict) and 'response' in result_data:
                    analysis_result = AnalysisResult(
                        analysis_id=analysis.id,
                        model_name=model_name,
                        response=result_data.get('response', ''),
                        response_time=result_data.get('response_time'),
                        prompt_tokens=result_data.get('prompt_tokens'),
                        completion_tokens=result_data.get('completion_tokens'),
                        total_tokens=result_data.get('total_tokens'),
                        cost=result_data.get('cost'),
                        created_at=datetime.utcnow()
                    )
                    db.add(analysis_result)
            
            db.commit()
            db.refresh(analysis)
            
            logger.info(f"Completed analysis session {analysis.uuid}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to complete analysis session {analysis_id}: {e}")
            db.rollback()
            raise

    async def get_user_analysis_history(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Get analysis history for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Analysis objects
        """
        try:
            analyses = (
                db.query(Analysis)
                .filter(Analysis.user_id == user_id)
                .order_by(Analysis.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            
            return analyses
            
        except Exception as e:
            logger.error(f"Failed to get analysis history for user {user_id}: {e}")
            raise

    async def get_analysis_by_uuid(
        self,
        db: Session,
        analysis_uuid: str,
        user_id: Optional[int] = None
    ) -> Optional[Analysis]:
        """
        Get analysis by UUID.
        
        Args:
            db: Database session
            analysis_uuid: Analysis UUID
            user_id: Optional user ID for access control
            
        Returns:
            Analysis object if found, None otherwise
        """
        try:
            query = db.query(Analysis).filter(Analysis.uuid == analysis_uuid)
            
            if user_id:
                query = query.filter(Analysis.user_id == user_id)
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Failed to get analysis {analysis_uuid}: {e}")
            raise

    async def get_user_usage_stats(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with usage statistics
        """
        try:
            total_queries = db.query(Analysis).filter(Analysis.user_id == user_id).count()
            
            completed_queries = (
                db.query(Analysis)
                .filter(Analysis.user_id == user_id, Analysis.status == AnalysisStatus.COMPLETED)
                .count()
            )
            
            # Get models used
            model_results = (
                db.query(Analysis.selected_models)
                .filter(Analysis.user_id == user_id)
                .all()
            )
            
            models_used = set()
            for result in model_results:
                if result.selected_models:
                    models_used.update(result.selected_models)
            
            # Get last query
            last_analysis = (
                db.query(Analysis)
                .filter(Analysis.user_id == user_id)
                .order_by(Analysis.created_at.desc())
                .first()
            )
            
            return {
                "total_queries": total_queries,
                "completed_queries": completed_queries,
                "models_used": list(models_used),
                "last_query": last_analysis.created_at.isoformat() if last_analysis and last_analysis.created_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage stats for user {user_id}: {e}")
            raise