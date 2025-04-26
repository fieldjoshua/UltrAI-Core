"""
Orchestration Engine Component

This module handles the coordination of LLM interactions, pattern selection,
and result aggregation.
"""

from typing import Dict, List, Optional, Any
from backend.core.llm import LLMProvider, PromptManager, ResponseProcessor


class Pattern:
    """Represents a pattern for LLM interaction."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, step: Dict[str, Any]):
        """Add a step to the pattern."""
        self.steps.append(step)


class OrchestrationEngine:
    """Coordinates LLM interactions and pattern execution."""

    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.llm_provider: Optional[LLMProvider] = None
        self.prompt_manager: Optional[PromptManager] = None
        self.response_processor: Optional[ResponseProcessor] = None

    def register_pattern(self, pattern: Pattern):
        """Register a new pattern."""
        self.patterns[pattern.name] = pattern

    def get_pattern(self, name: str) -> Optional[Pattern]:
        """Get a pattern by name."""
        return self.patterns.get(name)

    def set_llm_provider(self, provider: LLMProvider):
        """Set the LLM provider."""
        self.llm_provider = provider

    def set_prompt_manager(self, manager: PromptManager):
        """Set the prompt manager."""
        self.prompt_manager = manager

    def set_response_processor(self, processor: ResponseProcessor):
        """Set the response processor."""
        self.response_processor = processor

    async def execute_pattern(self, pattern_name: str, **kwargs) -> str:
        """Execute a pattern with the given parameters."""
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_name}' not found")

        if (
            not self.llm_provider
            or not self.prompt_manager
            or not self.response_processor
        ):
            raise ValueError("Missing required components")

        results = []
        for step in pattern.steps:
            prompt = self.prompt_manager.format_prompt(step["template"], **kwargs)
            response = await self.llm_provider.generate(prompt)
            processed_response = self.response_processor.process(response)
            results.append(processed_response)

        return "\n".join(results)
