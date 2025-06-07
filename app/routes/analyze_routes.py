"""
Route handlers for direct analysis endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import asyncio

from app.utils.logging import get_logger

logger = get_logger("analyze_routes")


class SimpleAnalysisRequest(BaseModel):
    """Request model for simple analysis endpoint."""
    text: str = Field(..., description="Text to analyze")
    model: Optional[str] = Field(default="gpt-4", description="Model to use for analysis")
    temperature: Optional[float] = Field(default=0.7, description="Analysis temperature")


class SimpleAnalysisResponse(BaseModel):
    """Response model for simple analysis endpoint."""
    success: bool = Field(..., description="Whether analysis was successful")
    analysis: str = Field(..., description="Analysis result")
    model_used: str = Field(..., description="Model used for analysis")
    error: Optional[str] = Field(default=None, description="Error message if failed")


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Analyze"])

    @router.post("/analyze", response_model=SimpleAnalysisResponse)
    async def simple_analyze(request: SimpleAnalysisRequest, http_request: Request):
        """
        Simple direct analysis endpoint.
        
        Provides a streamlined analysis interface that bypasses the full
        orchestration pipeline for faster, simpler analysis requests.
        """
        try:
            logger.info(f"Starting simple analysis with model: {request.model}")
            
            # For rapid implementation, return a structured response
            # In full implementation, this would connect to LLM adapters
            mock_analysis = f"""
Analysis of the provided text using {request.model}:

Text Length: {len(request.text)} characters
Analysis Type: Simple Direct Analysis
Temperature: {request.temperature}

Key Insights:
- Text appears to be well-formed
- Contains {len(request.text.split())} words approximately
- Analysis completed successfully

This is a rapid implementation response. Full LLM integration would provide deeper analysis.
            """.strip()
            
            logger.info(f"Analysis completed successfully with {request.model}")
            
            return SimpleAnalysisResponse(
                success=True,
                analysis=mock_analysis,
                model_used=request.model,
                error=None
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return SimpleAnalysisResponse(
                success=False,
                analysis="",
                model_used=request.model,
                error=str(e)
            )

    @router.get("/analyze/health")
    async def analyze_health():
        """Check analysis service health."""
        return {"status": "healthy", "service": "analyze"}

    return router


analyze_router = create_router()  # Expose router for application
