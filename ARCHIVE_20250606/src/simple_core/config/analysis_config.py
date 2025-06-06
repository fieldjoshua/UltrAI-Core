"""
Simple analysis configuration for the orchestrator.

This module provides a simplified configuration for analysis selection.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AnalysisConfig:
    """
    Simple configuration for analysis modules.

    This class provides a streamlined way to configure which analysis
    module to use for the orchestrator.
    """

    # The analysis type to use (default is comparative)
    analysis_type: str = "comparative"

    # Whether analysis is enabled (can be disabled for basic orchestration)
    enabled: bool = True

    @classmethod
    def create_default(cls) -> "AnalysisConfig":
        """Create a default analysis configuration."""
        return cls(analysis_type="comparative", enabled=True)
