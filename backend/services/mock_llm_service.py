"""
Mock LLM service for testing.

This module provides a mock implementation of the LLM service for development and testing.
"""

import random
import time
from typing import Any, Dict, List, Optional


class MockLLMService:
    """Mock LLM service that returns pre-defined responses"""

    def __init__(self):
        """Initialize the mock LLM service"""
        self.models = {
            "gpt4o": "GPT-4 Omni",
            "gpt4turbo": "GPT-4 Turbo",
            "claude3opus": "Claude 3 Opus",
            "claude3sonnet": "Claude 3 Sonnet",
            "claude3haiku": "Claude 3 Haiku",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "mixtral": "Mixtral 8x7B",
            "llama3": "Llama 3 70B",
        }

        self.pattern_responses = {
            "comparative_analysis": "This is a comparative analysis...",
            "comprehensive_analysis": "This is a comprehensive analysis...",
            "concise_analysis": "This is a concise analysis...",
            "contextual_understanding": "This is a contextual understanding...",
            "critical_evaluation": "This is a critical evaluation...",
            "explanatory_discourse": "This is an explanatory discourse...",
            "investigative_inquiry": "This is an investigative inquiry...",
        }

    def analyze(
        self,
        prompt: str,
        llms: List[str],
        ultra_llm: str,
        pattern: str = "comprehensive_analysis",
        ala_carte_options: Optional[List[Any]] = None,
        output_format: str = "txt",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Mock analysis of a prompt with multiple LLMs

        Args:
            prompt: The prompt to analyze
            llms: List of LLM models to use
            ultra_llm: The Ultra LLM to use
            pattern: The analysis pattern
            ala_carte_options: Additional a la carte options (can be enum objects or strings)
            output_format: Output format (txt, rtf, google_docs, word)
            options: Additional options

        Returns:
            Analysis results
        """
        # Add some delay to simulate processing
        time.sleep(random.uniform(0.5, 1.5))

        # Create mock model responses
        model_responses = {}
        token_counts = {}
        model_times = {}

        # Process a la carte options
        ala_carte_options = ala_carte_options or []
        ala_carte_responses = {}

        # Convert enum objects to strings if needed
        processed_options = []
        for option in ala_carte_options:
            # Handle both string and enum types
            option_value = getattr(option, "value", option) if option else ""
            processed_options.append(option_value)

        for option in processed_options:
            if option == "fact_check":
                ala_carte_responses[
                    "fact_check"
                ] = "Facts have been verified for this analysis."
            elif option == "avoid_ai_detection":
                ala_carte_responses[
                    "avoid_ai_detection"
                ] = "Content optimized to avoid AI detection."
            elif option == "sourcing":
                ala_carte_responses[
                    "sourcing"
                ] = "Sources have been added to support claims."
            elif option == "encrypted":
                ala_carte_responses[
                    "encrypted"
                ] = "Analysis has been encrypted for security."
            elif option == "no_data_sharing":
                ala_carte_responses[
                    "no_data_sharing"
                ] = "Analysis performed with no data sharing."
            elif option == "alternate_perspective":
                ala_carte_responses[
                    "alternate_perspective"
                ] = "Alternative perspectives have been included."

        # Apply formatting based on output_format
        formatting_applied = f"Output formatted for {output_format.upper()}"

        for model in llms:
            # Create a model-specific response
            model_display_name = self.models.get(model, model)
            model_responses[model] = f"{model_display_name} analysis: {prompt[:50]}..."

            # Add token counts
            token_counts[model] = {
                "prompt_tokens": len(prompt.split()) * 4,
                "completion_tokens": random.randint(100, 300),
                "total_tokens": len(prompt.split()) * 4 + random.randint(100, 300),
            }

            # Add model processing time
            model_times[model] = random.uniform(1.0, 5.0)

        # Get pattern response
        pattern_response = self.pattern_responses.get(
            pattern, "This is a default analysis pattern..."
        )

        # Create ultra response
        ultra_response = f"""
# Analysis Summary
{pattern_response}

## Key Points
1. First important insight about: {prompt[:30]}...
2. Second important observation related to the topic
3. Critical analysis of underlying assumptions
4. Alternative perspectives to consider

## Model Comparison
The models have different strengths in analyzing this prompt:
- {llms[0] if llms else 'Default model'}: Strong factual analysis
- {llms[1] if len(llms) > 1 else 'Secondary model'}: Good at identifying nuances

## Conclusion
The overall assessment indicates {random.choice(['significant potential', 'moderate value', 'careful consideration needed', 'promising directions'])} for this topic.

## A La Carte Features
{chr(10).join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in ala_carte_responses.items()])}

{formatting_applied}
"""

        # Create final result
        result = {
            "status": "success",
            "model_responses": model_responses,
            "ultra_response": ultra_response,
            "pattern": pattern,
            "ala_carte_options": ala_carte_options,
            "output_format": output_format,
            "model_times": model_times,
            "token_counts": token_counts,
            "total_tokens": sum(tc["total_tokens"] for tc in token_counts.values()),
            "options_used": options or {},
        }

        return result

    async def process_async(
        self,
        prompt: str,
        llms: List[str],
        ultra_llm: str,
        pattern: str = "comprehensive_analysis",
        ala_carte_options: Optional[List[Any]] = None,
        output_format: str = "txt",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Async version of the analyze method

        Args:
            prompt: The prompt to analyze
            llms: List of LLM models to use
            ultra_llm: The Ultra LLM to use
            pattern: The analysis pattern
            ala_carte_options: Additional a la carte options (can be enum objects or strings)
            output_format: Output format (txt, rtf, google_docs, word)
            options: Additional options

        Returns:
            Analysis results
        """
        # This is just a wrapper around the synchronous method for testing
        return self.analyze(
            prompt, llms, ultra_llm, pattern, ala_carte_options, output_format, options
        )

    # Add method for get_available_models
    async def get_available_models(self) -> Dict[str, Any]:
        """Returns a list of available LLM models"""
        return {
            "status": "success",
            "available_models": [
                "gpt4o",
                "gpt4turbo",
                "gpto3mini",
                "gpto1",
                "claude37",
                "claude3opus",
                "gemini15",
                "llama3",
            ],
            "errors": {},
        }

    # Add analyze_prompt method that would be awaited
    async def analyze_prompt(
        self,
        prompt: str,
        models: List[str],
        ultra_model: str,
        pattern: str,
        ala_carte_options: Optional[List[Any]] = None,
        output_format: str = "txt",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Asynchronous version of analyze method"""
        result = self.analyze(
            prompt,
            models,
            ultra_model,
            pattern,
            ala_carte_options,
            output_format,
            options,
        )
        return result
