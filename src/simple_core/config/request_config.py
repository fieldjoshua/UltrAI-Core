"""
Request configuration for the orchestrator.

This module provides a simple way to configure orchestrator requests.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RequestConfig:
    """
    Configuration for a specific orchestrator request.

    This class provides a simple way for users to control which LLMs
    participate and which one serves as the lead for synthesis.
    """

    # The prompt to process
    prompt: str

    # List of model names to include (if empty, use all available)
    model_names: List[str] = field(default_factory=list)

    # Name of the model to use as the UltrAI lead (synthesis)
    # If not specified, the highest priority model will be used
    lead_model: Optional[str] = None

    # Type of analysis to perform (default is comparative)
    analysis_type: str = "comparative"

    # Additional options (for advanced use)
    options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for processing."""
        return {
            "prompt": self.prompt,
            "model_names": self.model_names.copy(),
            "lead_model": self.lead_model,
            "analysis_type": self.analysis_type,
            "options": self.options.copy(),
        }
