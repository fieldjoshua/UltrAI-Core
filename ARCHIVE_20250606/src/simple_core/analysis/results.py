"""
Standardized results format for analysis modules.

This module provides utilities for formatting and aggregating analysis results.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AnalysisResult:
    """
    Standardized result format for analysis modules.

    This class provides a structured format for analysis results.
    """

    module_name: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)
    scores: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "module": self.module_name,
            "summary": self.summary,
            "details": self.details,
            "scores": self.scores,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
        }


def create_result(
    module_name: str,
    summary: str,
    details: Optional[Dict[str, Any]] = None,
    scores: Optional[Dict[str, float]] = None,
    recommendations: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized analysis result.

    Args:
        module_name: Name of the analysis module
        summary: Summary of the analysis
        details: Dictionary of detailed analysis information
        scores: Dictionary of numerical scores
        recommendations: List of recommendations
        metadata: Additional metadata

    Returns:
        Dictionary containing the analysis result
    """
    result = AnalysisResult(
        module_name=module_name,
        summary=summary,
        details=details or {},
        scores=scores or {},
        recommendations=recommendations or [],
        metadata=metadata or {},
    )

    return result.to_dict()
