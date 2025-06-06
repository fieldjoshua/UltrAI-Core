"""
Basic Orchestrator - Focus on What Actually Matters

Priorities:
1. Reliability: Works every time without timeouts or failures  
2. Speed: Responses in under 10 seconds for 3-4 models
3. Simplicity: Easy to understand and modify
4. Observability: Clear logging of what's happening

This is the simplest possible orchestrator that just works.
"""
import asyncio
import time
import os
from typing import Dict, List, Any, Optional
import logging
from backend.models.llm_adapter import OpenAIAdapter, AnthropicAdapter, GeminiAdapter

logger = logging.getLogger(__name__)

# Conservative timeout - better to be slow than fail
TIMEOUT_SECONDS = 25

# Model name mappings (frontend -> backend)
MODEL_MAPPINGS = {
    "gpt4o": "gpt-4",
    "gpt4turbo": "gpt-4-turbo", 
    "claude37": "claude-3",
    "claude3opus": "claude-3-opus",
    "gemini15": "gemini-pro"
}


class BasicOrchestrator:
    """Basic orchestrator that prioritizes reliability"""
    
    def __init__(self):
        """Initialize with available LLM adapters"""
        self.adapters = {}
        self._init_adapters()
        logger.info(f"BasicOrchestrator initialized with {len(self.adapters)} providers")
    
    def _init_adapters(self):
        """Initialize adapters, continue even if some fail"""
        # OpenAI
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.adapters["openai"] = {
                    "gpt-4": OpenAIAdapter(openai_key, model="gpt-4"),
                    "gpt-4-turbo": OpenAIAdapter(openai_key, model="gpt-4-turbo-preview")
                }
                logger.info("✓ OpenAI adapters initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Anthropic
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.adapters["anthropic"] = {
                    "claude-3": AnthropicAdapter(anthropic_key, model="claude-3-sonnet-20241022"),
                    "claude-3-opus": AnthropicAdapter(anthropic_key, model="claude-3-opus-20240229")
                }
                logger.info("✓ Anthropic adapters initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic: {e}")
        
        # Google
        try:
            google_key = os.getenv("GOOGLE_API_KEY")
            if google_key:
                self.adapters["google"] = {
                    "gemini-pro": GeminiAdapter(google_key, model="gemini-1.5-pro")
                }
                logger.info("✓ Google adapters initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Google: {e}")
    
    def _get_adapter(self, frontend_model: str):
        """Get adapter for a model, with clear error handling"""
        backend_model = MODEL_MAPPINGS.get(frontend_model, frontend_model)
        
        for provider, models in self.adapters.items():
            if backend_model in models:
                return models[backend_model], provider
        
        logger.warning(f"No adapter for {frontend_model} (mapped to {backend_model})")
        return None, None
    
    async def _call_model_safely(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """Call a model with proper timeout and error handling"""
        start_time = time.time()
        
        adapter, provider = self._get_adapter(model_name)
        if not adapter:
            return {
                "model": model_name,
                "response": f"Model {model_name} not available",
                "error": True,
                "time": 0
            }
        
        try:
            # Log what we're doing
            logger.info(f"Calling {model_name} via {provider}")
            
            # Call with timeout
            result = await asyncio.wait_for(
                adapter.generate(prompt),
                timeout=TIMEOUT_SECONDS
            )
            
            elapsed = time.time() - start_time
            logger.info(f"✓ {model_name} responded in {elapsed:.1f}s")
            
            return {
                "model": model_name,
                "response": result.get("generated_text", "No response generated"),
                "error": False,
                "time": elapsed
            }
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            logger.warning(f"✗ {model_name} timed out after {elapsed:.1f}s")
            return {
                "model": model_name,
                "response": f"Request timed out after {TIMEOUT_SECONDS} seconds",
                "error": True,
                "time": elapsed
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"✗ {model_name} error: {str(e)}")
            return {
                "model": model_name,
                "response": f"Error: {str(e)}",
                "error": True,
                "time": elapsed
            }
    
    async def orchestrate_basic(
        self, 
        prompt: str, 
        models: List[str],
        combine: bool = True
    ) -> Dict[str, Any]:
        """
        Basic orchestration - just call models in parallel and combine.
        
        Args:
            prompt: The user's prompt
            models: List of model names to use
            combine: Whether to combine responses into one
            
        Returns:
            Dict with responses and performance data
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        
        if not models:
            models = ["gpt4o", "claude37"]  # Sensible defaults
            logger.info(f"No models specified, using defaults: {models}")
        
        start_time = time.time()
        logger.info(f"Starting basic orchestration with {len(models)} models")
        
        # Call all models in parallel
        tasks = []
        for model in models:
            task = self._call_model_safely(model, prompt)
            tasks.append(task)
        
        # Wait for all responses
        results = await asyncio.gather(*tasks)
        
        # Build response dict
        model_responses = {}
        model_times = {}
        successful_responses = []
        
        for result in results:
            model_name = result["model"]
            model_responses[model_name] = result["response"]
            model_times[model_name] = result["time"]
            
            if not result["error"]:
                successful_responses.append(result["response"])
        
        # Simple combination if requested
        combined_response = ""
        if combine and successful_responses:
            if len(successful_responses) == 1:
                combined_response = successful_responses[0]
            else:
                combined_response = f"Based on {len(successful_responses)} model responses:\n\n"
                for i, resp in enumerate(successful_responses, 1):
                    combined_response += f"Model {i}:\n{resp}\n\n"
        
        total_time = time.time() - start_time
        logger.info(f"Orchestration completed in {total_time:.1f}s")
        
        return {
            "status": "success" if successful_responses else "error",
            "model_responses": model_responses,
            "combined_response": combined_response,
            "performance": {
                "total_time_seconds": total_time,
                "model_times": model_times,
                "successful_models": len(successful_responses),
                "failed_models": len(results) - len(successful_responses)
            }
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their status"""
        available = []
        
        for provider, models in self.adapters.items():
            for backend_name in models.keys():
                # Find frontend name
                frontend_name = None
                for fn, bn in MODEL_MAPPINGS.items():
                    if bn == backend_name:
                        frontend_name = fn
                        break
                
                available.append({
                    "id": frontend_name or backend_name,
                    "provider": provider,
                    "backend_name": backend_name,
                    "available": True
                })
        
        return available