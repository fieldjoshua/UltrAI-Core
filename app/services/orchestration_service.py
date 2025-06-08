"""
Orchestration Service

This service coordinates multi-model and multi-stage workflows according to the UltrLLMOrchestrator patent.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from app.services.quality_evaluation import QualityEvaluationService, ResponseQuality
from app.services.rate_limiter import RateLimiter
from app.services.token_management_service import TokenManagementService
from app.services.transaction_service import TransactionService
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

        # Define pipeline stages according to patent (will be dynamically overridden)
        self.pipeline_stages = [
            PipelineStage(
                name="initial_response",
                description="Initial response generation from multiple models",
                required_models=["claude-3-haiku"],  # Default fallback
                timeout_seconds=30,
            ),
            PipelineStage(
                name="meta_analysis",
                description="Meta-analysis of initial responses",
                required_models=["claude-3-haiku"],  # Default fallback
                timeout_seconds=45,
            ),
            PipelineStage(
                name="ultra_synthesis",
                description="Ultra-synthesis of meta-analysis results",
                required_models=["claude-3-haiku"],  # Default fallback
                timeout_seconds=60,
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
                # Override models for initial_response stage if selected_models provided
                if stage.name == "initial_response" and selected_models:
                    # Create a copy of the stage with selected models
                    stage_copy = PipelineStage(
                        name=stage.name,
                        description=stage.description,
                        required_models=selected_models,
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
        
        # Try each available model
        for model in models:
            try:
                if model.startswith("gpt"):
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        logger.warning(f"No OpenAI API key found for {model}, skipping")
                        continue
                    adapter = OpenAIAdapter(api_key, model)
                    result = await adapter.generate(prompt)
                    if "Error:" not in result.get("generated_text", ""):
                        responses[model] = result.get("generated_text", "Response generated successfully")
                        logger.info(f"✅ Successfully got response from {model}")
                    else:
                        logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                        continue
                elif model.startswith("claude"):
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                    if not api_key:
                        logger.warning(f"No Anthropic API key found for {model}, skipping")
                        continue
                    adapter = AnthropicAdapter(api_key, model)
                    result = await adapter.generate(prompt)
                    if "Error:" not in result.get("generated_text", ""):
                        responses[model] = result.get("generated_text", "Response generated successfully")
                        logger.info(f"✅ Successfully got response from {model}")
                    else:
                        logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                        continue
                elif model.startswith("gemini"):
                    api_key = os.getenv("GOOGLE_API_KEY")
                    if not api_key:
                        logger.warning(f"No Google API key found for {model}, skipping")
                        continue
                    adapter = GeminiAdapter(api_key, model)
                    result = await adapter.generate(prompt)
                    if "Error:" not in result.get("generated_text", ""):
                        responses[model] = result.get("generated_text", "Response generated successfully")
                        logger.info(f"✅ Successfully got response from {model}")
                    else:
                        logger.warning(f"❌ Error response from {model}: {result.get('generated_text', '')}")
                        continue
                elif "/" in model:  # HuggingFace model ID format (org/model-name)
                    # HuggingFace models - try direct API first (free tier), then adapter if available
                    api_key = os.getenv("HUGGINGFACE_API_KEY")
                    
                    # Direct HuggingFace Inference API (works without API key on free tier)
                    try:
                        import httpx
                        
                        headers = {"Content-Type": "application/json"}
                        if api_key:
                            headers["Authorization"] = f"Bearer {api_key}"
                        
                        async with httpx.AsyncClient() as client:
                            # Enhanced prompt for better responses
                            enhanced_prompt = f"Question: {prompt}\n\nProvide a detailed, professional analysis:\n"
                            
                            hf_response = await client.post(
                                f"https://api-inference.huggingface.co/models/{model}",
                                json={
                                    "inputs": enhanced_prompt,
                                    "parameters": {
                                        "max_new_tokens": 500,
                                        "temperature": 0.7,
                                        "do_sample": True,
                                        "return_full_text": False
                                    }
                                },
                                headers=headers,
                                timeout=45.0
                            )
                            
                            if hf_response.status_code == 200:
                                hf_data = hf_response.json()
                                
                                if isinstance(hf_data, list) and len(hf_data) > 0:
                                    generated_text = hf_data[0].get('generated_text', '')
                                    # Clean up the response
                                    cleaned_response = generated_text.replace(enhanced_prompt, '').strip()
                                    if len(cleaned_response) > 20:  # Ensure substantial response
                                        responses[model] = cleaned_response
                                        logger.info(f"✅ Successfully got real response from {model} ({len(cleaned_response)} chars)")
                                        continue
                                    else:
                                        logger.warning(f"Response too short from {model}, trying fallback")
                                elif isinstance(hf_data, dict) and 'error' in hf_data:
                                    logger.warning(f"HuggingFace API error for {model}: {hf_data['error']}")
                                else:
                                    logger.warning(f"Unexpected HuggingFace response format for {model}: {type(hf_data)}")
                            elif hf_response.status_code == 503:
                                logger.warning(f"Model {model} is loading, will try adapter fallback")
                            else:
                                logger.warning(f"HuggingFace API failed for {model}: {hf_response.status_code}")
                                
                    except Exception as hf_error:
                        logger.warning(f"HuggingFace direct API error for {model}: {str(hf_error)}")
                    
                    # Fallback to adapter if direct API failed and we have an API key
                    if api_key and model not in responses:
                        try:
                            adapter = HuggingFaceAdapter(api_key, model)
                            result = await adapter.generate(prompt)
                            if "Error:" not in result.get("generated_text", ""):
                                responses[model] = result.get("generated_text", "Response generated successfully")
                                logger.info(f"✅ Successfully got response from {model} via adapter fallback")
                            else:
                                logger.warning(f"HuggingFace adapter also failed for {model}")
                        except Exception as e:
                            logger.warning(f"HuggingFace adapter failed for {model}: {str(e)}")
                    
                    # Skip if neither approach worked
                    if model not in responses:
                        logger.warning(f"All HuggingFace approaches failed for {model}")
                        continue
                else:
                    logger.warning(f"Unknown model type or no API configuration: {model}")
                    continue
            except Exception as e:
                logger.error(f"Failed to get response from {model}: {str(e)}")
                # Skip models that fail completely
                continue
        
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

    async def meta_analysis(
        self, data: Any, models: List[str], options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Meta-analysis phase - analyze and compare initial responses.

        Args:
            data: Initial responses from multiple models
            models: List of models to use for meta-analysis
            options: Additional options

        Returns:
            Any: Meta-analysis results
        """
        if not isinstance(data, dict) or 'responses' not in data:
            logger.warning("Invalid data structure for meta-analysis")
            return {"stage": "meta_analysis", "error": "Invalid input data structure"}
        
        initial_responses = data['responses']
        
        # Create meta-analysis prompt
        analysis_text = "\\n\\n".join([
            f"**{model}:** {response}" 
            for model, response in initial_responses.items()
        ])
        
        meta_prompt = f\"\"\"Several of your fellow LLMs were given the same prompt as you. Their responses are as follows. Do NOT assume that anything written is correct or properly sourced, but given these other responses, could you make your original response better? More insightful? More factual, more comprehensive when considering the initial user prompt?

