import logging
from typing import Dict, List, Any

logger = logging.getLogger("mock_llm_service")


class MockLLMService:
    """Mock LLM service for testing and development"""

    def analyze(self, prompt: str, llms: List[str], ultra_llm: str, pattern: str) -> Dict[str, Any]:
        """Mock analysis that returns formatted results"""
        logger.info(f"Mock service analyzing prompt with {len(llms)} models")
        return {
            "status": "success",
            "ultra_response": (
                f"This is a mock response from the Ultra model: {ultra_llm}\n\n"
                f"Analysis of your query: {prompt}\n\n"
                f"Pattern used: {pattern}"
            ),
            "timing": {
                "total_seconds": 2.5,
                "model_seconds": {model: 1.2 for model in llms},
            },
        }

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
    async def analyze_prompt(self, prompt: str, models: List[str], ultra_model: str, pattern: str) -> Dict[str, Any]:
        """Asynchronous version of analyze method"""
        result = self.analyze(prompt, models, ultra_model, pattern)
        return result