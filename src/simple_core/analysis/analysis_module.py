"""
Base class for analysis modules in the Simple Core Orchestrator.

This module defines the interface for all analysis modules and provides
common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalysisModule(ABC):
    """
    Base class for all analysis modules.

    Analysis modules examine responses from different models and provide
    structured analysis results that can be used for synthesis.
    """

    def __init__(self, name: str, weight: float = 1.0):
        """
        Initialize the analysis module.

        Args:
            name: The name of the analysis module
            weight: The default weight of this analysis in the overall analysis
        """
        self.name = name
        self.weight = weight

    @abstractmethod
    async def analyze(
        self,
        prompt: str,
        responses: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a set of responses to a prompt.

        Args:
            prompt: The original prompt
            responses: List of response objects from different models
            options: Optional configuration for this analysis

        Returns:
            Dictionary containing analysis results
        """
        pass
