"""
Initialization for adapters package.

This package contains adapters for different LLM providers.
"""

from src.adapters.base_adapter import BaseAdapter
from src.adapters.adapter_factory import get_adapter_for_model, get_available_providers

__all__ = [
    'BaseAdapter',
    'get_adapter_for_model',
    'get_available_providers'
]