Original User Prompt: {data.get('prompt', 'Unknown prompt')}

Fellow LLM Responses:
{analysis_text}

If you believe you can make a better response considering these other perspectives, please draft a new, improved response to the initial inquiry. Focus on being more comprehensive and insightful than any single response alone.

Enhanced Response:\"\"\"

        # Use the first available model for meta-analysis
        analysis_model = models[0] if models else "claude-3-haiku"
        
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
                    "source_models": list(initial_responses.keys()),
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
        if not isinstance(data, dict) or 'analysis' not in data:
            logger.warning("Invalid data structure for ultra-synthesis")
            return {"stage": "ultra_synthesis", "error": "Invalid input data structure"}
        
        meta_analysis = data['analysis']
        source_models = data.get('source_models', [])
        
        synthesis_prompt = f\"\"\"You are tasked with creating the Ultra Synthesis™: a fully-integrated intelligence synthesis that combines the relevant outputs from all methods into a cohesive whole, with recommendations that benefit from multiple cognitive frameworks. 

The objective here is not to be necessarily the best, but the most expansive synthesization of the many outputs. While you should disregard facts or analyses that are extremely anomalous or wrong, your final Ultra Synthesis should reflect all of the relevant insights from the meta-level responses, organized in a manner that is clear and non-repetitive.

Original User Prompt: {data.get('input_data', {}).get('prompt', 'Unknown prompt')}

Meta-Level Enhanced Response:
{meta_analysis}

Source Models Analyzed: {', '.join(source_models)}

Your Ultra Synthesis should maximize intelligence multiplication by leveraging the complementary strengths of different analytical approaches, resulting in insights and recommendations that no single method could produce.

Ultra Synthesis™:\"\"\"

        # Use the first available model for synthesis
        synthesis_model = models[0] if models else "claude-3-haiku"
        
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
