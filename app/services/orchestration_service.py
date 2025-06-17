"""
Orchestration Service

This service coordinates multi-model and multi-stage workflows according to the UltrLLMOrchestrator patent.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import os
import json
from pathlib import Path

from app.services.quality_evaluation import QualityEvaluationService, ResponseQuality
from app.services.rate_limiter import RateLimiter
from app.services.token_management_service import TokenManagementService
from app.services.transaction_service import TransactionService
from app.services.llm_adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter, HuggingFaceAdapter
from app.utils.logging import get_logger

logger = get_logger("orchestration_service")


@dataclass
class PipelineStage:
    """Configuration for a pipeline stage."""

    name: str
    description: str
    required_models: List[str]
    timeout_seconds: int = 30


@dataclass
class PipelineResult:
    """Result from a pipeline stage."""

    stage_name: str
    output: Any
    quality: Optional[ResponseQuality] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None


class OrchestrationService:
    """
    Service for orchestrating multi-stage analysis pipelines.
    """

    def __init__(
        self,
        model_registry: Any,
        quality_evaluator: Optional[QualityEvaluationService] = None,
        rate_limiter: Optional[RateLimiter] = None,
        token_manager: Optional[TokenManagementService] = None,
        transaction_service: Optional[TransactionService] = None,
    ):
        """
        Initialize the orchestration service.

        Args:
            model_registry: The model registry service
            quality_evaluator: Optional quality evaluation service
            rate_limiter: Optional rate limiter service
            token_manager: Optional token management service
            transaction_service: Optional transaction service
        """
        self.model_registry = model_registry
        self.quality_evaluator = quality_evaluator or QualityEvaluationService()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.token_manager = token_manager or TokenManagementService()
        self.transaction_service = transaction_service or TransactionService()

        # Define pipeline stages according to correct Ultra Synthesis™ architecture
        self.pipeline_stages = [
            PipelineStage(
                name="initial_response",
                description="Initial response generation from multiple models in parallel",
                required_models=[],  # Uses user-selected models
                timeout_seconds=60,
            ),
            PipelineStage(
                name="peer_review_and_revision", 
                description="Each model reviews peer responses and revises their own answer",
                required_models=[],  # Uses same models as initial_response
                timeout_seconds=90,
            ),
            PipelineStage(
                name="meta_analysis",
                description="Meta-analysis of peer-revised responses",
                required_models=[],  # Uses lead model from selection
                timeout_seconds=60,
            ),
            PipelineStage(
                name="ultra_synthesis",
                description="Ultra-synthesis of meta-analysis results for final intelligence multiplication",
                required_models=[],  # Uses lead model from selection
                timeout_seconds=90,
            ),
        ]

    async def run_pipeline(
        self,
        input_data: Any,
        options: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        selected_models: Optional[List[str]] = None,
    ) -> Dict[str, PipelineResult]:
        """
        Run the full analysis pipeline according to the patent specification.

        Args:
            input_data: The input data for analysis
            options: Additional options for the pipeline
            user_id: Optional user ID for cost tracking

        Returns:
            Dict[str, PipelineResult]: Results from each pipeline stage
        """
        results = {}
        current_data = input_data
        total_cost = 0.0

        for stage in self.pipeline_stages:
            try:
                # Override models for stages that use selected_models
                if stage.name in ["initial_response", "peer_review_and_revision"] and selected_models:
                    # Create a copy of the stage with selected models
                    stage_copy = PipelineStage(
                        name=stage.name,
                        description=stage.description,
                        required_models=selected_models,
                        timeout_seconds=stage.timeout_seconds
                    )
                    stage_result = await self._run_stage(stage_copy, current_data, options)
                elif stage.name in ["meta_analysis", "ultra_synthesis"] and selected_models:
                    # Use lead model for synthesis stages
                    lead_model = selected_models[0] if selected_models else "gpt-4"
                    stage_copy = PipelineStage(
                        name=stage.name,
                        description=stage.description,
                        required_models=[lead_model],
                        timeout_seconds=stage.timeout_seconds
                    )
                    stage_result = await self._run_stage(stage_copy, current_data, options)
                else:
                    # Use original stage configuration
                    stage_result = await self._run_stage(stage, current_data, options)
                
                results[stage.name] = stage_result

                if stage_result.error:
                    logger.error(f"Error in {stage.name}: {stage_result.error}")
                    break

                # Track token usage and costs if user_id is provided
                if user_id and stage_result.token_usage:
                    for model, usage in stage_result.token_usage.items():
                        cost = await self.token_manager.track_usage(
                            model=model,
                            input_tokens=usage.get("input", 0),
                            output_tokens=usage.get("output", 0),
                            user_id=user_id,
                        )
                        total_cost += cost.total_cost

                # Update data for next stage
                current_data = stage_result.output

            except Exception as e:
                logger.error(f"Pipeline failed at {stage.name}: {str(e)}")
                results[stage.name] = PipelineResult(
                    stage_name=stage.name, output=None, error=str(e)
                )
                break

        # Deduct total cost from user's balance if user_id is provided
        if user_id and total_cost > 0:
            await self.transaction_service.deduct_cost(
                user_id=user_id,
                amount=total_cost,
                description=f"Pipeline execution cost: {', '.join(results.keys())}",
            )

        # Save pipeline outputs if requested in options
        save_outputs = options.get('save_outputs', False) if options else False
        saved_files = {}
        if save_outputs:
            saved_files = await self._save_pipeline_outputs(results, input_data, selected_models, user_id)

        # Add saved files info to results metadata
        if saved_files:
            results['_metadata'] = {
                'saved_files': saved_files,
                'save_outputs_requested': save_outputs
            }

        return results

    async def _run_stage(
        self,
        stage: PipelineStage,
        input_data: Any,
        options: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Run a single pipeline stage.

        Args:
            stage: The pipeline stage configuration
            input_data: Input data for the stage
            options: Additional options

        Returns:
            PipelineResult: Result from the stage
        """
        start_time = datetime.now()
        stage_output = None
        quality = None
        error = None
        token_usage = {}

        try:
            # Acquire rate limit tokens for all required models
            for model in stage.required_models:
                # Register model in rate limiter if not already registered
                try:
                    await self.rate_limiter.acquire(model)
                except ValueError as e:
                    if "not registered" in str(e):
                        # Register the model with default rate limits
                        self.rate_limiter.register_endpoint(model, requests_per_minute=60, burst_limit=10)
                        await self.rate_limiter.acquire(model)
                    else:
                        raise

            # Get the stage method
            method = getattr(self, stage.name, None)
            if not callable(method):
                raise ValueError(f"Stage method {stage.name} not found")

            # Run the stage
            stage_output = await method(input_data, stage.required_models, options)

            # Track token usage if available
            if hasattr(stage_output, "token_usage"):
                token_usage = stage_output.token_usage

            # Evaluate quality if evaluator is available
            if self.quality_evaluator:
                quality = await self.quality_evaluator.evaluate_response(
                    str(stage_output), context={"stage": stage.name, "options": options}
                )

        except Exception as e:
            error = str(e)
            logger.error(f"Error in {stage.name}: {error}")

        finally:
            # Release rate limit tokens
            for model in stage.required_models:
                await self.rate_limiter.release(model, success=error is None)

        # Calculate performance metrics
        duration = (datetime.now() - start_time).total_seconds()
        performance_metrics = {
            "duration_seconds": duration,
            "success": error is None,
            "rate_limit_stats": {
                model: self.rate_limiter.get_endpoint_stats(model)
                for model in stage.required_models
            },
        }

        return PipelineResult(
            stage_name=stage.name,
            output=stage_output,
            quality=quality,
            performance_metrics=performance_metrics,
            error=error,
            token_usage=token_usage,
        )

    async def initial_response(
        self, data: Any, models: List[str], options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Initial response generation stage.

        Args:
            data: Input data
            models: List of models to use
            options: Additional options

        Returns:
            Any: Initial responses from all models
        """
        import os
        from app.services.llm_adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter, HuggingFaceAdapter
        
        responses = {}
        prompt = f"Analyze the following query and provide insights: {data}"
        
        # Create model execution tasks for concurrent processing
        async def execute_model(model: str) -> tuple[str, dict]:
            """Execute a single model and return (model_name, result)"""
            try:
                if model.startswith("gpt") or model.startswith("o1"):
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        logger.warning(f"No OpenAI API key found for {model}, skipping")
                        return model, {"error": "No API key"}
                    adapter = OpenAIAdapter(api_key, model)
                    result = await adapter.generate(prompt)
                    if "Error:" not in result.get("generated_text", ""):
                        logger.info(f"✅ Successfully got response from {model}")
                        return model, {"generated_text": result.get("generated_text", "Response generated successfully")}
                    else:
                        logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                        return model, {"error": result.get("generated_text", "")}
                elif model.startswith("claude"):
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                    if not api_key:
                        logger.warning(f"No Anthropic API key found for {model}, skipping")
                        return model, {"error": "No API key"}
                    # Fix model name mapping for Anthropic
                    mapped_model = model
                    if model == "claude-3-sonnet":
                        mapped_model = "claude-3-sonnet-20240229"
                    elif model == "claude-3-5-sonnet-20241022":
                        mapped_model = "claude-3-5-sonnet-20241022"
                    elif model == "claude-3-5-haiku-20241022":
                        mapped_model = "claude-3-5-haiku-20241022"
                    adapter = AnthropicAdapter(api_key, mapped_model)
                    result = await adapter.generate(prompt)
                    if "Error:" not in result.get("generated_text", ""):
                        logger.info(f"✅ Successfully got response from {model}")
                        return model, {"generated_text": result.get("generated_text", "Response generated successfully")}
                    else:
                        logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                        return model, {"error": result.get("generated_text", "")}
                elif model.startswith("gemini"):
                    api_key = os.getenv("GOOGLE_API_KEY")
                    if not api_key:
                        logger.warning(f"No Google API key found for {model}, skipping")
                        return model, {"error": "No API key"}
                    # Fix model name mapping for Gemini
                    mapped_model = model
                    if model == "gemini-pro":
                        mapped_model = "gemini-1.5-pro"
                    elif model == "gemini-2.0-flash-exp":
                        mapped_model = "gemini-2.0-flash-exp"
                    elif model == "gemini-1.5-pro":
                        mapped_model = "gemini-1.5-pro"
                    elif model == "gemini-1.5-flash":
                        mapped_model = "gemini-1.5-flash"
                    adapter = GeminiAdapter(api_key, mapped_model)
                    result = await adapter.generate(prompt)
                    if "Error:" not in result.get("generated_text", ""):
                        logger.info(f"✅ Successfully got response from {model}")
                        return model, {"generated_text": result.get("generated_text", "Response generated successfully")}
                    else:
                        logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                        return model, {"error": result.get("generated_text", "")}
                elif "/" in model:  # HuggingFace model ID format (org/model-name)
                    # HuggingFace models - require API key for real responses
                    api_key = os.getenv("HUGGINGFACE_API_KEY")
                    
                    if not api_key:
                        logger.error(f"HuggingFace API key required for {model}. Set HUGGINGFACE_API_KEY environment variable.")
                        return model, {"error": "No API key"}
                    
                    try:
                        adapter = HuggingFaceAdapter(api_key, model)
                        result = await adapter.generate(prompt)
                        if "Error:" not in result.get("generated_text", ""):
                            logger.info(f"✅ Successfully got response from {model}")
                            return model, {"generated_text": result.get("generated_text", "Response generated successfully")}
                        else:
                            logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                            return model, {"error": result.get("generated_text", "")}
                    except Exception as e:
                        logger.error(f"HuggingFace adapter failed for {model}: {str(e)}")
                        return model, {"error": str(e)}
                else:
                    logger.warning(f"Unknown model type or no API configuration: {model}")
                    return model, {"error": "Unknown model type"}
            except Exception as e:
                logger.error(f"Failed to get response from {model}: {str(e)}")
                return model, {"error": str(e)}

        # Execute all models concurrently
        logger.info(f"🚀 Starting concurrent execution of {len(models)} models: {models}")
        tasks = [execute_model(model) for model in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and collect successful responses
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task execution failed: {str(result)}")
                continue
            
            model, output = result
            if "generated_text" in output:
                responses[model] = output["generated_text"]
            else:
                logger.warning(f"Model {model} failed: {output.get('error', 'Unknown error')}")
        
        # Only return results if we have at least one real response
        if not responses:
            error_msg = f"No models generated responses from {len(models)} attempted models: {models}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"✅ Real responses from {len(responses)}/{len(models)} models: {list(responses.keys())}")
        
        # Log sample of responses for verification
        for model, response in responses.items():
            sample = response[:100] + "..." if len(response) > 100 else response
            logger.info(f"  {model}: {sample}")
        
        return {
            "stage": "initial_response",
            "responses": responses,
            "prompt": prompt,
            "models_attempted": models,
            "successful_models": list(responses.keys()),
            "response_count": len(responses)
        }

    async def peer_review_and_revision(
        self, data: Any, models: List[str], options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Peer review and revision phase - each model reviews peer responses and revises their own answer.
        
        This is the core of the Ultra Synthesis™ collaborative intelligence architecture.
        Each model sees what their peers said and has the opportunity to improve their own response.
        """
        logger.info(f"🔄 Starting peer review and revision with {len(models)} models")
        
        # Extract initial responses from previous stage
        if not isinstance(data, dict) or "responses" not in data:
            logger.error(f"Invalid data for peer review - expected dict with 'responses', got: {type(data)}")
            return {"stage": "peer_review_and_revision", "error": "Invalid input data - missing initial responses"}
        
        initial_responses = data["responses"]
        original_prompt = data.get("prompt", "Unknown query")
        successful_models = data.get("successful_models", [])
        
        logger.info(f"Initial responses from: {list(initial_responses.keys())}")
        
        # Only process models that succeeded in the initial response stage
        working_models = [model for model in models if model in successful_models]
        
        if not working_models:
            logger.warning("No working models available for peer review")
            return {
                "stage": "peer_review_and_revision", 
                "error": "No models available for peer review",
                "original_responses": initial_responses
            }
        
        logger.info(f"Processing peer review for: {working_models}")
        
        # Create peer review tasks for each working model
        async def create_peer_review_task(model: str) -> tuple[str, dict]:
            """Create peer review prompt and get revised response for a specific model."""
            try:
                # Get the model's original response
                own_response = initial_responses[model]
                
                # Create peer responses section (excluding the model's own response)
                peer_responses_text = ""
                for peer_model, peer_response in initial_responses.items():
                    if peer_model != model:  # Don't include the model's own response as a "peer"
                        peer_responses_text += f"\n{peer_model}: {peer_response}\n"
                
                # Create the peer review prompt
                peer_review_prompt = f"""Original Query: {original_prompt}

Your Original Response:
{own_response}

Peer Responses from Other Models:
{peer_responses_text}

Instructions: You have now seen how other AI models responded to the same query. Do not assume that the peer responses are necessarily factually accurate, but having seen these other versions, do you have any edits you want to make to your original draft to make it stronger, more accurate, or more comprehensive?

Please provide your revised response. If you believe your original response was already optimal, you may keep it unchanged, but please explain briefly why you think it stands well against the peer responses."""

                # Execute the peer review using the same model adapters as initial_response
                if model.startswith("gpt") or model.startswith("o1"):
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        return model, {"error": "No OpenAI API key"}
                    adapter = OpenAIAdapter(api_key, model)
                    result = await adapter.generate(peer_review_prompt)
                    
                elif model.startswith("claude"):
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                    if not api_key:
                        return model, {"error": "No Anthropic API key"}
                    # Fix model name mapping for Anthropic
                    mapped_model = model
                    if model == "claude-3-sonnet":
                        mapped_model = "claude-3-sonnet-20240229"
                    elif model == "claude-3-5-sonnet-20241022":
                        mapped_model = "claude-3-5-sonnet-20241022"
                    elif model == "claude-3-5-haiku-20241022":
                        mapped_model = "claude-3-5-haiku-20241022"
                    adapter = AnthropicAdapter(api_key, mapped_model)
                    result = await adapter.generate(peer_review_prompt)
                    
                elif model.startswith("gemini"):
                    api_key = os.getenv("GOOGLE_API_KEY")
                    if not api_key:
                        return model, {"error": "No Google API key"}
                    # Fix model name mapping for Gemini
                    mapped_model = model
                    if model == "gemini-pro":
                        mapped_model = "gemini-1.5-pro"
                    elif model == "gemini-2.0-flash-exp":
                        mapped_model = "gemini-2.0-flash-exp"
                    elif model == "gemini-1.5-pro":
                        mapped_model = "gemini-1.5-pro"
                    elif model == "gemini-1.5-flash":
                        mapped_model = "gemini-1.5-flash"
                    adapter = GeminiAdapter(api_key, mapped_model)
                    result = await adapter.generate(peer_review_prompt)
                    
                elif "/" in model:  # HuggingFace model
                    api_key = os.getenv("HUGGINGFACE_API_KEY")
                    if not api_key:
                        return model, {"error": "No HuggingFace API key"}
                    adapter = HuggingFaceAdapter(api_key, model)
                    result = await adapter.generate(peer_review_prompt)
                    
                else:
                    return model, {"error": "Unknown model type"}
                
                # Check for successful response
                if "Error:" not in result.get("generated_text", ""):
                    logger.info(f"✅ {model} completed peer review")
                    return model, {"revised_text": result.get("generated_text", "")}
                else:
                    logger.warning(f"❌ {model} peer review failed: {result.get('generated_text', '')}")
                    return model, {"error": result.get("generated_text", ""), "fallback_response": own_response}
                    
            except Exception as e:
                logger.error(f"Peer review failed for {model}: {str(e)}")
                return model, {"error": str(e), "fallback_response": initial_responses.get(model, "")}
        
        # Execute peer review for all working models concurrently
        logger.info(f"🚀 Starting concurrent peer review for {len(working_models)} models")
        tasks = [create_peer_review_task(model) for model in working_models]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        revised_responses = {}
        successful_revisions = []
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Peer review task failed: {str(result)}")
                continue
            
            model, output = result
            if "revised_text" in output:
                revised_responses[model] = output["revised_text"]
                successful_revisions.append(model)
                logger.info(f"✅ {model} provided revised response")
            elif "fallback_response" in output:
                # Use original response if revision failed
                revised_responses[model] = output["fallback_response"]
                logger.warning(f"⚠️ {model} revision failed, using original response")
            else:
                logger.warning(f"❌ {model} peer review completely failed: {output.get('error', 'Unknown error')}")
        
        if not revised_responses:
            logger.error("No models completed peer review successfully")
            return {
                "stage": "peer_review_and_revision",
                "error": "All peer review attempts failed",
                "original_responses": initial_responses
            }
        
        logger.info(f"✅ Peer review completed for {len(revised_responses)}/{len(working_models)} models")
        
        # Log sample of revised responses
        for model, response in revised_responses.items():
            sample = response[:100] + "..." if len(response) > 100 else response
            logger.info(f"  {model} revised: {sample}")
        
        return {
            "stage": "peer_review_and_revision",
            "original_responses": initial_responses,
            "revised_responses": revised_responses,
            "models_with_revisions": successful_revisions,
            "models_attempted": working_models,
            "successful_models": list(revised_responses.keys()),
            "revision_count": len(revised_responses)
        }

    async def meta_analysis(
        self, data: Any, models: List[str], options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Meta-analysis phase - analyze and synthesize peer-revised responses.

        Args:
            data: Peer review results containing revised responses
            models: List of models to use for meta-analysis (typically lead model)
            options: Additional options

        Returns:
            Any: Meta-analysis results
        """
        # Debug: log the data structure we received
        logger.info(f"🔍 Meta-analysis received data type: {type(data)}")
        if isinstance(data, dict):
            logger.info(f"🔍 Meta-analysis data keys: {list(data.keys())}")
        
        # Handle both peer review results and fallback to initial responses
        if isinstance(data, dict) and 'revised_responses' in data:
            # New architecture: use peer-revised responses
            responses_to_analyze = data['revised_responses']
            # Try to get original prompt from nested original_responses, fallback to top level
            if 'original_responses' in data and isinstance(data['original_responses'], dict):
                original_prompt = data['original_responses'].get('prompt', 'Unknown prompt')
            else:
                original_prompt = 'Unknown prompt'
            logger.info(f"✅ Meta-analysis using {len(responses_to_analyze)} peer-revised responses")
            logger.info(f"🔍 Models in revised responses: {list(responses_to_analyze.keys())}")
        elif isinstance(data, dict) and 'responses' in data:
            # Fallback: if peer review failed, use initial responses
            responses_to_analyze = data['responses'] 
            original_prompt = data.get('prompt', 'Unknown prompt')
            logger.warning("⚠️ Meta-analysis falling back to initial responses (peer review may have failed)")
        else:
            logger.error(f"❌ Invalid data structure for meta-analysis. Data: {data}")
            return {"stage": "meta_analysis", "error": "Invalid input data structure"}
        
        # Create meta-analysis prompt using the revised/available responses
        analysis_text = "\\n\\n".join([
            f"**{model}:** {response}" 
            for model, response in responses_to_analyze.items()
        ])
        
        meta_prompt = f"""META-ANALYSIS TASK

You are conducting a meta-analysis of multiple AI responses to synthesize the best insights. Your goal is to create an enhanced response that's better than any individual response.

Original User Query: {original_prompt}

AI Model Responses to Analyze:
{analysis_text}

Your Task: 
1. Identify the strongest insights, facts, and perspectives from across all responses
2. Note any contradictions or gaps in the responses  
3. Create an improved, comprehensive response that incorporates the best elements
4. Do NOT simply describe what each model said - instead, integrate their insights into a cohesive answer

Focus on substance and accuracy. If responses contradict each other, use your knowledge to resolve conflicts.

Write a direct, comprehensive answer to the original query that synthesizes the best insights:"""

        # Use the first available model for meta-analysis
        analysis_model = models[0] if models else "claude-3-5-sonnet-20241022"
        
        try:
            # Call the same model infrastructure as initial_response
            meta_result = await self.initial_response(meta_prompt, [analysis_model], options)
            
            if 'responses' in meta_result and meta_result['responses']:
                meta_response = list(meta_result['responses'].values())[0]
                logger.info(f"✅ Meta-analysis completed using {analysis_model}")
                
                return {
                    "stage": "meta_analysis",
                    "analysis": meta_response,
                    "model_used": analysis_model,
                    "source_models": list(responses_to_analyze.keys()),
                    "input_data": data
                }
            else:
                logger.warning("Meta-analysis failed to generate response")
                return {"stage": "meta_analysis", "error": "Failed to generate meta-analysis"}
                
        except Exception as e:
            logger.error(f"Meta-analysis error: {str(e)}")
            return {"stage": "meta_analysis", "error": str(e)}

    async def ultra_synthesis(
        self, data: Any, models: List[str], options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Ultra-synthesis stage - final comprehensive synthesis.

        Args:
            data: Meta-analysis results
            models: List of models to use
            options: Additional options

        Returns:
            Any: Ultra-synthesis results
        """
        # Handle failed meta-analysis by checking if there's an error
        if not isinstance(data, dict):
            logger.warning("Invalid data structure for ultra-synthesis - not a dict")
            return {"stage": "ultra_synthesis", "error": "Invalid input data structure"}
        
        # Debug: log what ultra-synthesis received
        logger.info(f"🔍 Ultra-synthesis received data type: {type(data)}")
        logger.info(f"🔍 Ultra-synthesis data keys: {list(data.keys())}")
        if 'analysis' in data:
            logger.info(f"🔍 Analysis length: {len(str(data['analysis']))}")
        if 'error' in data:
            logger.info(f"🔍 Error present: {data['error']}")
        
        # Check if this has a valid meta-analysis
        if 'analysis' in data and data['analysis']:
            # Normal case - meta-analysis succeeded and we have the analysis
            meta_analysis = data['analysis']
            source_models = data.get('source_models', [])
            logger.info("✅ Using meta-analysis for Ultra Synthesis")
        elif 'error' in data and data.get('error'):
            logger.warning(f"Meta-analysis failed: {data['error']}, cannot proceed with ultra-synthesis")
            return {"stage": "ultra_synthesis", "error": f"Cannot synthesize due to meta-analysis failure: {data['error']}"}
        elif 'input_data' in data and isinstance(data['input_data'], dict) and 'responses' in data['input_data']:
            # Emergency fallback: use initial responses directly (should rarely happen)
            logger.warning("⚠️ Emergency fallback: synthesizing directly from initial responses")
            initial_responses = data['input_data']['responses']
            analysis_text = "\\n\\n".join([
                f"**{model}:** {response}" 
                for model, response in initial_responses.items()
            ])
            meta_analysis = f"Multiple AI responses:\\n{analysis_text}"
            source_models = list(initial_responses.keys())
        else:
            logger.warning(f"Invalid data structure for ultra-synthesis - data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            return {"stage": "ultra_synthesis", "error": f"Invalid input data structure - missing analysis. Available keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}"}
        
        # Extract the original prompt properly
        original_prompt = "Unknown prompt"
        if 'input_data' in data:
            if isinstance(data['input_data'], dict):
                if 'prompt' in data['input_data']:
                    original_prompt = data['input_data']['prompt']
                elif 'revised_responses' in data['input_data']:
                    # Get from peer review stage
                    peer_data = data['input_data']
                    if 'original_responses' in peer_data and isinstance(peer_data['original_responses'], dict):
                        original_prompt = peer_data['original_responses'].get('prompt', original_prompt)

        logger.info(f"Ultra Synthesis using original prompt: {original_prompt[:100]}...")
        logger.info(f"Meta-analysis length: {len(str(meta_analysis))}")
        logger.info(f"Source models: {source_models}")

        synthesis_prompt = f"""ULTRA SYNTHESIS™ TASK

You must create a single, comprehensive response that synthesizes insights from multiple AI models. This is NOT a comparison or summary - it's a unified answer.

CRITICAL INSTRUCTIONS:
- DO NOT list different model responses
- DO NOT copy-paste any individual response 
- DO NOT describe what other models said
- CREATE a single, coherent answer that incorporates the best insights
- Answer as if YOU are the expert, not as if you're reporting what others said

Original User Query: {original_prompt}

Meta-Analysis of Peer-Reviewed AI Responses:
{meta_analysis}

Your task: Write a direct, comprehensive answer to the user's original query. Use the meta-analysis as background knowledge, but respond in your own voice as a unified perspective. 

Begin your response immediately with content that answers the user's question - no preamble about synthesis or other models.

Response:"""

        # Use the first available model for synthesis
        synthesis_model = models[0] if models else "claude-3-5-sonnet-20241022"
        
        try:
            # Call the model infrastructure
            synthesis_result = await self.initial_response(synthesis_prompt, [synthesis_model], options)
            
            if 'responses' in synthesis_result and synthesis_result['responses']:
                synthesis_response = list(synthesis_result['responses'].values())[0]
                logger.info(f"✅ Ultra-synthesis completed using {synthesis_model}")
                
                return {
                    "stage": "ultra_synthesis",
                    "synthesis": synthesis_response,
                    "model_used": synthesis_model,
                    "meta_analysis": meta_analysis,
                    "source_models": source_models
                }
            else:
                logger.warning("Ultra-synthesis failed to generate response")
                return {"stage": "ultra_synthesis", "error": "Failed to generate synthesis"}
                
        except Exception as e:
            logger.error(f"Ultra-synthesis error: {str(e)}")
            return {"stage": "ultra_synthesis", "error": str(e)}

    async def hyper_level_analysis(
        self, data: Any, models: List[str], options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Hyper-level analysis stage.

        Args:
            data: Ultra-synthesis results
            models: List of models to use
            options: Additional options

        Returns:
            Any: Final hyper-level analysis
        """
        # TODO: Implement hyper-level analysis
        return {"stage": "hyper_level_analysis", "input": data}

    async def _save_pipeline_outputs(
        self, 
        results: Dict[str, Any], 
        input_data: Any, 
        selected_models: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save pipeline outputs as JSON and TXT files.
        
        Args:
            results: Pipeline results to save
            input_data: Original input data
            selected_models: Models used in the pipeline
            user_id: Optional user ID for file naming
            
        Returns:
            Dict[str, str]: Paths to the saved files (json_file, txt_file)
        """
        try:
            # Create outputs directory if it doesn't exist
            outputs_dir = Path("pipeline_outputs")
            outputs_dir.mkdir(exist_ok=True)
            
            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            user_prefix = f"{user_id}_" if user_id else ""
            base_filename = f"{user_prefix}pipeline_{timestamp}"
            
            # Prepare data for saving
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "input_query": str(input_data),
                "selected_models": selected_models or [],
                "pipeline_results": {}
            }
            
            # Extract readable results from each stage
            for stage_name, stage_result in results.items():
                if hasattr(stage_result, 'output') and stage_result.output:
                    save_data["pipeline_results"][stage_name] = {
                        "stage": stage_name,
                        "output": stage_result.output,
                        "success": stage_result.error is None,
                        "error": stage_result.error,
                        "performance": stage_result.performance_metrics
                    }
                else:
                    save_data["pipeline_results"][stage_name] = {
                        "stage": stage_name,
                        "output": stage_result,
                        "success": True,
                        "error": None
                    }
            
            # Save as JSON
            json_file = outputs_dir / f"{base_filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Save as readable TXT
            txt_file = outputs_dir / f"{base_filename}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ULTRA SYNTHESIS™ PIPELINE RESULTS\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Timestamp: {save_data['timestamp']}\n")
                f.write(f"Input Query: {save_data['input_query']}\n")
                f.write(f"Selected Models: {', '.join(save_data['selected_models'])}\n\n")
                
                # Write each stage output
                for stage_name, stage_data in save_data["pipeline_results"].items():
                    f.write("-" * 60 + "\n")
                    f.write(f"STAGE: {stage_name.upper()}\n")
                    f.write("-" * 60 + "\n")
                    
                    if stage_data.get("error"):
                        f.write(f"ERROR: {stage_data['error']}\n\n")
                    else:
                        output = stage_data.get("output", {})
                        
                        # Handle different output formats
                        if isinstance(output, dict):
                            if stage_name == "initial_response" and "responses" in output:
                                f.write("INITIAL RESPONSES:\n")
                                for model, response in output["responses"].items():
                                    f.write(f"\n{model}:\n{response}\n")
                            elif stage_name == "peer_review_and_revision" and "revised_responses" in output:
                                f.write("PEER-REVISED RESPONSES:\n")
                                for model, response in output["revised_responses"].items():
                                    f.write(f"\n{model} (Revised):\n{response}\n")
                            elif stage_name == "meta_analysis" and "analysis" in output:
                                f.write("META-ANALYSIS:\n")
                                f.write(f"{output['analysis']}\n")
                            elif stage_name == "ultra_synthesis" and "synthesis" in output:
                                f.write("ULTRA SYNTHESIS™:\n")
                                f.write(f"{output['synthesis']}\n")
                            else:
                                f.write(f"OUTPUT:\n{json.dumps(output, indent=2, default=str)}\n")
                        else:
                            f.write(f"OUTPUT:\n{str(output)}\n")
                    
                    f.write("\n")
            
            logger.info(f"✅ Pipeline outputs saved:")
            logger.info(f"   JSON: {json_file}")
            logger.info(f"   TXT:  {txt_file}")
            
            return {
                "json_file": str(json_file),
                "txt_file": str(txt_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to save pipeline outputs: {str(e)}")
            # Don't raise the exception - saving is optional
            return {}
