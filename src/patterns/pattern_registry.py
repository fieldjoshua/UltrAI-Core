"""
Pattern Registry for UltraAI

This module provides a centralized registry for all available feather patterns,
allowing easy access and discovery of patterns.
"""

from typing import Dict, List, Optional

from .ultra_analysis_patterns import AnalysisPattern, get_pattern_mapping
from .educational_feather import EducationalFeather
from .collaborative_feather import CollaborativeFeather
from .synthesis_feather import SynthesisFeather
from .feedback_feather import FeedbackFeather


class PatternRegistry:
    """
    Registry for all available analysis patterns in the system.
    Provides methods to retrieve patterns by name or category.
    """

    def __init__(self):
        # Get all standard patterns from the main module
        self._patterns = get_pattern_mapping()

        # Add specialized patterns
        self._specialized_patterns = {
            "Learning Optimization": EducationalFeather.get_pattern(),
            "Team Analysis": CollaborativeFeather.get_pattern(),
            "Advanced Synthesis": SynthesisFeather.get_pattern(),
            "Iterative Improvement": FeedbackFeather.get_pattern(),
        }

        # Combine all patterns into one mapping
        self._all_patterns = {**self._patterns, **self._specialized_patterns}

        # Define pattern categories
        self._categories = {
            "Analytical": [
                "Gut Analysis",
                "Confidence Analysis",
                "Critique Analysis",
                "Fact Check Analysis",
            ],
            "Perspective": ["Perspective Analysis", "Stakeholder Vision"],
            "Strategic": ["Scenario Analysis", "Time Horizon", "Systems Mapper"],
            "Innovation": ["Innovation Bridge"],
            "Educational": ["Learning Optimization"],
            "Collaborative": ["Team Analysis"],
            "Synthesis": ["Advanced Synthesis"],
            "Improvement": ["Iterative Improvement"],
        }

    def get_pattern(self, pattern_name: str) -> Optional[AnalysisPattern]:
        """
        Get a pattern by its name.

        Args:
            pattern_name: The name of the pattern to retrieve

        Returns:
            The pattern object or None if not found
        """
        return self._all_patterns.get(pattern_name)

    def get_all_patterns(self) -> Dict[str, AnalysisPattern]:
        """
        Get all available patterns.

        Returns:
            A dictionary mapping pattern names to pattern objects
        """
        return self._all_patterns

    def get_patterns_by_category(self, category: str) -> List[AnalysisPattern]:
        """
        Get all patterns in a specific category.

        Args:
            category: The category name

        Returns:
            A list of pattern objects in the category, or empty list if category not found
        """
        pattern_names = self._categories.get(category, [])
        return [
            self._all_patterns.get(name)
            for name in pattern_names
            if name in self._all_patterns
        ]

    def get_pattern_categories(self) -> Dict[str, List[str]]:
        """
        Get all pattern categories with their pattern names.

        Returns:
            A dictionary mapping category names to lists of pattern names
        """
        return self._categories

    def get_pattern_description(self, pattern_name: str) -> str:
        """
        Get the description of a pattern.

        Args:
            pattern_name: The name of the pattern

        Returns:
            The pattern description or empty string if not found
        """
        pattern = self.get_pattern(pattern_name)
        return pattern.description if pattern else ""

    def get_pattern_info(self, pattern_name: str) -> Dict:
        """
        Get detailed information about a pattern.

        Args:
            pattern_name: The name of the pattern

        Returns:
            A dictionary with pattern details or empty dict if not found
        """
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            return {}

        category = next(
            (
                cat
                for cat, patterns in self._categories.items()
                if pattern_name in patterns
            ),
            "Uncategorized",
        )

        return {
            "name": pattern.name,
            "description": pattern.description,
            "category": category,
            "stages": pattern.stages,
            "instructions": pattern.instructions,
        }


# Singleton instance for easy access
pattern_registry = PatternRegistry()


def get_pattern(pattern_name: str) -> Optional[AnalysisPattern]:
    """
    Get a pattern by name.

    Args:
        pattern_name: Name of the pattern to retrieve

    Returns:
        The pattern object or None if not found
    """
    return pattern_registry.get_pattern(pattern_name)


def get_all_patterns() -> Dict[str, AnalysisPattern]:
    """
    Get all available patterns.

    Returns:
        A dictionary mapping pattern names to pattern objects
    """
    return pattern_registry.get_all_patterns()


def get_pattern_info(pattern_name: str) -> Dict:
    """
    Get detailed information about a pattern.

    Args:
        pattern_name: The name of the pattern

    Returns:
        A dictionary with pattern details or empty dict if not found
    """
    return pattern_registry.get_pattern_info(pattern_name)
