"""
Frontend Interface Component

This module handles the frontend interface for prompt input, LLM selection,
pattern selection, and result display.
"""

from typing import Dict, Optional, Any, Callable
from pydantic import BaseModel


class FrontendConfig(BaseModel):
    """Configuration for the frontend interface."""

    title: str
    description: str
    version: str
    theme: Dict[str, Any]


class FrontendComponent:
    """Manages frontend components and their interactions."""

    def __init__(self, config: FrontendConfig):
        self.config = config
        self.components: Dict[str, Any] = {}

    def register_component(self, name: str, component: Any):
        """Register a new frontend component."""
        self.components[name] = component

    def get_component(self, name: str) -> Optional[Any]:
        """Get a frontend component by name."""
        return self.components.get(name)

    def render(self) -> Dict[str, Any]:
        """Render the frontend interface."""
        return {
            "title": self.config.title,
            "description": self.config.description,
            "version": self.config.version,
            "theme": self.config.theme,
            "components": self.components,
        }


class PromptInput:
    """Handles prompt input and validation."""

    def __init__(self):
        self.templates: Dict[str, str] = {}

    def add_template(self, name: str, template: str):
        """Add a new prompt template."""
        self.templates[name] = template

    def get_template(self, name: str) -> Optional[str]:
        """Get a prompt template by name."""
        return self.templates.get(name)

    def validate_input(self, input_text: str) -> bool:
        """Validate user input."""
        return bool(input_text.strip())


class ResultDisplay:
    """Handles result display and formatting."""

    def __init__(self):
        self.formatters: Dict[str, Callable[[str], str]] = {}

    def add_formatter(self, name: str, formatter: Callable[[str], str]):
        """Add a new result formatter."""
        self.formatters[name] = formatter

    def format_result(self, result: str, format_type: str) -> str:
        """Format a result using the specified formatter."""
        formatter = self.formatters.get(format_type)
        if not formatter:
            return result
        return formatter(result)
