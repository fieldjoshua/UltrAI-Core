"""
Base adapter interface for LLM providers.

This module defines the BaseAdapter abstract class that all LLM adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from src.orchestration.config import ModelConfig


class BaseAdapter(ABC):
    """
    Abstract base class for LLM adapters.
    
    All provider-specific adapters should inherit from this class
    and implement its abstract methods.
    """
    
    def __init__(self, model_config: ModelConfig):
        """
        Initialize the adapter with model configuration.
        
        Args:
            model_config: Configuration for the model
        """
        self.model_config = model_config
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The generated text response
        """
        pass
    
    @abstractmethod
    async def get_embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Get embeddings for the provided text.
        
        Args:
            text: The text to embed
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of embedding values
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the adapter is available for use.
        
        Returns:
            True if the adapter is available, False otherwise
        """
        pass