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
from pathlib import Path

from app.services.llm_adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
)

logger = logging.getLogger(__name__)

# Timeout for individual model calls (applied via asyncio.wait_for())
TIMEOUT_SECONDS = 30  # seconds

# Maximum number of simultaneous outbound LLM requests. This helps prevent hitting
# provider-side rate-limits when the caller supplies a large model list.
MAX_CONCURRENT_REQUESTS = 3

# Rough context size guard – if a built prompt exceeds this token estimate we will
# truncate individual peer answers starting from the longest until we fit.
MAX_CONTEXT_TOKENS = 6000  # adjust per model context window


# Simple word-based token estimate (≈0.75 tokens per English word on average)
def _estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 0.75)


TEMPLATE_CACHE: Dict[str, str] = {}


def _load_template(name: str) -> str:
    """Load a prompt template from app/services/prompt_templates/*.md"""

    if name in TEMPLATE_CACHE:
        return TEMPLATE_CACHE[name]

    template_path = Path(__file__).parent / "prompt_templates" / f"{name}.md"

    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
    else:
        # Fallback to empty string; callers must handle missing template
        logging.warning(
            f"Prompt template {template_path} not found. Using empty template."
        )
        content = ""

    TEMPLATE_CACHE[name] = content
    return content


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
            # Apply an overall timeout guard in addition to adapter-level httpx timeout.
            # This ensures no single model call blocks the entire orchestration run.
            result = await asyncio.wait_for(
                adapter.generate(prompt), timeout=TIMEOUT_SECONDS
            )

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

        # Enforce that at least two models are provided
        if not models or len(models) < 2:
            raise ValueError(
                "At least two distinct models must be specified for Ultra Synthesis."
            )

        # Determine which model will act as the synthesiser. If the caller does not
        # specify one, choose according to a preference order so we default to the
        # most capable model available.
        if not ultra_model:
            preference_order: List[str] = [
                "gpt4o",
                "gpt4turbo",
                "claude3opus",
                "claude37",
                "gemini15",
                "llama3",
            ]

            # Pick the first preferred model present in the supplied list; fall back
            # to the first supplied model.
            ultra_model = next((m for m in preference_order if m in models), models[0])

        # Exclude the ultra model from the peer stages to keep synthesis neutral
        peer_models = [m for m in models if m != ultra_model]

        if not peer_models:
            # Edge-case: caller only supplied the ultra model. Fallback to using it
            # for all stages (previous behaviour) rather than erroring out.
            peer_models = [ultra_model]

        start_time = time.time()
        model_times = {}
        token_counts: Dict[str, int] = {}

        # Semaphore for concurrency throttling
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def _sem_call(model_name: str, _prompt: str, stage: str):
            """Wrapper that limits concurrent API calls via a semaphore."""
            async with semaphore:
                return await self._call_model(model_name, _prompt, stage)

        # Stage 1: Initial responses (parallel with concurrency guard)
        initial_tasks = [_sem_call(model, prompt, "initial") for model in peer_models]

        initial_results = await asyncio.gather(*initial_tasks, return_exceptions=True)
        initial_responses = {}

        for model, result in zip(peer_models, initial_results):
            if isinstance(result, Exception):
                logger.error(
                    f"Unhandled exception during initial stage for {model}: {result}"
                )
                response_text = f"Error: {result}"
                time_val = 0
            else:
                response_text = result.get("response", "")  # type: ignore[attr-defined]
                time_val = result.get("time", 0)  # type: ignore[attr-defined]

            initial_responses[model] = response_text
            model_times[f"{model}_initial"] = time_val

        # Track token usage for meta prompt construction
        token_counts["initial_combined"] = _estimate_tokens(
            " ".join(initial_responses.values())
        )

        # Stage 2: Meta responses (parallel)
        # Build meta prompt with all initial responses
        meta_prompt_base = self._build_meta_prompt(prompt, initial_responses)

        token_counts["meta_prompt"] = _estimate_tokens(meta_prompt_base)

        meta_tasks = [
            _sem_call(model, meta_prompt_base, "meta") for model in peer_models
        ]

        meta_results = await asyncio.gather(*meta_tasks, return_exceptions=True)
        meta_responses = {}

        for model, result in zip(peer_models, meta_results):
            if isinstance(result, Exception):
                logger.error(
                    f"Unhandled exception during meta stage for {model}: {result}"
                )
                response_text = f"Error: {result}"
                time_val = 0
            else:
                response_text = result.get("response", "")  # type: ignore[attr-defined]
                time_val = result.get("time", 0)  # type: ignore[attr-defined]

            meta_responses[model] = response_text
            model_times[f"{model}_meta"] = time_val

        # Track token usage for meta prompt construction
        token_counts["meta_combined"] = _estimate_tokens(
            " ".join(meta_responses.values())
        )

        # Stage 3: Ultra synthesis
        ultra_prompt = self._build_ultra_prompt(prompt, meta_responses)

        token_counts["ultra_prompt"] = _estimate_tokens(ultra_prompt)

        ultra_result = await self._call_model(ultra_model, ultra_prompt, "ultra")

        ultra_response = ultra_result["response"]
        model_times[f"{ultra_model}_ultra"] = ultra_result["time"]

        # Calculate total time
        total_time = time.time() - start_time

        # Build response (prunes duplicate keys, but keeps backward-compat "model_responses")
        return {
            "status": "success",
            "model_responses": initial_responses,  # backward-compat key
            "meta_responses": meta_responses,
            "ultra_response": ultra_response,
            "ultra_model": ultra_model,
            "performance": {
                "total_time_seconds": total_time,
                "model_times": model_times,
                "token_estimates": token_counts,
            },
            "cached": False,
        }

    def _build_meta_prompt(
        self, original_prompt: str, initial_responses: Dict[str, str]
    ) -> str:
        """Build the meta stage prompt"""
        # Truncate responses if needed to fit within context window
        truncated_initials = self._truncate_responses(initial_responses)

        responses_text = "\n\n".join(
            [
                f"### {model} Answer\n{resp}"
                for model, resp in truncated_initials.items()
            ]
        )

        template = _load_template("meta_prompt")

        if not template:
            # Fallback to inline default template
            template = (
                "SYSTEM: You are an expert reviewer who wants to improve upon peer LLM answers.\n"
                "USER:\n"
                "--- Original prompt ---\n"
                "{ORIGINAL_PROMPT}\n\n"
                "--- Peer answers (assume they may contain errors) ---\n"
                "{RESPONSES_TEXT}\n\n"
                "TASK: Produce an improved answer that corrects mistakes and fills gaps.\n"
                "Limit length to what is necessary; avoid repetition."
            )

        return template.format(
            ORIGINAL_PROMPT=original_prompt, RESPONSES_TEXT=responses_text
        )

    def _build_ultra_prompt(
        self, original_prompt: str, meta_responses: Dict[str, str]
    ) -> str:
        """Build the ultra synthesis prompt"""
        # Truncate meta responses similarly
        truncated_meta = self._truncate_responses(meta_responses)

        responses_text = "\n\n".join(
            [
                f"### {model} Revised Answer\n{resp}"
                for model, resp in truncated_meta.items()
            ]
        )

        template = _load_template("ultra_prompt")

        if not template:
            template = (
                "SYSTEM: You are the ULTRA synthesiser. Combine the strongest points from each answer into one coherent, non-redundant response.\n"
                "USER:\n"
                "--- Original prompt ---\n"
                "{ORIGINAL_PROMPT}\n\n"
                "--- Candidate answers ---\n"
                "{RESPONSES_TEXT}\n\n"
                "TASK: Write a SINGLE, well-structured answer with:\n"
                "1. Executive Summary\n2. Detailed Analysis\n3. Confidence & Open Questions\n"
            )

        return template.format(
            ORIGINAL_PROMPT=original_prompt, RESPONSES_TEXT=responses_text
        )

    # ---------------------------------------------------------------------
    # Helper methods
    # ---------------------------------------------------------------------

    def _truncate_responses(self, responses: Dict[str, str]) -> Dict[str, str]:
        """Ensure combined responses fit within MAX_CONTEXT_TOKENS.

        The algorithm trims the longest responses by 20% chunks until the total
        token estimate drops below the threshold. This is a simple heuristic
        that avoids an extra LLM summarisation pass while protecting against
        context overflow.
        """

        if _estimate_tokens(" ".join(responses.values())) <= MAX_CONTEXT_TOKENS:
            return responses

        # Work on a copy so we don't mutate original dict
        truncated = responses.copy()

        # Keep iterating until within budget or all responses very small
        while _estimate_tokens(" ".join(truncated.values())) > MAX_CONTEXT_TOKENS:
            # Find the key of the longest response (by token estimate)
            longest_key = max(truncated, key=lambda k: _estimate_tokens(truncated[k]))
            text = truncated[longest_key]
            # Reduce length by 20%
            new_length = int(len(text) * 0.8)
            truncated[longest_key] = text[:new_length] + " …"

            # Break if drastic truncation didn't help (avoid infinite loop)
            if new_length < 200:  # about 150 tokens
                break

        return truncated
