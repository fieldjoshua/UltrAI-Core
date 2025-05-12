"""
Synchronous wrapper for async adapters.

This module provides a wrapper to allow using async adapters in a
synchronous context. This is particularly useful for Docker environments
where we want to avoid the complexity of async/await in the CLI.
"""

import asyncio
from typing import Any, Dict, List, Optional

from src.adapters.base_adapter import BaseAdapter


class SyncAdapterWrapper:
    """
    Synchronous wrapper for async adapters.
    
    This wrapper converts async methods to synchronous ones by
    creating an event loop and running the async method to completion.
    """
    
    def __init__(self, async_adapter: BaseAdapter):
        """
        Initialize the wrapper with an async adapter.
        
        Args:
            async_adapter: The async adapter to wrap
        """
        self.async_adapter = async_adapter
        self.provider = getattr(async_adapter, 'provider', 'unknown')
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response synchronously.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters for the adapter
            
        Returns:
            Generated text
        """
        # Create a new event loop
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            # Run the async method to completion
            return loop.run_until_complete(self.async_adapter.generate(prompt, **kwargs))
        except Exception as e:
            # Re-raise the exception
            raise e
        finally:
            # Clean up the event loop
            loop.close()
    
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Get embeddings synchronously.
        
        Args:
            text: The text to embed
            **kwargs: Additional parameters for the adapter
            
        Returns:
            List of embedding values
        """
        # Create a new event loop
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            # Run the async method to completion
            return loop.run_until_complete(self.async_adapter.get_embedding(text, **kwargs))
        except Exception as e:
            # Re-raise the exception
            raise e
        finally:
            # Clean up the event loop
            loop.close()
    
    def is_available(self) -> bool:
        """
        Check if the adapter is available.
        
        Returns:
            True if the adapter is available, False otherwise
        """
        return self.async_adapter.is_available()