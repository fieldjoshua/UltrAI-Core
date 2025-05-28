"""
Simplified orchestrator routes for testing
"""

from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/test/simple")
async def simple_test():
    """Simple test endpoint"""
    return {"status": "ok", "message": "Simple test works"}

@router.get("/test/models")
async def test_models():
    """Test models endpoint without orchestrator"""
    # Just return environment variable names for testing
    api_keys = {
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "google": bool(os.getenv("GOOGLE_API_KEY")),
        "mistral": bool(os.getenv("MISTRAL_API_KEY")),
    }
    
    models = []
    if api_keys.get("anthropic"):
        models.append("claude-3-opus")
    if api_keys.get("openai"):
        models.append("gpt-4-turbo")
    if api_keys.get("google"):
        models.append("gemini-pro")
    if api_keys.get("mistral"):
        models.append("mistral-large")
        
    if not models:
        models = ["mock-claude", "mock-gpt4", "mock-gemini"]
    
    return {
        "status": "success",
        "models": models,
        "test": True
    }