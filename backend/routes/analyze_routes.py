import json
import logging
import os
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from backend.config import Config
from backend.utils.cache import response_cache, generate_cache_key
from backend.utils.metrics import performance_metrics, update_metrics_history, processing_times

# Create an analysis router
analyze_router = APIRouter(tags=["Analysis"])

# Configure logging
logger = logging.getLogger("analyze_routes")

# Check if pattern orchestrator is available
try:
    from ultra_pattern_orchestrator import PatternOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    logger.warning("PatternOrchestrator not available, using mock/basic functionality")
    ORCHESTRATOR_AVAILABLE = False

# Check if pricing integration is available
try:
    from pricing_integration import (
        PricingIntegration, check_request_authorization, track_request_cost
    )
    pricing_integration = PricingIntegration()
except ImportError:
    logger.warning("PricingIntegration not available, using mock")
    # Create a mock pricing integration
    class MockPricingIntegration:
        def __init__(self):
            self.pricing_enabled = False

        def estimate_request_cost(self, **kwargs):
            return {
                "estimated_cost": 0.01,
                "tier": "free",
                "has_sufficient_balance": True,
                "cost_details": {
                    "base_cost": 0.01,
                    "markup_cost": 0,
                    "discount_amount": 0,
                    "feature_costs": {},
                },
            }

    pricing_integration = MockPricingIntegration()

    # Define mock functions for pricing
    async def check_request_authorization(**kwargs):
        return {"authorized": True, "details": {}}

    async def track_request_cost(**kwargs):
        return {"status": "success", "cost": 0.01}


