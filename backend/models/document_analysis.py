"""
Document analysis models for the backend API.

This module defines the Pydantic models for document analysis.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class DocumentAnalysisRequest(BaseModel):
    """Document analysis request model."""
    document_id: str = Field(..., description="ID of the document to analyze")
    selected_models: List[str] = Field(..., description="List of LLM models to use")
    ultra_model: str = Field(..., description="Ultra model to use")
    pattern: str = Field("confidence", description="Analysis pattern to use")
    options: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional options"
    )
    user_id: Optional[str] = Field(None, description="Optional user ID")


class DocumentAnalysisResponse(BaseModel):
    """Document analysis response model."""
    status: str = Field(..., description="Response status")
    analysis_id: str = Field(..., description="Unique identifier for the analysis")
    results: Optional[Dict[str, Any]] = Field(None, description="Analysis results if available")
    message: Optional[str] = Field(None, description="Status message")


class DocumentChunkAnalysisRequest(BaseModel):
    """Request model for analyzing document chunks."""
    document_id: str = Field(..., description="ID of the document")
    chunk_ids: List[str] = Field(..., description="List of chunk IDs to analyze")
    query: str = Field(..., description="Query to analyze against the chunks")
    models: List[str] = Field(..., description="List of models to use")
    options: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional options"
    )


class DocumentChunkMetadata(BaseModel):
    """Metadata about a document chunk."""
    id: str
    page: Optional[int] = None
    section: Optional[str] = None
    relevance: float


class DocumentChunkAnalysisResponse(BaseModel):
    """Response model for document chunk analysis."""
    status: str
    document_id: str
    analysis_id: str
    chunk_count: int
    results: Optional[Dict[str, Any]] = None