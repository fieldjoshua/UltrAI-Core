# backend/mock_llm_service.py
import asyncio
import json
import random
import time
import logging

# Configure logging
logger = logging.getLogger("mock_llm_service")

MOCK_RESPONSES = {
    # OpenAI models - from official registry names to user-friendly display names
    "gpt-4o": "This is a mock response from GPT-4o. I would analyze your prompt with exceptional reasoning and problem-solving skills if this were the real API.",
    "gpt-4-turbo-preview": "GPT-4 Turbo mock response: Your query would receive detailed and nuanced analysis with current knowledge and enhanced reasoning capabilities.",
    "gpt-4": "This is a mock response from GPT-4. It would analyze your prompt in great detail if this were the real API.",
    "gpt-3.5-turbo": "GPT-3.5 Turbo would provide a solid analysis here, though perhaps not as detailed as GPT-4.",
    
    # Mapped names for frontend display
    "gpt4o": "This is a mock response from GPT-4o. I would analyze your prompt with exceptional reasoning and problem-solving skills if this were the real API.",
    "gpt4turbo": "GPT-4 Turbo mock response: Your query would receive detailed and nuanced analysis with current knowledge and enhanced reasoning capabilities.",
    
    # Anthropic models
    "claude-3-opus-20240229": "Claude 3 Opus mock response with very thoughtful and well-structured analysis of your prompt. I would provide comprehensive reasoning with exceptional attention to detail.",
    "claude-3-sonnet-20240229": "Claude 3 Sonnet would respond with a balanced, nuanced analysis that considers multiple perspectives while staying grounded in facts.",
    "claude-3-haiku-20240307": "Claude 3 Haiku mock response - concise but still insightful analysis that captures the essential points efficiently.",
    
    # Mapped names for frontend display
    "claude3opus": "Claude 3 Opus mock response with very thoughtful and well-structured analysis of your prompt. I would provide comprehensive reasoning with exceptional attention to detail.",
    "claude3sonnet": "Claude 3 Sonnet would respond with a balanced, nuanced analysis that considers multiple perspectives while staying grounded in facts.",
    "claude37": "Claude 3.7 mock response: I'm the latest Claude model providing ultra-fast, precise analysis with improved reasoning capabilities.",
    
    # Google models
    "gemini-1.5-pro-latest": "Gemini 1.5 Pro mock response analyzing your prompt with Google's perspective and approach. I would leverage extensive knowledge and reasoning to provide a thorough analysis.",
    "gemini-1.5-flash-latest": "Gemini 1.5 Flash mock response: Efficient and quick analysis that balances speed with quality while focusing on the core elements of your request.",
    "gemini-pro": "Gemini Pro mock response analyzing your prompt with Google's perspective and approach.",
    
    # Mapped names for frontend display
    "gemini15pro": "Gemini 1.5 Pro mock response analyzing your prompt with Google's perspective and approach. I would leverage extensive knowledge and reasoning to provide a thorough analysis.",
    "gemini15flash": "Gemini 1.5 Flash mock response: Efficient and quick analysis that balances speed with quality while focusing on the core elements of your request.",
    "gemini15": "Gemini 1.5 Pro mock response analyzing your prompt with Google's perspective and approach.",
    
    # Docker Model Runner models
    "ai/smollm2": "Small but effective mock response from a local Smol LM model running on Docker Model Runner. I'm a lightweight model but still capable of useful responses.",
    "ai/mistral": "Mock response from Mistral running on Docker Model Runner. I provide a good balance of reasoning capabilities while running efficiently on local hardware.",
    "ai/llama3": "Llama 3 mock response via Docker Model Runner. Open-source model with solid reasoning and language understanding capabilities.",
    
    # Mapped names for frontend display
    "local-ai/smollm2": "Small but effective mock response from a local Smol LM model running on Docker Model Runner. I'm a lightweight model but still capable of useful responses.",
    "local-ai/mistral": "Mock response from Mistral running on Docker Model Runner. I provide a good balance of reasoning capabilities while running efficiently on local hardware.",
    "local-ai/llama3": "Llama 3 mock response via Docker Model Runner. Open-source model with solid reasoning and language understanding capabilities.",
    "llama3": "Llama 3 mock response. This is a high-quality open-source model providing detailed analysis and insights.",
}

# Mock analysis patterns with different synthesized response formats
MOCK_PATTERNS = {
    "gut": "Quick assessment synthesis focusing on the most probable answer based on model consensus.",
    "confidence": "Detailed evaluation with confidence ratings for each model's response.",
    "critique": "Critical analysis comparing and contrasting model responses to find strengths and weaknesses.",
    "perspective": "Multi-perspective synthesis considering different viewpoints on the topic.",
    "investigative": "Deep dive investigation with fact-checking and source references.",
    "comparative": "Side-by-side comparison of model responses highlighting key differences.",
    "comprehensive": "Thorough combined analysis incorporating all relevant points from each model.",
    "concise": "Brief synthesis of the most important points from all models.",
    "creative": "Innovative synthesis introducing novel perspectives and ideas.",
}