@analyze_router.post("/api/analyze")
async def analyze_prompt(request: Request):
    """Analyze a prompt using multiple LLMs and an Ultra LLM"""
    start_time = time.time()

    try:
        data = await request.json()
        prompt = data.get("prompt")
        selected_models = data.get("llms", data.get("selectedModels", []))
        ultra_model = data.get("ultraLLM", data.get("ultraModel"))
        pattern_name = data.get("pattern", "Confidence Analysis")
        options = data.get("options", {})
        user_id = data.get("userId")

        # Validate required fields
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        if not selected_models:
            raise HTTPException(status_code=400, detail="At least one model must be selected")
        if not ultra_model:
            raise HTTPException(status_code=400, detail="Ultra model is required")

        # Update metrics
        performance_metrics["requests_processed"] += 1

        # Check cache for identical request
        cache_key = generate_cache_key(
            prompt, selected_models, ultra_model, pattern_name
        )
        cached_response = response_cache.get(cache_key)

        if cached_response and not options.get("bypass_cache", False):
            logger.info(f"Cache hit for prompt: {prompt[:30]}...")
            performance_metrics["cache_hits"] += 1

            # Add cache indicator to response
            cached_response["cached"] = True
            cached_response["cache_time"] = datetime.now().isoformat()

            # Track cost (even for cached responses)
            if user_id and pricing_integration.pricing_enabled:
                await track_request_cost(
                    user_id=user_id,
                    request_type="cached_analyze",
                    model=ultra_model,
                    tokens_used=0,  # No tokens used for cached response
                )

            return cached_response

        logger.info(f"Received analyze request with pattern: {pattern_name}")

        # Use mock service if in mock mode
        if Config.use_mock and hasattr(Config, 'mock_service') and Config.mock_service:
            try:
                result = await Config.mock_service.analyze_prompt(
                    prompt=prompt,
                    models=selected_models,
                    ultra_model=ultra_model,
                    pattern=pattern_name,
                )

                # Format the result to match expected response structure
                response = {
                    "status": "success",
                    "results": result.get("results", {}),
                    "ultra_response": result.get("ultra_response", ""),
                    "pattern": result.get("pattern", pattern_name),
                }

                # Cache the response
                response_cache[cache_key] = response

                return response
            except Exception as e:
                logger.error(f"Error in mock analyze: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Mock service error: {str(e)}"
                )

        # Map frontend pattern names to backend pattern keys
        pattern_map = {
            "Confidence Analysis": "confidence",
            "Critique": "critique",
            "Gut Check": "gut",
            "Fact Check": "fact_check",
            "Perspective Analysis": "perspective",
            "Scenario Analysis": "scenario",
        }

        pattern_key = pattern_map.get(pattern_name, "confidence")

        # Check authorization if pricing is enabled
        if user_id and pricing_integration.pricing_enabled:
            auth_result = await check_request_authorization(
                user_id=user_id,
                request_type="analyze",
                model=ultra_model,
                estimated_tokens=len(prompt.split()) * 8,  # Rough estimate
            )

            if not auth_result["authorized"]:
                return JSONResponse(
                    status_code=402,  # Payment Required
                    content={
                        "status": "error",
                        "code": "insufficient_balance",
                        "message": "Your account balance is insufficient for this request",
                        "details": auth_result.get("details", {}),
                    },
                )

        try:
            # Initialize the orchestrator with the selected models and pattern
            try:
                # Note: ultra_model is set as a separate attribute after initialization
                orchestrator = PatternOrchestrator(
                    api_keys={
                        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                        "openai": os.getenv("OPENAI_API_KEY"),
                        "google": os.getenv("GOOGLE_API_KEY"),
                        "mistral": os.getenv("MISTRAL_API_KEY"),
                        "deepseek": os.getenv("DEEPSEEK_API_KEY"),
                        "cohere": os.getenv("COHERE_API_KEY"),
                    },
                    pattern=pattern_key,
                    output_format="plain",
                )

                # Set the ultra model after initialization
                orchestrator.ultra_model = ultra_model

                # Process the prompt with the orchestrator
                result = await orchestrator.orchestrate_full_process(prompt)

                # Format the result
                response = {
                    "status": "success",
                    "ultra_response": result.get("ultra_response", ""),
                    "results": {
                        model: content
                        for model, content in result.get(
                            "initial_responses", {}
                        ).items()
                    },
                    "pattern": pattern_name,
                    "processing_time": time.time() - start_time,
                }

                # Cache the response
                response_cache[cache_key] = response

                # Track the request cost if pricing is enabled
                if user_id and pricing_integration.pricing_enabled:
                    # Estimate token usage
                    token_count = sum(
                        len(text.split()) * 4
                        for text in result.get("initial_responses", {}).values()
                    )
                    token_count += len(result.get("ultra_response", "").split()) * 4

                    await track_request_cost(
                        user_id=user_id,
                        request_type="analyze",
                        model=ultra_model,
                        tokens_used=token_count,
                    )

                return response

            except TypeError as e:
                # Handle specific initialization errors for different API clients
                logger.warning(f"API client initialization error: {str(e)}")

                # Filter selected_models to only include models we can initialize
                working_models = []

                # Check which models we can use based on the error
                if (
                    "AsyncClient.__init__() got an unexpected keyword argument 'proxies'"
                    in str(e)
                ):
                    logger.warning(
                        "Anthropic/Claude client incompatible - removing from available models"
                    )
                    working_models = [
                        model
                        for model in selected_models
                        if model != "claude37" and model != "claude3opus"
                    ]
                else:
                    # For other errors, assume we can use OpenAI and Gemini (but not Claude)
                    working_models = [
                        model
                        for model in selected_models
                        if not model.startswith("claude")
                    ]

                if not working_models:
                    # If no selected models can work, add a default that usually works
                    working_models = ["gpt4o"]

                # Create a simplified orchestrator
                orchestrator = PatternOrchestrator(
                    api_keys={
                        "openai": os.getenv("OPENAI_API_KEY"),
                        "google": os.getenv("GOOGLE_API_KEY"),
                    },
                    pattern=pattern_key,
                    output_format="plain",
                )

                orchestrator.ultra_model = ultra_model

                # Process with the working models
                result = await orchestrator.orchestrate_full_process(prompt)

                # Format the result
                response = {
                    "status": "success",
                    "ultra_response": result.get("ultra_response", ""),
                    "results": {
                        model: content
                        for model, content in result.get(
                            "initial_responses", {}
                        ).items()
                    },
                    "pattern": pattern_name,
                    "processing_time": time.time() - start_time,
                    "models_adjusted": True,
                    "working_models": working_models,
                }

                # Cache the response
                response_cache[cache_key] = response

                return response

        except Exception as e:
            logger.error(f"Error in pattern orchestration: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Pattern orchestration error: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing analyze request: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@analyze_router.post("/api/analyze-with-docs")
async def analyze_with_docs(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    selectedModels: str = Form(...),
    ultraModel: str = Form(...),
    files: List[UploadFile] = File([]),
    pattern: str = Form("Confidence Analysis"),
    options: str = Form("{}"),
    userId: str = Form(None),
):
    """Process documents and analyze them with models"""
    try:
        # Parse JSON strings
        try:
            selected_models = json.loads(selectedModels)
            options_dict = json.loads(options)
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Invalid JSON in selectedModels or options",
                },
            )

        # Process files if any
        if files:
            # In a real implementation, you would handle file processing
            # For now, we'll just acknowledge the files
            file_names = [file.filename for file in files]
            logger.info(f"Processing files: {', '.join(file_names)}")

        # Create a document context
        document_context = f"Analyzing with {len(files)} documents" if files else ""

        # Combine with prompt
        combined_prompt = f"{prompt}\n\n{document_context}" if document_context else prompt

        # Use the analyze endpoint to process the prompt
        # In a real implementation, you would properly process the documents
        # and incorporate their content into the analysis

        return {
            "status": "success",
            "message": "Document analysis initiated",
            "prompt": combined_prompt,
            "files_processed": len(files),
        }
    except Exception as e:
        logger.error(f"Error in analyze with docs: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error: {str(e)}"},
        )


