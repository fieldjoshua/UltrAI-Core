# backend/mock_llm_service.py
import asyncio
import json
import random

MOCK_RESPONSES = {
    "gpt-4": "This is a mock response from GPT-4. It would analyze your prompt in great detail if this were the real API.",
    "gpt-4-turbo": "GPT-4 Turbo mock response with even more insightful analysis that would be very helpful.",
    "gpt-3.5-turbo": "GPT-3.5 Turbo would provide a solid analysis here, though perhaps not as detailed as GPT-4.",
    "claude-3-opus": "Claude 3 Opus mock response with very thoughtful and well-structured analysis of your prompt.",
    "claude-3-sonnet": "Claude 3 Sonnet would respond with a comprehensive, nuanced analysis of the given text.",
    "claude-3-haiku": "Claude 3 Haiku mock response - concise but still insightful analysis.",
    "gemini-pro": "Gemini Pro mock response analyzing your prompt with Google's perspective and approach.",
}


class MockLLMService:
    """Mock implementation of LLM service that returns predefined responses"""

    @staticmethod
    async def get_available_models():
        """Return all models as available in mock mode"""
        return {
            "status": "success",
            "available_models": [
                "gpt4o",
                "gpto1",
                "gpto3mini",
                "gpt4turbo",
                "claude37",
                "claude3opus",
                "gemini15",
                "llama3",
            ],
            "errors": {},
        }

    @staticmethod
    async def analyze_prompt(prompt, models, ultra_model, pattern):
        """Return mock analysis data"""
        # Add slight delay to simulate API call
        await asyncio.sleep(1)

        results = {}
        for model in models:
            # Random timing between 2-5 seconds
            time_taken = round(random.uniform(2.0, 5.0), 2)
            results[model] = {
                "response": MOCK_RESPONSES.get(model, f"Mock response from {model}"),
                "time_taken": time_taken,
            }

        # Mock ultra analysis
        ultra_response = f"ULTRA ANALYSIS using {ultra_model} as the base model:\\n\\nThis is a synthesized view of all model responses for your prompt: '{prompt[:50]}...'"

        # Add more realistic delay for Ultra processing
        await asyncio.sleep(2)

        return {
            "results": results,
            "ultra_response": ultra_response,
            "pattern": pattern,
        }
