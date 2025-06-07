"""
Route handlers for the orchestrator service.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import asyncio

from app.utils.logging import get_logger

logger = get_logger("orchestrator_routes")


class AnalysisRequest(BaseModel):
    """Request model for analysis endpoint."""
    query: str = Field(..., description="The query or text to analyze")
    analysis_type: str = Field(default="simple", description="Type of analysis to perform")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional analysis options")
    user_id: Optional[str] = Field(default=None, description="User ID for cost tracking")


class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint."""
    success: bool = Field(..., description="Whether the analysis was successful")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    error: Optional[str] = Field(default=None, description="Error message if analysis failed")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")


def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["Orchestrator"])

    @router.post("/orchestrator/analyze", response_model=AnalysisResponse)
    async def analyze_query(request: AnalysisRequest, http_request: Request):
        """
        Main analysis endpoint using the orchestration service.
        
        This endpoint provides the core analysis functionality by routing
        requests through the multi-stage orchestration pipeline.
        """
        try:
            import time
            start_time = time.time()
            
            logger.info(f"Starting analysis for query: {request.query[:100]}...")
            
            # Get orchestration service from app state
            if not hasattr(http_request.app.state, 'orchestration_service'):
                raise HTTPException(
                    status_code=503, 
                    detail="Orchestration service not available"
                )
            
            orchestration_service = http_request.app.state.orchestration_service
            
            # Run the analysis pipeline
            pipeline_results = await orchestration_service.run_pipeline(
                input_data=request.query,
                options=request.options,
                user_id=request.user_id
            )
            
            # Process results into response format
            analysis_results = {}
            for stage_name, stage_result in pipeline_results.items():
                if stage_result.error:
                    analysis_results[stage_name] = {
                        "error": stage_result.error,
                        "status": "failed"
                    }
                else:
                    analysis_results[stage_name] = {
                        "output": stage_result.output,
                        "quality": stage_result.quality.__dict__ if stage_result.quality else None,
                        "status": "completed"
                    }
            
            processing_time = time.time() - start_time
            
            logger.info(f"Analysis completed in {processing_time:.2f} seconds")
            
            return AnalysisResponse(
                success=True,
                results=analysis_results,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return AnalysisResponse(
                success=False,
                results={},
                error=str(e)
            )

    @router.get("/orchestrator/health")
    async def orchestrator_health(http_request: Request):
        """Check orchestrator service health."""
        try:
            if hasattr(http_request.app.state, 'orchestration_service'):
                return {"status": "healthy", "service": "orchestration"}
            else:
                return {"status": "degraded", "service": "orchestration", "error": "Service not initialized"}
        except Exception as e:
            return {"status": "error", "service": "orchestration", "error": str(e)}

    return router


router = create_router()  # Expose router for application