# Second implementation of analyze that differs from the first one in main.py
@analyze_router.post("/api/analyze-legacy")
async def analyze_legacy(request: dict = Body(...)):
    """
    Analyze a prompt using multiple LLMs and an Ultra LLM (legacy implementation)
    """
    global processing_times
    start_processing = time.time()

    try:
        # Extract request parameters
        prompt = request.get("prompt", "")
        models = request.get("models", ["gpt4o", "gpt4turbo"])
        ultra_model = request.get("ultraModel", "gpt4o")
        pattern = request.get("pattern", "confidence")
        user_id = request.get("userId")
        session_id = request.get("sessionId")

        # Basic validation
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Use cache if available
        cache_key = generate_cache_key(prompt, models, ultra_model, pattern)
        cached_response = (
            response_cache.get(cache_key) if hasattr(response_cache, "get") else None
        )

        if cached_response:
            performance_metrics["cache_hits"] += 1
            logger.info(f"Cache hit for prompt: {prompt[:30]}...")
            end_processing = time.time()
            processing_time = end_processing - start_processing
            processing_times.append(processing_time)
            performance_metrics["requests_processed"] += 1
            update_metrics_history()

            return cached_response

        # Check if we should use mock
        if Config.use_mock and hasattr(Config, 'mock_service') and Config.mock_service:
            logger.info(f"Using mock service for prompt: {prompt[:30]}...")
            # Use the async analyze_prompt for consistency
            result = await Config.mock_service.analyze_prompt(
                prompt, models, ultra_model, pattern
            )

            # Cache the result
            if hasattr(response_cache, "update"):
                response_cache[cache_key] = result

            # Update metrics
            end_processing = time.time()
            processing_time = end_processing - start_processing
            processing_times.append(processing_time)
            performance_metrics["requests_processed"] += 1
            update_metrics_history()

            return result

        # Use orchestrator if available
        if ORCHESTRATOR_AVAILABLE:
            logger.info(f"Using pattern orchestrator for prompt: {prompt[:30]}...")
            # Get or create orchestrator
            orchestrator = PatternOrchestrator()
            orchestrator.ultra_model = ultra_model

            # Use the full process for better results
            result = await orchestrator.orchestrate_full_process(prompt)

            # Cache the result
            if hasattr(response_cache, "update"):
                response_cache[cache_key] = result

            # Update metrics
            end_processing = time.time()
            processing_time = end_processing - start_processing
            processing_times.append(processing_time)
            performance_metrics["requests_processed"] += 1
            update_metrics_history()

            return result

        # Fallback to basic analysis
        raise HTTPException(status_code=500, detail="No analysis service available")

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")