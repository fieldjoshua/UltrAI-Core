"""
OpenAI adapter for interacting with OpenAI API models.

This module provides an adapter for OpenAI models like GPT-4, GPT-3.5, etc.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional

from src.adapters.base_adapter import BaseAdapter
from src.orchestration.config import ModelConfig

logger = logging.getLogger(__name__)

class OpenAIAdapter(BaseAdapter):
    """
    Adapter for OpenAI models.
    
    This adapter interacts with the OpenAI API to generate text
    using models like GPT-4, GPT-3.5, etc.
    """
    
    def __init__(self, model_config: ModelConfig):
        """
        Initialize the OpenAI adapter.
        
        Args:
            model_config: Configuration for the OpenAI model
        """
        super().__init__(model_config)
        self.api_key = model_config.api_key or os.environ.get("OPENAI_API_KEY")
        self.api_base = model_config.api_base or os.environ.get("OPENAI_API_BASE")
        self.model_id = model_config.model_id
        
        # Map model IDs to actual OpenAI model names
        self.model_map = {
            "gpt4": "gpt-4",
            "gpt4o": "gpt-4o",
            "gpt4turbo": "gpt-4-turbo",
            "gpt35turbo": "gpt-3.5-turbo",
            "davinci": "text-davinci-003"
        }
        
        # Get the actual model name
        self.openai_model = self.model_map.get(self.model_id, self.model_id)
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            try:
                # Dynamically import OpenAI to avoid requiring it for all users
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                if self.api_base:
                    self.client.base_url = self.api_base
                logger.info(f"Initialized OpenAI client for model {self.openai_model}")
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            logger.warning("No OpenAI API key found, adapter will not be functional")
            self.client = None
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            **kwargs: Additional parameters for the API call
            
        Returns:
            Generated text
            
        Raises:
            Exception: If the API call fails
        """
        if not self.client:
            raise Exception("OpenAI client not initialized (missing API key?)")
        
        # Get default values from model config if not provided
        max_tokens = max_tokens or self.model_config.max_tokens
        temperature = temperature or self.model_config.temperature
        timeout = timeout or self.model_config.timeout
        
        try:
            # Make the API call with a timeout
            response = await asyncio.wait_for(
                self._generate_async(prompt, max_tokens, temperature, **kwargs),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Error in OpenAI generate: {str(e)}")
            raise
    
    async def _generate_async(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> str:
        """
        Make the async API call to OpenAI.
        
        This method is separated to allow for proper timeout handling.
        """
        try:
            # Use a thread to make the synchronous API call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
            )
            
            # Extract the response text
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def get_embedding(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Get embeddings for text using OpenAI API.
        
        Args:
            text: Text to embed
            **kwargs: Additional parameters for the API call
            
        Returns:
            List of embedding values
            
        Raises:
            Exception: If the API call fails
        """
        if not self.client:
            raise Exception("OpenAI client not initialized (missing API key?)")
        
        try:
            # Use a thread to make the synchronous API call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text,
                    **kwargs
                )
            )
            
            # Extract embeddings
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """
        Check if the OpenAI adapter is available for use.
        
        Returns:
            True if the adapter is available, False otherwise
        """
        return self.client is not None