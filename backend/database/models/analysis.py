"""
Analysis models for the Ultra backend.

This module defines the SQLAlchemy ORM models for analysis results and related data.
"""

import enum
from datetime import datetime

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, Text, Boolean)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from backend.database.models.base import Base


class AnalysisStatus(enum.Enum):
    """Analysis status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisType(enum.Enum):
    """Analysis type enumeration"""
    STANDARD = "standard"
    DOCUMENT = "document"
    SUMMARIZATION = "summarization"
    COMPARISON = "comparison"
    CUSTOM = "custom"


class AlaCarteOption(enum.Enum):
    """A la carte options for analysis"""
    FACT_CHECK = "fact_check"
    AVOID_AI_DETECTION = "avoid_ai_detection"
    SOURCING = "sourcing"
    ENCRYPTED = "encrypted"
    NO_DATA_SHARING = "no_data_sharing"
    ALTERNATE_PERSPECTIVE = "alternate_perspective"


class OutputFormat(enum.Enum):
    """Output format options"""
    TEXT = "txt"
    RTF = "rtf"
    GOOGLE_DOCS = "google_docs"
    WORD = "word"


class Analysis(Base):
    """Analysis model for storing analysis results"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Analysis metadata
    prompt = Column(Text, nullable=False)
    analysis_type = Column(Enum(AnalysisType), default=AnalysisType.STANDARD, nullable=False)
    pattern = Column(String, nullable=True)
    ultra_model = Column(String, nullable=False)

    # A la carte options
    ala_carte_options = Column(ARRAY(String), nullable=True)

    # Output format
    output_format = Column(Enum(OutputFormat), default=OutputFormat.TEXT, nullable=False)

    # Selected models
    selected_models = Column(ARRAY(String), nullable=False)

    # Results
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    result = Column(JSONB, nullable=True)
    ultra_response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Performance metrics
    total_time_seconds = Column(Float, nullable=True)
    model_times = Column(JSONB, nullable=True)  # Map of model name to time in seconds
    token_counts = Column(JSONB, nullable=True)  # Map of model name to token counts
    total_tokens = Column(Integer, nullable=True)

    # Cost metrics
    estimated_cost = Column(Float, nullable=True)

    # Document reference (for document analyses)
    document_ids = Column(ARRAY(Integer), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Cache metadata
    cache_key = Column(String, nullable=True, index=True)
    is_cached = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="analyses")

    def __repr__(self) -> str:
        return f"<Analysis {self.uuid}>"


class AnalysisResult(Base):
    """Model for storing detailed analysis results"""

    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)

    # Model results
    model_name = Column(String, nullable=False)
    response = Column(Text, nullable=False)
    response_time = Column(Float, nullable=True)

    # Token usage
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    # Cost calculation
    cost = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    analysis = relationship("Analysis")

    def __repr__(self) -> str:
        return f"<AnalysisResult {self.id} for Analysis {self.analysis_id}>"