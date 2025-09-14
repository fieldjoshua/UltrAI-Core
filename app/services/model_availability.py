"""
Model Availability Checker for Ultra Synthesis™

This module provides real-time model availability checking with
smart recommendations based on query type and model performance.
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import os

from app.services.llm_adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    GeminiAdapter,
    HuggingFaceAdapter,
)
from app.utils.logging import get_logger

logger = get_logger("model_availability")


class AvailabilityStatus(Enum):
    """Model availability status."""
    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    NO_API_KEY = "no_api_key"
    CHECKING = "checking"
    UNKNOWN = "unknown"


@dataclass
class ModelAvailability:
    """Model availability information."""
    model_name: str
    status: AvailabilityStatus
    response_time: Optional[float] = None
    last_checked: Optional[datetime] = None
    error_message: Optional[str] = None
    recommended_for_query: bool = False
    performance_score: Optional[float] = None


class ModelAvailabilityChecker:
    """
    Checks model availability in real-time and provides recommendations.
    """
    
    def __init__(self, model_selector=None):
        """
        Initialize the availability checker.
        
        Args:
            model_selector: Optional SmartModelSelector for performance data
        """
        self.model_selector = model_selector
        self.cache: Dict[str, ModelAvailability] = {}
        self.cache_duration = timedelta(minutes=5)
        
        # Quick check prompt for availability
        self.availability_prompt = "Hi"
        
        # Model to provider mapping
        self.model_providers = {
            "gpt-4": "openai",
            "gpt-4-turbo": "openai",
            "gpt-4o": "openai",
            "gpt-4o-mini": "openai",
            "o1-preview": "openai",
            "o1-mini": "openai",
            "claude-3-5-sonnet-20241022": "anthropic",
            "claude-3-5-haiku-20241022": "anthropic",
            "claude-3-opus-20240229": "anthropic",
            "gemini-1.5-pro": "google",
            "gemini-1.5-flash": "google",
            "gemini-2.0-flash-exp": "google",
        }
    
    def _get_cached_availability(self, model: str) -> Optional[ModelAvailability]:
        """Get cached availability if still valid."""
        if model in self.cache:
            cached = self.cache[model]
            if cached.last_checked and datetime.now() - cached.last_checked < self.cache_duration:
                return cached
        return None
    
    async def check_single_model(self, model: str) -> ModelAvailability:
        """
        Check availability of a single model.
        
        Args:
            model: Model name to check
            
        Returns:
            ModelAvailability object
        """
        # Check cache first
        cached = self._get_cached_availability(model)
        if cached:
            return cached
        
        availability = ModelAvailability(
            model_name=model,
            status=AvailabilityStatus.CHECKING,
            last_checked=datetime.now()
        )
        
        try:
            # Determine provider
            provider = self.model_providers.get(model, "unknown")
            
            # Check API key first
            api_key = self._get_api_key(provider)
            if not api_key:
                availability.status = AvailabilityStatus.NO_API_KEY
                availability.error_message = f"No API key found for {provider}"
                self.cache[model] = availability
                return availability
            
            # Create adapter and test
            adapter = self._create_adapter(model, api_key)
            if not adapter:
                availability.status = AvailabilityStatus.ERROR
                availability.error_message = "Failed to create adapter"
                self.cache[model] = availability
                return availability
            
            # Quick availability check
            start_time = datetime.now()
            try:
                response = await asyncio.wait_for(
                    adapter.generate(self.availability_prompt),
                    timeout=5.0  # 5 second timeout for availability check
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                # Extract text from response dict
                response_text = response.get("generated_text", "") if isinstance(response, dict) else str(response)
                
                if response_text and not response_text.lower().startswith("error:"):
                    availability.status = AvailabilityStatus.AVAILABLE
                    availability.response_time = response_time
                elif "rate limit" in response_text.lower():
                    availability.status = AvailabilityStatus.RATE_LIMITED
                    availability.error_message = "Rate limited"
                else:
                    availability.status = AvailabilityStatus.ERROR
                    availability.error_message = response_text
                    
            except asyncio.TimeoutError:
                availability.status = AvailabilityStatus.ERROR
                availability.error_message = "Timeout during availability check"
            except Exception as e:
                availability.status = AvailabilityStatus.ERROR
                availability.error_message = str(e)
                
        except Exception as e:
            availability.status = AvailabilityStatus.ERROR
            availability.error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Error checking {model}: {e}")
        
        # Update cache
        self.cache[model] = availability
        
        # Update model selector if available
        if self.model_selector and availability.status == AvailabilityStatus.AVAILABLE:
            self.model_selector.update_model_availability(model, True)
        elif self.model_selector and availability.status != AvailabilityStatus.AVAILABLE:
            self.model_selector.update_model_availability(model, False)
        
        return availability
    
    async def check_all_models(
        self,
        models: List[str],
        query: Optional[str] = None,
        parallel: bool = True
    ) -> Dict[str, ModelAvailability]:
        """
        Check availability of multiple models.
        
        Args:
            models: List of models to check
            query: Optional query for recommendations
            parallel: Whether to check in parallel
            
        Returns:
            Dictionary mapping model names to availability
        """
        results = {}
        
        if parallel:
            # Check all models in parallel
            tasks = [self.check_single_model(model) for model in models]
            availabilities = await asyncio.gather(*tasks, return_exceptions=True)
            
            for model, availability in zip(models, availabilities):
                if isinstance(availability, Exception):
                    results[model] = ModelAvailability(
                        model_name=model,
                        status=AvailabilityStatus.ERROR,
                        error_message=str(availability),
                        last_checked=datetime.now()
                    )
                else:
                    results[model] = availability
        else:
            # Check models sequentially
            for model in models:
                results[model] = await self.check_single_model(model)
        
        # Add recommendations if query provided
        if query and self.model_selector:
            available_models = [
                model for model, avail in results.items()
                if avail.status == AvailabilityStatus.AVAILABLE
            ]
            
            if available_models:
                # Get performance-based rankings
                from app.services.synthesis_prompts import SynthesisPromptManager
                prompt_manager = SynthesisPromptManager()
                query_type = prompt_manager.detect_query_type(query)
                
                ranked_models = await self.model_selector.select_best_synthesis_model(
                    available_models=available_models,
                    query_type=query_type.value
                )
                
                # Mark top 3 as recommended
                for i, model in enumerate(ranked_models[:3]):
                    if model in results:
                        results[model].recommended_for_query = True
                        # Add performance score (normalized 0-1)
                        results[model].performance_score = 1.0 - (i * 0.3)
        
        return results
    
    async def get_available_models(
        self,
        all_models: List[str],
        check_availability: bool = True
    ) -> Tuple[List[str], List[str]]:
        """
        Get lists of available and unavailable models.
        
        Args:
            all_models: List of all models to check
            check_availability: Whether to perform real checks
            
        Returns:
            Tuple of (available_models, unavailable_models)
        """
        if not check_availability:
            # Return all as available if not checking
            return all_models, []
        
        results = await self.check_all_models(all_models)
        
        available = []
        unavailable = []
        
        for model, availability in results.items():
            if availability.status == AvailabilityStatus.AVAILABLE:
                available.append(model)
            else:
                unavailable.append(model)
        
        return available, unavailable
    
    def get_availability_summary(
        self,
        results: Dict[str, ModelAvailability]
    ) -> Dict[str, Any]:
        """
        Get a summary of availability check results.
        
        Args:
            results: Availability check results
            
        Returns:
            Summary statistics
        """
        total = len(results)
        available = sum(1 for a in results.values() if a.status == AvailabilityStatus.AVAILABLE)
        rate_limited = sum(1 for a in results.values() if a.status == AvailabilityStatus.RATE_LIMITED)
        no_key = sum(1 for a in results.values() if a.status == AvailabilityStatus.NO_API_KEY)
        errors = sum(1 for a in results.values() if a.status == AvailabilityStatus.ERROR)
        
        avg_response_time = None
        response_times = [
            a.response_time for a in results.values()
            if a.response_time is not None
        ]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_models": total,
            "available": available,
            "rate_limited": rate_limited,
            "no_api_key": no_key,
            "errors": errors,
            "availability_rate": f"{(available / total * 100):.1f}%" if total > 0 else "0%",
            "average_response_time": f"{avg_response_time:.2f}s" if avg_response_time else None,
            "recommended_models": [
                model for model, avail in results.items()
                if avail.recommended_for_query
            ]
        }
    
    def _get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider."""
        key_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "huggingface": "HUGGINGFACE_API_KEY",
        }
        
        env_var = key_mapping.get(provider)
        if env_var:
            return os.getenv(env_var)
        return None
    
    def _create_adapter(self, model: str, api_key: str):
        """Create appropriate adapter for model."""
        try:
            if model.startswith("gpt") or model.startswith("o1"):
                return OpenAIAdapter(api_key, model)
            elif model.startswith("claude"):
                return AnthropicAdapter(api_key, model)
            elif model.startswith("gemini"):
                return GeminiAdapter(api_key, model)
            elif "/" in model:  # HuggingFace format
                return HuggingFaceAdapter(api_key, model)
        except Exception as e:
            logger.error(f"Failed to create adapter for {model}: {e}")
            return None