"""
Mock LLM service for testing.

This module provides a mock implementation of the LLM service for development and testing.
"""

import asyncio
import hashlib
import random
import time
from typing import Any, Dict, List, Optional


class MockLLMService:
    """Mock LLM service that returns pre-defined responses"""

    def __init__(self, config=None):
        """
        Initialize the mock LLM service

        Args:
            config: Optional configuration dictionary
        """
        # Initialize configuration
        self.config = config or {}

        # Check if we should use Docker Model Runner for more realistic mock responses
        self.use_model_runner = self.config.get("USE_MODEL_RUNNER_FOR_MOCK", False)
        if self.use_model_runner:
            try:
                from src.models.docker_modelrunner_adapter import (
                    DockerModelRunnerAdapter,
                )

                # Create an adapter for the default model
                default_model = self.config.get("DEFAULT_LOCAL_MODEL", "phi3:mini")
                self.model_runner_adapter = DockerModelRunnerAdapter(
                    model=default_model
                )
                print(
                    f"Mock LLM service will use Docker Model Runner with model {default_model} when available"
                )
            except ImportError:
                print(
                    "Docker Model Runner adapter not available, using static mock responses"
                )
                self.use_model_runner = False
        self.models = {
            "gpt4o": "GPT-4 Omni",
            "gpt4turbo": "GPT-4 Turbo",
            "claude37": "Claude 3.7 Haiku",
            "claude3opus": "Claude 3 Opus",
            "claude3sonnet": "Claude 3 Sonnet",
            "claude3haiku": "Claude 3 Haiku",
            "gemini15": "Gemini 1.5 Pro",
            "mixtral": "Mixtral 8x7B",
            "llama3": "Llama 3 70B",
        }

        # Enhanced model-specific response templates
        self.model_response_styles = {
            "gpt4o": {
                "strengths": [
                    "logical reasoning",
                    "technical details",
                    "balanced analysis",
                ],
                "style": "concise and precise, with clear logical steps",
                "tone": "professional but conversational",
            },
            "gpt4turbo": {
                "strengths": ["speed", "broad knowledge", "summarization"],
                "style": "efficient and direct, with clear bullet points",
                "tone": "business-like with occasional clever phrasing",
            },
            "claude37": {
                "strengths": ["creative content", "ethical reasoning", "nuance"],
                "style": "thoughtful and nuanced, with careful consideration of implications",
                "tone": "warm and reflective",
            },
            "claude3opus": {
                "strengths": ["depth", "detail", "scholarly tone"],
                "style": "thorough and comprehensive, with careful consideration",
                "tone": "academic and precise",
            },
            "gemini15": {
                "strengths": [
                    "multimodal understanding",
                    "contemporary knowledge",
                    "technical accuracy",
                ],
                "style": "structured and methodical with clear sections",
                "tone": "helpful and straightforward",
            },
            "llama3": {
                "strengths": [
                    "creative writing",
                    "coding examples",
                    "conversational tone",
                ],
                "style": "relaxed and approachable, with vivid examples",
                "tone": "friendly and enthusiastic",
            },
        }

        self.pattern_responses = {
            "gut": "This gut check analysis evaluates different perspectives to identify the most likely answer...",
            "confidence": "This confidence analysis evaluates the strength of each model response with confidence scoring...",
            "critique": "This critique analysis has models evaluate each other's reasoning and answers...",
            "fact_check": "This fact check analysis verifies factual accuracy and cites sources for claims...",
            "perspective": "This perspective analysis examines the question from multiple analytical angles...",
            "scenario": "This scenario analysis explores potential future outcomes and alternative possibilities...",
            "stakeholder": "This stakeholder vision analyzes multiple perspectives to reveal diverse interests...",
            "systems": "This systems mapper identifies complex dynamics with feedback loops and leverage points...",
            "time": "This time horizon analysis balances short and long-term considerations...",
            "innovation": "This innovation bridge uses cross-domain analogies to discover non-obvious patterns...",
        }

    async def _try_model_runner_response(self, model: str, prompt: str) -> str:
        """
        Attempt to get a response from Docker Model Runner.

        Args:
            model: The model name
            prompt: The prompt to send

        Returns:
            Response from Model Runner or None if unavailable
        """
        if not self.use_model_runner:
            return None

        try:
            # Map internal model name to Docker Model Runner model if needed
            model_mapping = {
                "llama3": "llama3:8b",
                "gpt4o": "phi3:mini",  # Fallback mapping
                "claude3opus": "mistral:7b",  # Fallback mapping
            }

            # Use the mapped model or the original if no mapping exists
            model_runner_model = model_mapping.get(model, "phi3:mini")

            # Construct a system message appropriate for the model
            if "gpt" in model:
                system_msg = (
                    "You are GPT-4, a helpful and precise AI assistant from OpenAI."
                )
            elif "claude" in model:
                system_msg = "You are Claude, a helpful and thoughtful AI assistant from Anthropic."
            elif "gemini" in model:
                system_msg = "You are Gemini, a helpful and knowledgeable AI assistant from Google."
            elif "llama" in model:
                system_msg = (
                    "You are Llama, a helpful and creative open-source AI assistant."
                )
            else:
                system_msg = "You are a helpful AI assistant."

            # Get response from Docker Model Runner
            response = await self.model_runner_adapter.generate(
                prompt,
                model=model_runner_model,
                system_message=system_msg,
                max_tokens=500,
                temperature=0.7,
            )

            return response
        except Exception as e:
            print(f"Failed to get response from Docker Model Runner: {e}")
            return None

    async def _generate_model_response(self, model: str, prompt: str) -> str:
        """Generate a model-specific response that reflects its personality"""
        # Try to get a response from Docker Model Runner first
        if self.use_model_runner:
            try:
                runner_response = await self._try_model_runner_response(model, prompt)
                if runner_response:
                    return runner_response
            except Exception as e:
                print(f"Error using Docker Model Runner for mock response: {e}")

        # Fall back to static responses if Model Runner is not available or fails
        # Get model style or use default if not defined
        style_info = self.model_response_styles.get(
            model,
            {
                "strengths": ["general intelligence"],
                "style": "straightforward and clear",
                "tone": "neutral and helpful",
            },
        )

        # Create a hash of the prompt to ensure consistent responses for the same prompt
        prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 1000
        random.seed(model + str(prompt_hash))

        # Extract a keyword from the prompt
        words = prompt.split()
        keyword = words[prompt_hash % len(words)] if words else "topic"

        # Generate different analysis styles based on the model
        if "gpt" in model:
            return (
                f"Based on my analysis of {keyword}, I've identified several key aspects to consider:\n\n"
                + f"1. First, {keyword} involves {random.choice(['technical', 'conceptual', 'practical', 'theoretical'])} considerations including {random.choice(['efficiency', 'scalability', 'applicability', 'reliability'])}.\n\n"
                + f"2. From a {random.choice(['business', 'scientific', 'engineering', 'user experience'])} perspective, {keyword} demonstrates significant {random.choice(['potential', 'limitations', 'advantages', 'challenges'])}.\n\n"
                + f"3. The {random.choice(['research', 'data', 'literature', 'evidence'])} suggests that {keyword} is best approached through {random.choice(['iterative development', 'systematic analysis', 'comparative evaluation', 'holistic understanding'])}.\n\n"
                + f"In conclusion, {keyword} represents a {random.choice(['promising', 'complex', 'evolving', 'multifaceted'])} area that requires careful consideration of multiple factors."
            )

        elif "claude" in model:
            return (
                f"I've carefully considered your question about {keyword} and would like to offer a thoughtful analysis:\n\n"
                + f"*First dimension*: {keyword} can be understood through the lens of {random.choice(['ethical implications', 'historical context', 'societal impact', 'philosophical underpinnings'])}.\n\n"
                + f"*Second dimension*: When we examine the {random.choice(['human element', 'practical applications', 'theoretical foundations', 'cultural significance'])} of {keyword}, we find interesting patterns.\n\n"
                + f"*Third dimension*: It's worth considering how {keyword} relates to {random.choice(['broader systems', 'individual experiences', 'organizational structures', 'future developments'])}.\n\n"
                + f"I hope this analysis provides helpful perspective on {keyword}. Would you like me to explore any particular aspect in more depth?"
            )

        elif "gemini" in model:
            return (
                f"Analysis of {keyword}:\n\n"
                + f"• Primary considerations: {random.choice(['technical feasibility', 'market potential', 'user adoption', 'resource requirements'])}\n"
                + f"• Secondary factors: {random.choice(['competitive landscape', 'regulatory environment', 'innovation potential', 'implementation challenges'])}\n"
                + f"• Key metrics: {random.choice(['efficiency', 'scalability', 'reliability', 'maintainability'])}\n\n"
                + f"Based on my analysis, {keyword} presents a {random.choice(['significant opportunity', 'notable challenge', 'interesting case study', 'valuable learning experience'])} in the context you've described.\n\n"
                + f"I recommend focusing on {random.choice(['practical implementation', 'theoretical understanding', 'comparative analysis', 'future applications'])} as you proceed."
            )

        elif "llama" in model:
            return (
                f"Hey there! I've thought about your question on {keyword} and have some ideas to share! 🚀\n\n"
                + f"So when it comes to {keyword}, I think we should look at a few different angles:\n\n"
                + f"1️⃣ The {random.choice(['creative', 'technical', 'practical', 'fun'])} side: {keyword} can be super {random.choice(['interesting', 'challenging', 'rewarding', 'exciting'])} when you explore it deeply!\n\n"
                + f"2️⃣ The {random.choice(['learning', 'growing', 'building', 'sharing'])} aspect: There's so much to {random.choice(['discover', 'create', 'develop', 'share'])} with {keyword}.\n\n"
                + f"3️⃣ The {random.choice(['community', 'personal', 'professional', 'social'])} dimension: Don't forget how {keyword} connects to {random.choice(['people around you', 'your goals', 'bigger trends', 'everyday life'])}!\n\n"
                + f"Hope that helps! Let me know if you want to dive deeper into any of these areas! 😊"
            )

        else:
            return (
                f"Analysis of {keyword}:\n\n"
                + f"- {keyword} can be characterized as {random.choice(['innovative', 'traditional', 'disruptive', 'evolutionary'])}\n"
                + f"- Key aspects include {random.choice(['technical feasibility', 'market potential', 'user adoption', 'resource allocation'])}\n"
                + f"- Recommended approach: {random.choice(['iterative development', 'comprehensive planning', 'focused execution', 'adaptive management'])}\n\n"
                + f"This analysis is based on general principles of {random.choice(['system design', 'project management', 'business strategy', 'technological innovation'])}."
            )

    async def analyze(
        self,
        prompt: str,
        llms: List[str],
        ultra_llm: str,
        pattern: str = "confidence",
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
        # Add some delay to simulate processing - longer for more models
        processing_time = random.uniform(0.5, 1.0) * len(llms)
        await asyncio.sleep(processing_time)

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
                ala_carte_responses["fact_check"] = (
                    "Facts have been verified for this analysis."
                )
            elif option == "avoid_ai_detection":
                ala_carte_responses["avoid_ai_detection"] = (
                    "Content optimized to avoid AI detection."
                )
            elif option == "sourcing":
                ala_carte_responses["sourcing"] = (
                    "Sources have been added to support claims."
                )
            elif option == "encrypted":
                ala_carte_responses["encrypted"] = (
                    "Analysis has been encrypted for security."
                )
            elif option == "no_data_sharing":
                ala_carte_responses["no_data_sharing"] = (
                    "Analysis performed with no data sharing."
                )
            elif option == "alternate_perspective":
                ala_carte_responses["alternate_perspective"] = (
                    "Alternative perspectives have been included."
                )

        # Apply formatting based on output_format
        formatting_applied = f"Output formatted for {output_format.upper()}"

        # Generate model-specific responses
        for model in llms:
            # Create a model-specific response
            model_responses[model] = await self._generate_model_response(model, prompt)

            # Calculate model-specific time (make primary model slightly faster)
            model_time = random.uniform(0.8, 3.0)
            if model == ultra_llm:
                model_time *= 0.8  # Primary model is a bit faster
            model_times[model] = model_time

            # Generate realistic token counts
            prompt_tokens = len(prompt.split()) * 1.3
            completion_tokens = len(model_responses[model].split()) * 1.3
            token_counts[model] = {
                "prompt_tokens": int(prompt_tokens),
                "completion_tokens": int(completion_tokens),
                "total_tokens": int(prompt_tokens + completion_tokens),
            }

        # Get pattern response
        pattern_response = self.pattern_responses.get(
            pattern, "This is a default analysis pattern..."
        )

        # Create ultra response - more comprehensive
        model_names = [self.models.get(model, model) for model in llms]
        ultra_response = f"""
# {pattern.title()} Analysis

{pattern_response}

## Key Points from All Models

1. {random.choice(["Most models agree", "Several models highlight", "The consensus indicates"])} that {prompt.split()[0] if prompt.split() else "the topic"} is {random.choice(["important", "significant", "worth exploring", "complex"])}.
2. {random.choice(["There are differences in", "Models diverge on", "Variation exists regarding"])} {random.choice(["the approach to", "the details of", "the implications of"])} the subject.
3. {random.choice(["The strongest evidence suggests", "The most convincing analysis indicates", "The highest confidence is in"])} {random.choice(["a balanced perspective", "a nuanced understanding", "a multi-faceted approach"])}.

## Model Comparison

The models demonstrate different strengths in analyzing this prompt:

{chr(10).join([f"- **{self.models.get(llm, llm)}**: {random.choice(['Excels at', 'Focuses on', 'Specializes in'])} {random.choice(['detailed analysis', 'creative connections', 'logical reasoning', 'factual accuracy'])}" for llm in llms])}

## Analysis Confidence

{chr(10).join([f"- **{self.models.get(llm, llm)}**: {random.randint(70, 95)}% - {random.choice(['High consistency', 'Strong evidence', 'Clear reasoning', 'Comprehensive approach'])}" for llm in llms])}

## Conclusion

Based on the {pattern} analysis of responses from {', '.join(model_names[:-1]) + (' and ' + model_names[-1] if model_names else '')}, the recommendation is to {random.choice(['proceed with confidence', 'consider multiple perspectives', 'gather additional information', 'implement a balanced approach'])}.

## A La Carte Features
{chr(10).join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in ala_carte_responses.items()]) if ala_carte_responses else "No additional features applied."}

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
            "performance": {
                "total_time_seconds": processing_time + sum(model_times.values()),
                "model_times": model_times,
                "token_counts": token_counts,
            },
            "total_tokens": sum(tc["total_tokens"] for tc in token_counts.values()),
            "options_used": options or {},
        }

        return result

    async def get_available_models(self) -> Dict[str, Any]:
        """Returns a list of available LLM models"""
        # Simulate a small delay
        await asyncio.sleep(0.2)

        return {
            "status": "success",
            "available_models": list(self.models.keys()),
            "errors": {},
        }

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
        # Call the async analyze method directly
        # (renamed the non-async method to async since we need async for Docker Model Runner)
        return await self.analyze(
            prompt,
            models,
            ultra_model,
            pattern,
            ala_carte_options,
            output_format,
            options,
        )
