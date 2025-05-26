#!/usr/bin/env python3
"""
Mock Available Models API Server

This is a simple FastAPI server that implements the /api/available-models endpoint
for production readiness testing.
"""

import logging
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_available_models")

# Create FastAPI app
app = FastAPI(
    title="Mock Available Models API",
    description="Simple mock API server for available-models endpoint",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response model
class AvailableModelsResponse(BaseModel):
    status: str
    available_models: List[str]


@app.get(
    "/api/available-models", response_model=AvailableModelsResponse, tags=["Models"]
)
async def get_available_models():
    """Get available LLM models."""
    logger.info("Received request for available models")
    return {
        "status": "success",
        "available_models": [
            "gpt4o",
            "gpt4turbo",
            "claude37",
            "claude3opus",
            "gemini15",
            "llama3",
        ],
    }


@app.get("/api/health")
async def get_health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    port = 8086  # Use a different port than the main server
    logger.info(f"Starting mock available models API on port {port}")
    logger.info(f"Test with: curl http://localhost:{port}/api/available-models")
    uvicorn.run(app, host="0.0.0.0", port=port)
