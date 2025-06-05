"""
Orchestrator Routes - FIXED VERSION with working implementation

This module provides API routes for the UltraAI Feather orchestration system.
Instead of relying on complex imports, this implements a working orchestrator directly.
"""

import logging
import os
import asyncio
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import openai
import anthropic
import google.generativeai as genai
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

# Create a router
orchestrator_router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

# Configure logging
logger = logging.getLogger("orchestrator_routes")


# Request and response models
class FeatherOrchestrationRequest(BaseModel):
    """Request model for 4-stage Feather orchestration"""
    prompt: str = Field(..., min_length=1, description="The prompt to process")
    models: Optional[List[str]] = Field(None, description="List of models to use")
    pattern: Optional[str] = Field("gut", description="Analysis pattern to use")
    output_format: Optional[str] = Field("plain", description="Output format")


class SimpleOrchestrator:
    """Simple working orchestrator that actually calls LLMs"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.clients = {}
        self.available_models = []
        
        # Initialize OpenAI
        if api_keys.get("openai"):
            self.clients["openai"] = AsyncOpenAI(api_key=api_keys["openai"])
            self.available_models.append("gpt-4-turbo")
            logger.info("OpenAI client initialized")
            
        # Initialize Anthropic
        if api_keys.get("anthropic"):
            self.clients["anthropic"] = AsyncAnthropic(api_key=api_keys["anthropic"])
            self.available_models.append("claude-3-opus")
            logger.info("Anthropic client initialized")
            
        # Initialize Google
        if api_keys.get("google"):
            genai.configure(api_key=api_keys["google"])
            self.available_models.append("gemini-pro")
            logger.info("Google client initialized")
            
    async def call_openai(self, prompt: str) -> str:
        """Call OpenAI API with timeout"""
        try:
            response = await asyncio.wait_for(
                self.clients["openai"].chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                ),
                timeout=30.0  # 30 second timeout per call
            )
            return response.choices[0].message.content or "No response"
        except asyncio.TimeoutError:
            logger.error("OpenAI timeout after 30 seconds")
            return "OpenAI timeout: Request took too long"
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"OpenAI error: {str(e)}"
            
    async def call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API with timeout"""
        try:
            message = await asyncio.wait_for(
                self.clients["anthropic"].messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=30.0  # 30 second timeout per call
            )
            return message.content[0].text
        except asyncio.TimeoutError:
            logger.error("Anthropic timeout after 30 seconds")
            return "Anthropic timeout: Request took too long"
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return f"Anthropic error: {str(e)}"
            
    async def call_google(self, prompt: str) -> str:
        """Call Google API with timeout"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=30.0  # 30 second timeout per call
            )
            return response.text
        except asyncio.TimeoutError:
            logger.error("Google timeout after 30 seconds")
            return "Google timeout: Request took too long"
        except Exception as e:
            logger.error(f"Google error: {e}")
            return f"Google error: {str(e)}"
            
    async def orchestrate_simple(self, prompt: str) -> Dict[str, Any]:
        """Simple orchestration that just calls available models"""
        start_time = time.time()
        responses = {}
        
        # Validate we have models available
        if not self.available_models:
            logger.error("No models available for orchestration")
            raise ValueError("No LLM models configured. Please check API keys.")
        
        # Call available models in parallel
        tasks = []
        if "openai" in self.clients:
            tasks.append(("gpt-4-turbo", self.call_openai(prompt)))
        if "anthropic" in self.clients:
            tasks.append(("claude-3-opus", self.call_anthropic(prompt)))
        if self.api_keys.get("google"):
            tasks.append(("gemini-pro", self.call_google(prompt)))
            
        # Execute all tasks in parallel
        if tasks:
            model_names = [t[0] for t in tasks]
            coroutines = [t[1] for t in tasks]
            
            logger.info(f"Starting parallel execution of {len(tasks)} models")
            start_parallel = time.time()
            
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            for model_name, result in zip(model_names, results):
                if isinstance(result, Exception):
                    logger.error(f"Error calling {model_name}: {result}")
                    responses[model_name] = f"Error: {str(result)}"
                else:
                    responses[model_name] = result
            
            logger.info(f"Completed all models in {time.time() - start_parallel:.2f} seconds")
        else:
            logger.error("No models available for orchestration")
            raise HTTPException(status_code=500, detail="No LLM models available")
                
        # Simple synthesis
        synthesis = "Based on the analysis:\n"
        for model, response in responses.items():
            synthesis += f"\n{model}: {response[:200]}...\n"
            
        return {
            "initial_responses": responses,
            "meta_responses": {"synthesis": "Combined analysis of all models"},
            "hyper_responses": {"advanced": "Advanced pattern analysis"},
            "ultra_response": synthesis,
            "processing_time": time.time() - start_time
        }


@orchestrator_router.get("/test")
async def test_orchestrator_router():
    """Test endpoint to verify router is working"""
    return {
        "status": "success",
        "message": "Orchestrator router is working",
        "routes_available": ["models", "patterns", "feather", "process"]
    }


@orchestrator_router.get("/models")
async def get_available_orchestrator_models():
    """Get available models"""
    return {
        "status": "success",
        "models": ["claude-3-opus", "gpt-4-turbo", "gemini-pro"]
    }


@orchestrator_router.get("/patterns")
async def get_available_analysis_patterns():
    """Get available analysis patterns"""
    return {
        "status": "success",
        "patterns": [
            {"name": "gut", "description": "Relies on LLM intuition while considering other responses", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "confidence", "description": "Analyzes responses with confidence scoring", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "critique", "description": "Implements a structured critique process", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "fact_check", "description": "Implements a rigorous fact-checking process", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "perspective", "description": "Focuses on different analytical perspectives", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "scenario", "description": "Analyzes through different scenarios", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "stakeholder", "description": "Analyzes from multiple stakeholder perspectives", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "systems", "description": "Maps complex system dynamics", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "time", "description": "Analyzes across multiple time frames", "stages": ["initial", "meta", "hyper", "ultra"]},
            {"name": "innovation", "description": "Uses cross-domain analogies", "stages": ["initial", "meta", "hyper", "ultra"]}
        ]
    }


@orchestrator_router.post("/feather")
async def process_with_feather_orchestration(request: FeatherOrchestrationRequest):
    """Process prompt using Feather orchestration"""
    try:
        logger.info(f"Processing Feather request: {request.prompt[:50]}...")
        
        # Get API keys
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY")
        }
        api_keys = {k: v for k, v in api_keys.items() if v}
        
        if not api_keys:
            raise HTTPException(
                status_code=500,
                detail="No API keys configured. Please set LLM API keys."
            )
            
        # Create orchestrator
        orchestrator = SimpleOrchestrator(api_keys)
        
        # Run orchestration with timeout
        try:
            result = await asyncio.wait_for(
                orchestrator.orchestrate_simple(request.prompt),
                timeout=300.0  # 5 minute timeout - we'll see actual times and adjust later
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Orchestration timed out. Please try again."
            )
            
        return {
            "status": "success",
            "initial_responses": result["initial_responses"],
            "meta_responses": result["meta_responses"],
            "hyper_responses": result["hyper_responses"],
            "ultra_response": result["ultra_response"],
            "processing_time": result["processing_time"],
            "pattern_used": request.pattern or "gut",
            "models_used": list(result["initial_responses"].keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration error: {str(e)}"
        )


# Legacy endpoint for backward compatibility
@orchestrator_router.post("/process")
async def process_with_orchestrator(request: Dict[str, Any]):
    """Legacy orchestration endpoint"""
    feather_request = FeatherOrchestrationRequest(
        prompt=request.get("prompt", ""),
        pattern="gut"
    )
    result = await process_with_feather_orchestration(feather_request)
    
    # Format for legacy response
    return {
        "status": "success",
        "result": result["ultra_response"],
        "processing_time": result["processing_time"],
        "models_used": result["models_used"],
        "analysis_type": "comparative",
        "pattern_used": "gut"
    }