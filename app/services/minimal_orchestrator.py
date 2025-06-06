"""
Minimal Orchestrator - Drop-in replacement implementing Ultra Synthesis™

This orchestrator implements the three-stage process:
1. Initial: Models respond independently
2. Meta: Models see each other's responses and can improve
3. Ultra: One model synthesizes all meta responses
"""

import asyncio
import time
import os
from typing import Dict, List, Any, Optional
import logging
from app.services.llm_adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter

logger = logging.getLogger(__name__)

# Timeout for individual model calls
TIMEOUT_SECONDS = 30


class MinimalOrchestrator:
    """Minimal orchestrator implementing Ultra Synthesis"""

    def __init__(self):
        """Initialize orchestrator with LLM clients"""
        self.adapters = {}
        self._init_adapters()

        # Model name mappings (frontend -> backend)
        self.model_mappings = {
            "gpt4o": "gpt-4",
            "gpt4turbo": "gpt-4-turbo",
            "claude37": "claude-3",
            "claude3opus": "claude-3-opus",
            "gemini15": "gemini-pro",
            "llama3": "llama-3",  # If we add Llama support
        }

    def _init_adapters(self):
        """Initialize LLM adapters based on available API keys"""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.adapters["openai"] = {
                "gpt-4": OpenAIAdapter(api_key=openai_key, model="gpt-4"),
                "gpt-4-turbo": OpenAIAdapter(
                    api_key=openai_key, model="gpt-4-turbo-preview"
                ),
            }
            logger.info("OpenAI adapters initialized")

        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.adapters["anthropic"] = {
                "claude-3": AnthropicAdapter(
                    api_key=anthropic_key, model="claude-3-sonnet-20240229"
                ),
                "claude-3-opus": AnthropicAdapter(
                    api_key=anthropic_key, model="claude-3-opus-20240229"
                ),
            }
            logger.info("Anthropic adapters initialized")

        # Google
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            self.adapters["google"] = {
                "gemini-pro": GeminiAdapter(
                    api_key=google_key, model="gemini-1.5-pro-latest"
                )
            }
            logger.info("Google adapters initialized")

    def _map_model_name(self, frontend_name: str) -> str:
        """Map frontend model names to backend names"""
        return self.model_mappings.get(frontend_name, frontend_name)

    def _get_adapter(self, model_name: str):
        """Get the appropriate adapter for a model"""
        backend_name = self._map_model_name(model_name)

        # Find which provider has this model
        for _provider, models in self.adapters.items():
            if backend_name in models:
                return models[backend_name]

        logger.warning(
            f"No adapter found for model: {model_name} (mapped to {backend_name})"
        )
        return None

    async def _call_model(
        self, model_name: str, prompt: str, stage: str = "initial"
    ) -> Dict[str, Any]:
        """Call a model with timeout and error handling"""
        adapter = self._get_adapter(model_name)
        if not adapter:
            return {
                "response": f"Error: Model {model_name} not available",
                "time": 0,
                "error": True,
            }

        start_time = time.time()
        try:
            # The new adapters handle their own timeouts internally via httpx
            result = await adapter.generate(prompt)

            elapsed = time.time() - start_time

            return {
                "response": result.get("generated_text", ""),
                "time": elapsed,
                "model": model_name,
            }

        except Exception as e:
            logger.error(f"Error calling model {model_name}: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "time": time.time() - start_time,
                "error": True,
            }

    async def orchestrate(
        self, prompt: str, models: List[str], ultra_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate Ultra Synthesis across multiple models

        Args:
            prompt: The user's prompt
            models: List of model names to use
            ultra_model: Model to use for final synthesis (defaults to first model)

        Returns:
            Dict with initial_responses, meta_responses, ultra_response, and performance
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        if not models:
            models = ["gpt4o", "claude37"]  # Default models

        if not ultra_model:
            ultra_model = models[0]

        start_time = time.time()
        model_times = {}

        # Stage 1: Initial responses (parallel)
        initial_tasks = []
        for model in models:
            task = self._call_model(model, prompt, "initial")
            initial_tasks.append(task)

        initial_results = await asyncio.gather(*initial_tasks)
        initial_responses = {}

        for model, result in zip(models, initial_results):
            initial_responses[model] = result["response"]
            model_times[f"{model}_initial"] = result["time"]

        # Stage 2: Meta responses (parallel)
        # Build meta prompt with all initial responses
        meta_prompt_base = self._build_meta_prompt(prompt, initial_responses)

        meta_tasks = []
        for model in models:
            task = self._call_model(model, meta_prompt_base, "meta")
            meta_tasks.append(task)

        meta_results = await asyncio.gather(*meta_tasks)
        meta_responses = {}

        for model, result in zip(models, meta_results):
            meta_responses[model] = result["response"]
            model_times[f"{model}_meta"] = result["time"]

        # Stage 3: Ultra synthesis
        ultra_prompt = self._build_ultra_prompt(prompt, meta_responses)
        ultra_result = await self._call_model(ultra_model, ultra_prompt, "ultra")

        ultra_response = ultra_result["response"]
        model_times[f"{ultra_model}_ultra"] = ultra_result["time"]

        # Calculate total time
        total_time = time.time() - start_time

        # Build response in format expected by frontend
        return {
            "status": "success",
            "model_responses": initial_responses,  # Frontend expects initial responses here
            "meta_responses": meta_responses,  # Additional data
            "ultra_response": ultra_response,
            "performance": {
                "total_time_seconds": total_time,
                "model_times": model_times,
            },
            "initial_responses": initial_responses,  # For testing
            "cached": False,
        }

    def _build_meta_prompt(
        self, original_prompt: str, initial_responses: Dict[str, str]
    ) -> str:
        """Build the meta stage prompt"""
        responses_text = "\\n\\n".join(
            [
                f"Model {model}:\\n{response}"
                for model, response in initial_responses.items()
            ]
        )

        return (
            f"Several of your fellow LLMs were given the same prompt as you. "
            f"Their responses are as follows:\\n\\n{responses_text}\\n\\n"
            f"Do NOT assume that anything written is correct or properly sourced, "
            f"but given these other responses, could you make your original response better? "
            f"More insightful? More factual, more comprehensive when considering the initial user prompt? "
            f"If you do believe you can make your original response better, "
            f"please draft a new response to the initial inquiry.\\n\\n"
            f"Original inquiry: {original_prompt}"
        )

    def _build_ultra_prompt(
        self, original_prompt: str, meta_responses: Dict[str, str]
    ) -> str:
        """Build the ultra synthesis prompt"""
        responses_text = "\\n\\n".join(
            [
                f"Model {model}:\\n{response}"
                for model, response in meta_responses.items()
            ]
        )

        return (
            f"To the chosen synthesizer: You are tasked with creating the Ultra Synthesis: "
            f"a fully-integrated intelligence synthesis that combines the relevant outputs "
            f"from all methods into a cohesive whole, with recommendations that benefit "
            f"from multiple cognitive frameworks. The objective here is not to be necessarily "
            f"the best, but the most expansive synthesization of the many outputs. "
            f"While you should disregard facts or analyses that are extremely anomalous or wrong, "
            f"with the original prompt in mind, your final Ultra Synthesis should reflect "
            f"all of the relevant meat from the meta level responses, organized in a manner "
            f"that is clear and non repetitive.\\n\\n"
            f"Original prompt: {original_prompt}\\n\\n"
            f"Meta-level responses to synthesize:\\n{responses_text}"
        )