class MockLLMService:
    """Mock implementation of LLM service that returns predefined responses"""

    @staticmethod
    async def get_available_models():
        """Return all models as available in mock mode"""
        return {
            "status": "success",
            "available_models": [
                # OpenAI models
                "gpt4o",
                "gpt4turbo",
                
                # Anthropic models
                "claude3opus",
                "claude3sonnet",
                "claude37",
                
                # Google models
                "gemini15pro",
                "gemini15flash",
                "gemini15",
                
                # Local models (if Docker Model Runner is enabled)
                "local-ai/smollm2",
                "local-ai/mistral",
                "local-ai/llama3",
                "llama3"
            ],
            "errors": {},
        }

    @staticmethod
    async def analyze_prompt(prompt, models, ultra_model, pattern):
        """Return mock analysis data with realistic model responses."""
        logger.info(f"Mock analyzing prompt with {len(models)} models using pattern {pattern}")
        
        # Simulate more realistic processing delay based on complexity
        complexity_factor = min(len(prompt) / 500, 3)  # Cap at 3x for very long prompts
        processing_delay = 1 + (0.5 * complexity_factor)
        await asyncio.sleep(processing_delay)

        results = {}
        total_time = 0
        
        for model in models:
            # Generate model-specific timing based on model tier
            if "gpt4" in model or "claude3opus" in model:
                # Premium models take longer
                time_taken = round(random.uniform(3.0, 6.0), 2)
            elif "gpt3" in model or "claude3sonnet" in model or "gemini" in model:
                # Mid-tier models
                time_taken = round(random.uniform(2.0, 4.0), 2)
            else:
                # Faster models
                time_taken = round(random.uniform(1.0, 3.0), 2)
                
            # Add complexity factor
            time_taken = round(time_taken * complexity_factor, 2)
            total_time += time_taken
            
            # Get appropriate response for this model
            response = MOCK_RESPONSES.get(model, f"Mock response from {model}")
            
            # Make response prompt-specific
            if "?" in prompt:
                # For questions, add a direct answer first
                topic = prompt.strip("?. ").split()[-3:]  # Use last few words as the topic
                topic_str = " ".join(topic)
                response = f"In response to your question about {topic_str}: {response}"
            else:
                # For statements, frame as analysis
                topics = prompt.split()
                if len(topics) > 5:
                    topic_keywords = random.sample(topics, min(3, len(topics)))
                    topic_str = ", ".join(topic_keywords)
                    response = f"Analysis of '{topic_str}': {response}"
            
            # Calculate token usage based on response length
            tokens_used = len(response.split()) + len(prompt.split())
            
            results[model] = {
                "response": response,
                "time_taken": time_taken,
                "tokens_used": tokens_used,
                "id": f"mock-{model}-{int(time.time())}"
            }

        # Create ultra response that actually synthesizes the mock results
        pattern_style = MOCK_PATTERNS.get(pattern, MOCK_PATTERNS.get("comprehensive"))
        ultra_tokens = 0
        
        # Make a more realistic ultra response that incorporates elements from each model
        model_insights = []
        for model, result in results.items():
            # Extract a snippet from each model response to include in the ultra response
            response_parts = result["response"].split(". ")
            if len(response_parts) > 2:
                snippet = ". ".join(response_parts[1:3])  # Take the 2nd and 3rd sentences
                model_insights.append(f"{model}: {snippet}")
                ultra_tokens += len(snippet.split())
            else:
                snippet = result["response"]
                model_insights.append(f"{model}: {snippet}")
                ultra_tokens += len(snippet.split())
        
        # Create a pattern-aware ultra response
        ultra_response = (
            f"# Analysis of '{prompt[:100]}...'\n\n"
            f"## Summary\n\n"
            f"Based on all model responses, this analysis uses the '{pattern}' pattern to provide {pattern_style}\n\n"
            f"## Key Insights\n\n"
        )
        
        # Add bullet points with insights from each model
        for insight in model_insights:
            ultra_response += f"- {insight}\n"
        
        # Add synthesis section
        ultra_response += (
            f"\n## Synthesis\n\n"
            f"The {ultra_model} model has synthesized the above responses to provide a unified analysis:\n\n"
            f"The prompt requests information about {prompt.split()[:3]}... {MOCK_RESPONSES.get(ultra_model, 'This synthesized response represents the combined insights of all models.')}"
        )
        
        # Delay for ultra processing
        ultra_delay = 1.5 + (0.5 * len(models))  # More models means more processing time
        await asyncio.sleep(ultra_delay)
        
        # Calculate total time including ultra processing
        total_time += ultra_delay
        
        return {
            "results": results,
            "ultra_response": ultra_response,
            "pattern": pattern,
            "ultra_model": ultra_model,
            "ultra_tokens": ultra_tokens,
            "total_time": total_time
        }
