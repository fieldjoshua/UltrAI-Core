#!/usr/bin/env python3
"""
Simple test endpoint that bypasses orchestration complexity.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from app.services.llm_adapters import GeminiAdapter, AnthropicAdapter
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/test/gemini")
async def test_gemini():
    """Test Gemini API directly."""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return JSONResponse({"error": "No Google API key found"}, status_code=500)
        
        adapter = GeminiAdapter(api_key, "gemini-1.5-flash")
        result = await adapter.generate("What is 2+2? Answer in one line.")
        return {"success": True, "result": result}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/test/anthropic")
async def test_anthropic():
    """Test Anthropic API directly."""
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return JSONResponse({"error": "No Anthropic API key found"}, status_code=500)
        
        adapter = AnthropicAdapter(api_key, "claude-3-haiku-20240307")
        result = await adapter.generate("What is 2+2? Answer in one line.")
        return {"success": True, "result": result}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/test/simple-orchestrate")
async def simple_orchestrate():
    """Simple orchestration without all the complexity."""
    try:
        google_key = os.getenv("GOOGLE_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        results = []
        
        # Try Gemini
        if google_key:
            try:
                adapter = GeminiAdapter(google_key, "gemini-1.5-flash")
                result = await adapter.generate("What is 2+2?")
                results.append({"model": "gemini-1.5-flash", "response": result})
            except Exception as e:
                results.append({"model": "gemini-1.5-flash", "error": str(e)})
        
        # Try Anthropic
        if anthropic_key:
            try:
                adapter = AnthropicAdapter(anthropic_key, "claude-3-haiku-20240307")
                result = await adapter.generate("What is 2+2?")
                results.append({"model": "claude-3-haiku", "response": result})
            except Exception as e:
                results.append({"model": "claude-3-haiku", "error": str(e)})
        
        # Simple synthesis
        if results:
            synthesis = "Based on the AI responses, 2+2 equals 4."
            return {
                "success": True,
                "models_used": len(results),
                "results": results,
                "synthesis": synthesis
            }
        else:
            return JSONResponse({"error": "No models available"}, status_code=503)
            
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    print("Starting simple test server on http://localhost:8001")
    print("Available endpoints:")
    print("  GET /test/gemini")
    print("  GET /test/anthropic")
    print("  GET /test/simple-orchestrate")
    uvicorn.run(app, host="0.0.0.0", port=8001)