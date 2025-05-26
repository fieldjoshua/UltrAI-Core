"""Minimal Ultra FastAPI app with no SQLAlchemy dependency"""

import logging
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal app
app = FastAPI(
    title="Ultra API - Minimal",
    version="1.0.0",
    description="Minimal Ultra API without database dependencies",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "ultra-api-minimal",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "production"),
        "database": "not configured",
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Ultra API Minimal - No Database",
        "version": "1.0.0",
        "health": "/api/health",
    }


# Simple analyze endpoint
@app.post("/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
        return {
            "status": "processing",
            "message": "Analysis started",
            "input": data.get("prompt", "No prompt provided"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Available models endpoint
@app.get("/api/available-models")
async def get_available_models():
    return {
        "status": "ok",
        "available_models": [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus",
            "claude-3-sonnet",
        ],
    }


# Simple orchestrator endpoint
@app.post("/api/orchestrator/execute")
async def execute_orchestrator(request: Request):
    try:
        data = await request.json()
        return {
            "status": "success",
            "result": {
                "prompt": data.get("prompt", ""),
                "models": data.get("models", []),
                "pattern": data.get("pattern", "default"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Login endpoint (mock)
@app.post("/api/auth/login")
async def login(request: Request):
    try:
        data = await request.json()
        return {
            "access_token": "mock_token_123456",
            "token_type": "bearer",
            "user": {"email": data.get("email", "user@example.com"), "id": "123"},
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Upload document endpoint
@app.post("/api/upload-document")
async def upload_document():
    return {
        "status": "success",
        "message": "Document processing not implemented in minimal mode",
        "document_id": "mock_123",
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
            "details": str(exc) if os.getenv("ENV") != "production" else None,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info"
    )
