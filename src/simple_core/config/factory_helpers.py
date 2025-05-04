"""
Helper functions for the factory module.

This module provides helper functions for creating and configuring
orchestrator instances.
"""

import logging
from typing import Dict, List, Optional, Tuple, Type, Union

from src.simple_core.adapter import Adapter
from src.simple_core.analysis.analysis_module import AnalysisModule
from src.simple_core.analysis.modules.comparative import ComparativeAnalysis
from src.simple_core.analysis.modules.factual import FactualAnalysis
from src.simple_core.config import AnalysisConfig, Config, ModelDefinition

logger = logging.getLogger(__name__)


def create_analysis_registry() -> Dict[str, Type[AnalysisModule]]:
    """Create the default analysis module registry."""
    return {
        "comparative": ComparativeAnalysis,
        "factual": FactualAnalysis,
    }


def get_analysis_module_class(analysis_type: str) -> Optional[Type[AnalysisModule]]:
    """Get the analysis module class for the specified type."""
    registry = create_analysis_registry()
    return registry.get(analysis_type)
