"""
LLM Integration Component

This module handles the integration with various Language Model providers,
including prompt handling and response processing.
"""

from typing import Dict, List, Optional, Callable


class LLMProvider:
    """Base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

    async def stream(self, prompt: str, **kwargs) -> str:
        """Stream a response from the LLM."""
        raise NotImplementedError


class PromptManager:
    """Manages prompt templates and processing."""

    def __init__(self):
        self.templates: Dict[str, str] = {}

    def add_template(self, name: str, template: str):
        """Add a new prompt template."""
        self.templates[name] = template

    def get_template(self, name: str) -> Optional[str]:
        """Get a prompt template by name."""
        return self.templates.get(name)

    def format_prompt(self, name: str, **kwargs) -> str:
        """Format a prompt template with the given parameters."""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")
        return template.format(**kwargs)


class ResponseProcessor:
    """Processes and validates LLM responses."""

    def __init__(self):
        self.validators: List[Callable[[str], bool]] = []

    def add_validator(self, validator: Callable[[str], bool]):
        """Add a response validator."""
        self.validators.append(validator)

    def validate(self, response: str) -> bool:
        """Validate a response using all registered validators."""
        return all(validator(response) for validator in self.validators)

    def process(self, response: str) -> str:
        """Process a response, including validation and formatting."""
        if not self.validate(response):
            raise ValueError("Response validation failed")
        return response.strip()
