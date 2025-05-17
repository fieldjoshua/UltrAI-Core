"""
Ultra MVP Backend Application

This module provides the FastAPI application with the core endpoints for the Ultra MVP.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
)
logger = logging.getLogger("ultra-mvp")

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Ultra MVP API",
    description="API for the Ultra MVP, allowing analysis of prompts with multiple LLMs.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with actual frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define models
class AnalysisRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to analyze")
    selected_models: List[str] = Field(..., description="List of LLM models to use")
    ultra_model: Optional[str] = Field(
        None, description="The model to use for synthesis"
    )
    pattern: Optional[str] = Field(
        "comprehensive", description="Analysis pattern to use"
    )
    options: Optional[Dict[str, Any]] = Field({}, description="Additional options")


class ModelResponse(BaseModel):
    content: Optional[str] = None
    error: Optional[str] = None
    tokens: Optional[int] = None
    processing_time: Optional[float] = None


class AnalysisResponse(BaseModel):
    status: str
    analysis_id: Optional[str] = None
    message: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


# Mock LLM responses for testing
MOCK_RESPONSES = {
    "gpt4o": "Paris is the capital of France, known for its iconic Eiffel Tower and rich cultural heritage.",
    "claude3opus": "The capital of France is Paris, which is situated on the Seine River in the northern part of the country.",
    "gemini15": "Paris is the capital city of France. It's located in the north-central part of the country on the Seine River.",
    "mistral": "Paris is the capital of France. It is known as the 'City of Light' and is famous for its art, culture, and landmarks like the Eiffel Tower.",
    "llama3": "The capital of France is Paris. It is one of the world's major global cities and an important center for finance, diplomacy, commerce, fashion, and science.",
}

# Mock data for available models
AVAILABLE_MODELS = [
    {
        "id": "gpt4o",
        "name": "GPT-4o",
        "description": "OpenAI's most capable multimodal model",
        "status": "available",
    },
    {
        "id": "claude3opus",
        "name": "Claude 3 Opus",
        "description": "Anthropic's flagship model",
        "status": "available",
    },
    {
        "id": "gemini15",
        "name": "Gemini 1.5 Pro",
        "description": "Google's multimodal model",
        "status": "available",
    },
    {
        "id": "mistral",
        "name": "Mistral Large",
        "description": "Mistral AI's largest model",
        "status": "available",
    },
    {
        "id": "llama3",
        "name": "Llama 3 70B",
        "description": "Meta's open model",
        "status": "available",
    },
]

# Mock data for analysis patterns
AVAILABLE_PATTERNS = [
    "comprehensive",
    "comparative",
    "critical",
    "creative",
    "technical",
]

# Storage for request responses (would be a proper database in production)
request_cache = {}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log details about each request"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.4f}s")

    return response


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Ultra MVP API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time(), "version": "1.0.0"}


@app.get("/api/llms")
async def get_available_llms():
    """Get all available LLM models"""
    try:
        return {
            "status": "success",
            "count": len(AVAILABLE_MODELS),
            "models": AVAILABLE_MODELS,
        }
    except Exception as e:
        logger.error(f"Error retrieving LLM models: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving LLM information: {str(e)}"
        )


@app.get("/api/patterns")
async def get_available_patterns():
    """Get all available analysis patterns"""
    try:
        return {
            "status": "success",
            "count": len(AVAILABLE_PATTERNS),
            "patterns": AVAILABLE_PATTERNS,
        }
    except Exception as e:
        logger.error(f"Error retrieving patterns: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving patterns: {str(e)}"
        )


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_prompt(request: AnalysisRequest = Body(...)):
    """
    Analyze a prompt using multiple LLMs and optionally an Ultra LLM
    for synthesis.
    """
    try:
        # Validate the request
        if not request.prompt.strip():
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Prompt cannot be empty"},
            )

        if not request.selected_models:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "At least one model must be selected",
                },
            )

        # Get the set of valid model IDs
        valid_model_ids = [model["id"] for model in AVAILABLE_MODELS]

        # Filter out invalid models
        valid_selected_models = [
            model for model in request.selected_models if model in valid_model_ids
        ]

        if not valid_selected_models:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "No valid models selected"},
            )

        # Generate a unique analysis ID
        analysis_id = f"analysis_{int(time.time())}"

        # Mock for now - in production, this would call the actual LLM orchestrator
        start_time = time.time()

        # Process with selected models
        model_responses = {}
        for model in valid_selected_models:
            # Simulate processing time
            time.sleep(0.5)

            # Get mock response for the model
            model_responses[model] = {
                "content": MOCK_RESPONSES.get(
                    model, f"This is a response from {model}"
                ),
                "processing_time": 0.5,
                "tokens": len(MOCK_RESPONSES.get(model, "").split()),
            }

        # Create Ultra synthesis if requested
        ultra_response = None
        if request.ultra_model and request.ultra_model in valid_selected_models:
            # Simulate synthesis
            time.sleep(0.8)

            # Create a synthesis combining insights from all models
            synthesis_text = (
                f"Based on analysis from {len(valid_selected_models)} models, "
                f"the consensus is that Paris is the capital of France. "
                f"Models highlight its cultural significance, location on the Seine River, "
                f"and its status as a global center for art, fashion, and diplomacy."
            )

            ultra_response = {
                "content": synthesis_text,
                "processing_time": 0.8,
                "tokens": len(synthesis_text.split()),
            }

        # Calculate total processing time
        total_time = time.time() - start_time

        # Create the response
        result = {
            "status": "success",
            "analysis_id": analysis_id,
            "results": {
                "model_responses": model_responses,
                "ultra_response": ultra_response,
                "total_time": total_time,
            },
        }

        # Store in cache
        request_cache[analysis_id] = result

        return result

    except Exception as e:
        logger.error(f"Error processing analysis request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error processing analysis: {str(e)}",
            },
        )


@app.get("/api/analyze/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get the results of a previous analysis"""
    if analysis_id not in request_cache:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": f"Analysis {analysis_id} not found"},
        )

    return request_cache[analysis_id]


if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # Start the server
    uvicorn.run("app:app", host=host, port=port, reload=debug)
