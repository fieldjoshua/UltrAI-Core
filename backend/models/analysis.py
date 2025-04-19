"""
Analysis models for the backend API.

This module defines the Pydantic models for the analysis API endpoints.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class AlaCarteOption(str, Enum):
    """A la carte options for analysis"""
    FACT_CHECK = "fact_check"
    AVOID_AI_DETECTION = "avoid_ai_detection"
    SOURCING = "sourcing"
    ENCRYPTED = "encrypted"
    NO_DATA_SHARING = "no_data_sharing"
    ALTERNATE_PERSPECTIVE = "alternate_perspective"


class OutputFormat(str, Enum):
    """Output format options"""
    TEXT = "txt"
    RTF = "rtf"
    GOOGLE_DOCS = "google_docs"
    WORD = "word"


class AnalysisRequest(BaseModel):
    """Analysis request model."""
    prompt: str = Field(..., description="The prompt to analyze")
    selected_models: List[str] = Field(..., description="List of LLM models to use")
    ultra_model: str = Field(..., description="Ultra model to use")
    pattern: str = Field("confidence", description="Analysis pattern to use")
    ala_carte_options: Optional[List[AlaCarteOption]] = Field(
        default=[], description="A la carte options to apply"
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.TEXT, description="Output format"
    )
    document_ids: Optional[List[str]] = Field(
        default=[], description="List of document IDs to analyze"
    )
    options: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional options"
    )


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    id: str
    name: str
    size: int
    type: str
    status: str
    message: str