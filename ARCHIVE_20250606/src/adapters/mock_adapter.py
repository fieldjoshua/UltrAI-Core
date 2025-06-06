"""
Mock adapter for testing and development.

This module provides a mock implementation of the BaseAdapter for use
in testing and development environments without API keys.
"""

import asyncio
import json
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional

from src.adapters.base_adapter import BaseAdapter
from src.orchestration.config import ModelConfig

logger = logging.getLogger(__name__)


class MockAdapter(BaseAdapter):
    """
    Mock adapter for testing and development.

    This adapter simulates responses from an LLM without making
    actual API calls, useful for testing and development.
    """

    def __init__(self, model_config: ModelConfig):
        """
        Initialize the mock adapter.

        Args:
            model_config: Configuration for the model
        """
        super().__init__(model_config)
        self.responses_dir = os.path.join(os.getcwd(), "responses")
        os.makedirs(self.responses_dir, exist_ok=True)

        # Create a unique identifier for this adapter instance
        self.instance_id = f"mock_{model_config.model_id}_{int(time.time())}"
        logger.info(f"Initialized MockAdapter with ID {self.instance_id}")

    async def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        timeout: int = None,
        **kwargs,
    ) -> str:
        """
        Generate a mock response.

        Args:
            prompt: The prompt to respond to
            max_tokens: Maximum number of tokens (ignored in mock)
            temperature: Temperature (affects randomness in mock)
            timeout: Request timeout (simulated in mock)
            **kwargs: Additional parameters

        Returns:
            A mock response string
        """
        # Get default values from model config if not provided
        max_tokens = max_tokens or self.model_config.max_tokens
        temperature = temperature or self.model_config.temperature
        timeout = timeout or self.model_config.timeout

        # Simulate processing time (faster than real API)
        delay = min(1.0, random.uniform(0.2, 0.7))
        await asyncio.sleep(delay)

        # If timeout is very small, simulate timeout error
        if timeout and timeout < delay:
            raise TimeoutError(f"Request timed out after {timeout} seconds")

        # Generate response based on prompt characteristics
        response_length = min(max_tokens // 4, 150)  # Simpler than real token counting

        # Look for existing responses or generate a new one
        response = self._get_canned_response(prompt)
        if not response:
            # Generate a generic response based on prompt
            response = self._generate_mock_response(
                prompt, response_length, temperature
            )

        # Simulate failure based on low probability
        if random.random() < 0.05:  # 5% chance of failure
            raise Exception("Simulated random failure in mock adapter")

        return response

    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        Generate mock embeddings.

        Args:
            text: The text to embed
            **kwargs: Additional parameters

        Returns:
            A list of random embedding values
        """
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Generate deterministic but seemingly random embeddings
        # Seed random generator with hash of text to get consistent results
        random.seed(hash(text))
        embedding_dim = 384  # Common embedding dimension
        embeddings = [random.uniform(-1, 1) for _ in range(embedding_dim)]

        # Normalize the embeddings
        magnitude = sum(x**2 for x in embeddings) ** 0.5
        normalized_embeddings = [x / magnitude for x in embeddings]

        return normalized_embeddings

    def is_available(self) -> bool:
        """
        Check if the mock adapter is available.

        Returns:
            Always returns True for mock adapter
        """
        return True

    def _get_canned_response(self, prompt: str) -> Optional[str]:
        """
        Look for a canned response that matches the prompt.

        Args:
            prompt: The prompt to match

        Returns:
            A canned response if found, None otherwise
        """
        # Simple keywords-based matching for canned responses
        prompt_lower = prompt.lower()

        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm a mock LLM. How can I assist you today?"

        if "help" in prompt_lower:
            return "I'm a mock LLM service used for testing. I don't provide real assistance, but I simulate responses to help developers test their applications."

        if "error" in prompt_lower:
            if (
                random.random() < 0.5
            ):  # 50% chance of returning error for error-related prompts
                raise Exception("You asked for an error, so I'm providing one!")
            return "You mentioned errors. In a real system, error handling is crucial for robustness."

        # Check for saved responses in the responses directory
        try:
            response_files = os.listdir(self.responses_dir)
            for file_name in response_files:
                if file_name.endswith(".json"):
                    with open(os.path.join(self.responses_dir, file_name), "r") as f:
                        saved_responses = json.load(f)
                        for item in saved_responses:
                            if "prompt" in item and "response" in item:
                                # Simple matching - could be improved with semantic similarity
                                if (
                                    item["prompt"].lower() in prompt_lower
                                    or prompt_lower in item["prompt"].lower()
                                ):
                                    return item["response"]
        except Exception as e:
            logger.warning(f"Error loading canned responses: {str(e)}")

        return None

    def _generate_mock_response(
        self, prompt: str, length: int, temperature: float
    ) -> str:
        """
        Generate a mock response based on prompt characteristics.

        Args:
            prompt: The prompt to respond to
            length: Approximate length of response
            temperature: Controls randomness (higher = more random)

        Returns:
            Generated mock response
        """
        # Analyze prompt to determine the type of response
        prompt_lower = prompt.lower()

        # Different response templates based on prompt type
        if "list" in prompt_lower or "enumerate" in prompt_lower:
            return self._generate_list_response(prompt, length)
        elif "explain" in prompt_lower or "describe" in prompt_lower:
            return self._generate_explanation_response(prompt, length)
        elif (
            "code" in prompt_lower
            or "function" in prompt_lower
            or "script" in prompt_lower
        ):
            return self._generate_code_response(prompt)
        elif "?" in prompt:
            return self._generate_question_response(prompt, length)
        else:
            return self._generate_generic_response(prompt, length)

    def _generate_list_response(self, prompt: str, length: int) -> str:
        """Generate a response in list format."""
        num_items = min(10, max(3, length // 20))
        response = "Here are some key points:\n\n"

        for i in range(1, num_items + 1):
            response += f"{i}. Mock list item {i} related to the topic\n"

        return response

    def _generate_explanation_response(self, prompt: str, length: int) -> str:
        """Generate an explanatory response."""
        paragraphs = max(2, length // 50)
        response = ""

        for i in range(paragraphs):
            response += f"This is paragraph {i+1} of the mock explanation. It contains simulated content that would normally be related to your query about '{prompt[:20]}...'. "
            response += "The actual content would be more meaningful and directly address your question.\n\n"

        return response

    def _generate_code_response(self, prompt: str) -> str:
        """Generate a code snippet response."""
        language = "python"
        if "javascript" in prompt.lower() or "js" in prompt.lower():
            language = "javascript"
        elif "java" in prompt.lower():
            language = "java"

        if language == "python":
            return '''
```python
def mock_function(param1, param2=None):
    """
    This is a mock Python function generated for demonstration.

    Args:
        param1: First parameter
        param2: Optional second parameter

    Returns:
        A mock result
    """
    result = f"Processing {param1}"
    if param2:
        result += f" with {param2}"
    return result

# Example usage
output = mock_function("data", param2="options")
print(output)  # Output: Processing data with options
```

This is a simple Python function that demonstrates parameter handling.
'''
        elif language == "javascript":
            return """
```javascript
/**
 * Mock JavaScript function for demonstration
 * @param {string} param1 - First parameter
 * @param {object} [param2] - Optional second parameter
 * @returns {string} Mock result
 */
function mockFunction(param1, param2 = null) {
  let result = `Processing ${param1}`;
  if (param2) {
    result += ` with ${JSON.stringify(param2)}`;
  }
  return result;
}

// Example usage
const output = mockFunction("data", { option: "value" });
console.log(output); // Output: Processing data with {"option":"value"}
```

This JavaScript function demonstrates parameter handling and default values.
"""
        else:
            return """
```java
/**
 * Mock Java class for demonstration
 */
public class MockExample {
    /**
     * Sample method that processes input
     * @param param1 First parameter
     * @param param2 Optional second parameter
     * @return A mock result
     */
    public String mockMethod(String param1, String param2) {
        String result = "Processing " + param1;
        if (param2 != null) {
            result += " with " + param2;
        }
        return result;
    }

    public static void main(String[] args) {
        MockExample example = new MockExample();
        String output = example.mockMethod("data", "options");
        System.out.println(output); // Output: Processing data with options
    }
}
```

This Java class demonstrates a simple method with parameters.
"""

    def _generate_question_response(self, prompt: str, length: int) -> str:
        """Generate a response to a question."""
        return f"In response to your question about '{prompt.replace('?', '')}', I would provide a detailed answer. As a mock LLM, I'm simulating what a response would look like. A real LLM would give you specific information about your query."

    def _generate_generic_response(self, prompt: str, length: int) -> str:
        """Generate a generic response."""
        words = min(100, max(20, length // 5))
        response = f"This is a mock response to your input: '{prompt[:30]}...'. "
        response += "In a real system, you would receive a meaningful response that addresses your specific query or instruction. "
        response += "This placeholder text simulates approximately what the length and structure of a response might be, "
        response += "but without the actual informational content you would receive from a real language model."

        return response
