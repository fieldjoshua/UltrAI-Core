"""
Ultra Pattern Orchestrator Module

This module implements the orchestration of different large language models
for multi-level analysis of prompts using various patterns.
"""

# noqa: E501
# pylint: disable=line-too-long

import asyncio
import json
import logging
import os
import platform
import re
import time
import traceback
from datetime import datetime, timedelta
from string import Template
from typing import Any, Dict, List, Optional

import cohere
import google.generativeai as genai
import httpx
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from mistralai.async_client import MistralAsyncClient
from mistralai.client import MistralClient
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core.ultra_error_handling import (
    APIError,
    ConfigurationError,
    RateLimitError,
    ValidationError,
)
from src.patterns.ultra_analysis_patterns import (
    AnalysisPattern,
    get_pattern_mapping,
)

# Load environment variables
load_dotenv(override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ultra_orchestrator.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class PatternOrchestrator:
    """
    Orchestrates the execution of analysis patterns using multiple LLMs.

    This class manages API clients, rate limiting, and the execution flow
    of the various analysis levels in the patterns.
    """

    def __init__(
        self,
        api_keys: Dict[str, str],
        pattern: str = "gut",
        output_format: str = "plain",
    ):
        """Initialize the Pattern Orchestrator with API keys and pattern."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Pattern Orchestrator")

        # Store API keys
        self.anthropic_key = api_keys.get("anthropic")
        self.openai_key = api_keys.get("openai")
        self.google_key = api_keys.get("google")
        self.perplexity_key = api_keys.get("perplexity")
        self.cohere_key = api_keys.get("cohere")
        self.deepseek_key = api_keys.get("deepseek")
        self.mistral_key = api_keys.get("mistral")

        # Ensure pattern is not None
        pattern_str = pattern if pattern else "gut"

        # Load pattern
        self.pattern = get_pattern_mapping().get(pattern_str)
        if not self.pattern:
            self.logger.warning(f"Invalid pattern: {pattern_str}, defaulting to 'gut'")
            self.pattern = get_pattern_mapping().get("gut")
            if not self.pattern:
                raise ValidationError(
                    "Failed to load any pattern, including default 'gut'"
                )

        # Set formatter
        self.formatter = self._get_formatter(output_format)
        self.ultra_model = None

        # Track available models
        self.available_models = []

        # Initialize rate limiting state
        self.last_request = {}

        # Initialize Ollama state
        self.ollama_available = None

        # Create output directory for saving results
        self.outputs_dir = os.path.join(os.getcwd(), "outputs")
        self.current_session_dir = None
        os.makedirs(self.outputs_dir, exist_ok=True)

        # Initialize file attachment storage
        self.file_attachments = []
        self.documents_processor = None

        # Initialize API clients
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize API clients for various LLM providers."""
        self.logger.info("Initializing API clients")
        self.clients = {}

        # Initialize Anthropic client if key is available
        if self.anthropic_key:
            self.clients["anthropic"] = AsyncAnthropic(api_key=self.anthropic_key)
            self.available_models.append("anthropic")
            self.logger.info("Anthropic client initialized")

        # Initialize OpenAI client if key is available
        if self.openai_key:
            self.clients["openai"] = AsyncOpenAI(api_key=self.openai_key)
            self.available_models.append("openai")
            self.logger.info("OpenAI client initialized")

        # Initialize Google client if key is available
        if self.google_key:
            genai.configure(api_key=self.google_key)
            self.clients["google"] = genai
            self.available_models.append("google")
            self.logger.info("Google client initialized")

        # Initialize Mistral client if key is available
        if self.mistral_key:
            self.clients["mistral"] = MistralClient(api_key=self.mistral_key)
            self.clients["mistral_async"] = MistralAsyncClient(api_key=self.mistral_key)
            self.available_models.append("mistral")
            self.logger.info("Mistral client initialized")

        # Initialize Cohere client if key is available
        if self.cohere_key:
            self.clients["cohere"] = cohere.Client(api_key=self.cohere_key)
            self.available_models.append("cohere")
            self.logger.info("Cohere client initialized")

        # Check if any clients were initialized
        if not self.available_models:
            self.logger.warning(
                "No API clients initialized. Please provide at least one API key."
            )
            raise ConfigurationError(
                "No API clients initialized. Please provide at least one API key."
            )

    async def check_ollama_availability(self):
        """
        Check if Ollama is available and running locally.

        Returns:
            bool: True if Ollama is available, False otherwise.
        """
        if self.ollama_available is not None:
            return self.ollama_available

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:11434/api/tags", timeout=2.0
                )

                if response.status_code == 200:
                    models_data = response.json()
                    models_count = len(models_data.get("models", []))
                    self.logger.info(f"Ollama available with {models_count} models")
                    self.available_models.append("ollama")
                    self.ollama_available = True
                    return True
                else:
                    self.logger.warning("Ollama responded but with non-200 status code")
                    self.ollama_available = False
                    return False
        except Exception as e:
            self.logger.info(f"Ollama not available: {str(e)}")
            self.ollama_available = False
            return False

    async def call_claude(self, prompt: str) -> str:
        """Call Anthropic's Claude model with a prompt."""
        await self._respect_rate_limit("claude")
        try:
            message = await self.clients["anthropic"].messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except anthropic.RateLimitError as e:
            self.logger.error("Claude rate limit exceeded: %s", str(e))
            raise RateLimitError(f"Claude rate limit exceeded: {e}") from e
        except Exception as e:
            self.logger.error("Error with Claude API: %s", str(e))
            raise APIError(f"Error with Claude API: {e}") from e

    async def call_chatgpt(self, prompt: str) -> str:
        """Call OpenAI's GPT model with a prompt."""
        await self._respect_rate_limit("chatgpt")
        try:
            response = await self.clients["openai"].chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
            )
            return response.choices[0].message.content or ""
        except openai.RateLimitError as e:
            self.logger.error("ChatGPT rate limit exceeded: %s", str(e))
            raise RateLimitError(f"ChatGPT rate limit exceeded: {e}") from e
        except Exception as e:
            self.logger.error("Error with ChatGPT API: %s", str(e))
            raise APIError(f"Error with ChatGPT API: {e}") from e

    async def call_cohere(self, prompt: str) -> str:
        """Call Cohere's API with a prompt."""
        try:
            await self._respect_rate_limit("cohere")
            response = self.clients["cohere"].chat(message=prompt, model="command")
            return response.text
        except Exception as e:
            error_msg = str(e)
            return f"Error calling Cohere: {error_msg or 'Unknown error'}"

    async def call_gemini(self, prompt: str) -> str:
        """Call Google's Gemini model with a prompt."""
        await self._respect_rate_limit("gemini")
        try:
            # Use the generative_models API
            model = self.clients["google"].GenerativeModel(model_name="gemini-pro")

            response = model.generate_content(prompt)
            if hasattr(response, "text") and response.text:
                return response.text
            else:
                return "No response from Gemini (empty text)"
        except Exception as e:
            error_msg = str(e)
            # Safely handle error without using len() on Exception
            return f"Error calling Gemini: {error_msg or 'Unknown error'}"

    async def call_perplexity(self, prompt: str) -> str:
        """Call Perplexity AI API with a prompt."""
        await self._respect_rate_limit("perplexity")
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "llama-3-sonar-large-32k-online",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_msg = (
                        f"Perplexity API error {response.status_code}: "
                        f"{response.text}"
                    )
                    return f"Error: {error_msg}"
        except Exception as e:
            error_msg = str(e)
            # Safely handle error without using len() on Exception
            return f"Perplexity error: {error_msg or 'Unknown error'}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    async def get_claude_response(self, prompt: str) -> str:
        """Get response from Claude API"""
        if "claude" not in self.available_models:
            self.logger.warning("Claude is not available")
            return ""

        await self._respect_rate_limit("claude")
        try:
            message = await self.clients["anthropic"].messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            if "rate limit" in str(e).lower():
                self.logger.error(f"Claude rate limit exceeded: {e}")
                raise RateLimitError(f"Claude rate limit exceeded: {e}")
            else:
                self.logger.error(f"Error with Claude API: {e}")
                raise APIError(f"Error with Claude API: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    async def get_chatgpt_response(self, prompt: str) -> str:
        """Get response from ChatGPT"""
        if "chatgpt" not in self.available_models:
            self.logger.warning("ChatGPT is not available")
            return ""

        await self._respect_rate_limit("chatgpt")
        try:
            response = await self.clients["openai"].chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            # Explicitly check for None before returning
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            if "rate limit" in str(e).lower():
                self.logger.error(f"ChatGPT rate limit exceeded: {e}")
                raise RateLimitError(f"ChatGPT rate limit exceeded: {e}")
            else:
                self.logger.error(f"Error with ChatGPT API: {e}")
                raise APIError(f"Error with ChatGPT API: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    async def get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini API"""
        if "gemini" not in self.available_models:
            self.logger.warning("Gemini is not available")
            return ""

        await self._respect_rate_limit("gemini")
        try:
            # Use the generative_models API
            model = self.clients["google"].GenerativeModel(
                model_name="gemini-pro",
                generation_config={
                    "temperature": 0.6,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
            )

            response = model.generate_content(prompt)
            if response.text:
                return response.text
            else:
                return "No response from Gemini (empty text)"
        except Exception as e:
            error_message = str(e)
            # Safely check the error message length without using len() on the exception
            return f"Error calling Gemini: {error_message if error_message else 'Unknown error'}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    async def get_perplexity_response(self, prompt: str) -> str:
        """Get response from Perplexity API"""
        try:
            await self._respect_rate_limit("perplexity")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3-sonar-large-32k-online",  # Updated model
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_msg = (
                        f"Perplexity API returned status {response.status_code}: "
                        f"{response.text}"
                    )
                    return f"Error calling Perplexity: {error_msg}"
        except Exception as e:
            error_message = str(e)
            # Safely check the error message length without using len() on the exception
            return f"Error calling Perplexity: {error_message if error_message else 'Unknown error'}"

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_cohere_response(self, prompt: str) -> str:
        """Get response from Cohere API"""
        try:
            await self._respect_rate_limit("cohere")
            response = self.clients["cohere"].chat(message=prompt, model="command")
            return response.text
        except Exception as e:
            logging.error(f"Error with Cohere API: {e}")
            return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    async def get_llama_response(self, prompt: str) -> str:
        """Get response from Ollama's Llama model"""
        # Initialize the ollama_port attribute if not present
        if not hasattr(self, "ollama_port"):
            self.ollama_port = 8080  # Default to our new port

        # Check Ollama availability if we haven't yet
        if self.ollama_available is None:
            try:
                await self.check_ollama_availability()
                self.ollama_available = True
                if "llama" not in self.available_models:
                    self.available_models.append("llama")
                    self.logger.info("Llama (Ollama) is available")
            except Exception as e:
                self.ollama_available = False
                self.logger.warning(f"Ollama not available: {e}")
                return ""

        # If we've previously determined Ollama is not available, return early
        if not self.ollama_available:
            return ""

        await self._respect_rate_limit("llama")
        try:
            # Try to use llama3 if available, fall back to llama2
            model_to_use = "llama3"

            # Check if the selected model exists
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    model_check = await client.get(
                        f"http://localhost:{self.ollama_port}/api/tags"
                    )
                    model_check.raise_for_status()
                    available_models = model_check.json()

                    # Check if either model exists in the response
                    models = [m["name"] for m in available_models.get("models", [])]
                    if not any(m.startswith("llama3") for m in models):
                        if not any(m.startswith("llama2") for m in models):
                            # Neither model exists
                            self.logger.warning(
                                "Neither llama3 nor llama2 found in Ollama. Using default model."
                            )
                            model_to_use = (
                                "llama2"  # Default to llama2 even if not found
                            )
                        else:
                            model_to_use = "llama2"
                except Exception as e:
                    # If we can't check the models, default to llama2
                    self.logger.warning(
                        f"Could not check available models: {e}. Using llama2 as default."
                    )
                    model_to_use = "llama2"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"http://localhost:{self.ollama_port}/api/generate",
                    json={
                        "model": f"{model_to_use}:latest",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 1024,
                        },
                    },
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            self.logger.error(f"Error with Ollama: {e}")
            # Don't retry for Ollama errors as they're likely local issues
            return ""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError)),
    )
    async def get_mistral_response(self, prompt: str) -> str:
        """Get response from Mistral API"""
        if "mistral" not in self.available_models:
            self.logger.warning("Mistral is not available")
            return ""

        await self._respect_rate_limit("mistral")
        try:
            # Use the async client for non-blocking operation
            response = await self.clients["mistral_async"].chat(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            return response.choices[0].message.content
        except Exception as e:
            if "rate limit" in str(e).lower():
                self.logger.error(f"Mistral rate limit exceeded: {e}")
                raise RateLimitError(f"Mistral rate limit exceeded: {e}")
            else:
                self.logger.error(f"Error with Mistral API: {e}")
                raise APIError(f"Error with Mistral API: {e}")

    async def _respect_rate_limit(self, model: str):
        """Respect rate limits between API calls"""
        try:
            current_time = datetime.now()
            last_call = self.last_request.get(
                model, current_time - timedelta(seconds=10)
            )

            # Set different wait times based on model type
            wait_seconds = {
                "claude": 1.0,  # 60 RPM (requests per minute)
                "chatgpt": 3.0,  # 20 RPM
                "gemini": 1.0,  # 60 RPM
                "perplexity": 3.0,  # 20 RPM
                "cohere": 2.0,  # 30 RPM
                "mistral": 2.0,  # 30 RPM
                "deepseek": 1.0,  # 60 RPM
                "llama": 0.5,  # 120 RPM (local, so faster)
            }.get(
                model, 2.0
            )  # Default 2s (30 RPM)

            wait_time = max(
                0, wait_seconds - (current_time - last_call).total_seconds()
            )

            if wait_time > 0:
                self.logger.debug(
                    f"Rate limiting: waiting {wait_time:.2f}s for {model}"
                )
                await asyncio.sleep(wait_time)

            self.last_request[model] = datetime.now()
        except Exception as e:
            # Don't let rate limiting errors break the flow
            self.logger.warning(f"Error in rate limiting for {model}: {e}")
            # Still update the timestamp to prevent rapid retries
            self.last_request[model] = datetime.now()

    def _create_stage_prompt(self, stage: str, context: Dict[str, Any]) -> str:
        """Create a prompt for a specific analysis stage"""
        try:
            # Check if pattern exists and has templates
            if not self.pattern:
                raise ValidationError(f"No pattern defined for stage: {stage}")

            if not hasattr(self.pattern, "templates"):
                raise ValidationError(
                    f"Pattern does not have templates attribute for stage: {stage}"
                )

            template = self.pattern.templates.get(stage)
            if not template:
                raise ValidationError(f"Unknown stage: {stage}")

            # Apply template variables
            return Template(template).safe_substitute(context)
        except Exception as e:
            self.logger.error(f"Error creating prompt for stage '{stage}': {e}")
            raise ValidationError(
                f"Failed to create prompt for stage '{stage}': {str(e)}"
            )

    async def get_initial_responses(self, prompt: str) -> Dict[str, str]:
        """Get initial responses from available models"""
        self.logger.info("Getting initial responses from available models")

        if not self.available_models:
            error_msg = "No models are available. Please check your API keys."
            self.logger.error(error_msg)
            print(f"\nError: {error_msg}")
            print("1. Ensure you have set the required API keys in your .env file")
            print("2. Check your internet connection")
            print("3. Verify that the API services are accessible")
            raise ValidationError(error_msg)

        # Process file attachments if any
        attachment_content = self._process_attachments()

        # Enhance prompt with attachment content if available
        enhanced_prompt = prompt
        if attachment_content:
            # Format the prompt differently depending on if we have RAG-processed content
            if "From:" in attachment_content and "Relevance:" in attachment_content:
                # This is content from semantic retrieval with relevance scores
                enhanced_prompt = (
                    f"{prompt}\n\n"
                    f"--- RELEVANT DOCUMENT EXCERPTS ---\n{attachment_content}\n"
                    f"--- END OF DOCUMENT EXCERPTS ---\n\n"
                    f"Please provide a comprehensive analysis based on the query and the most relevant parts "
                    f"of the provided documents. Focus on addressing the original query directly, using "
                    f"information from the document excerpts to support your answer."
                )
            else:
                # This is regular document content
                enhanced_prompt = (
                    f"{prompt}\n\n"
                    f"--- CONTENT FROM ATTACHED DOCUMENTS ---\n{attachment_content}\n"
                    f"--- END OF DOCUMENT CONTENT ---\n\n"
                    f"Based on the above documents and the original prompt, please provide a comprehensive "
                    f"analysis that focuses specifically on answering the original query."
                )

            self.logger.info(
                f"Enhanced prompt with content from {len(self.file_attachments)} attached documents"
            )

            # Calculate tokens (approximate)
            words = len(enhanced_prompt.split())
            tokens = words * 1.3  # Rough approximation of tokens
            self.logger.info(
                f"Enhanced prompt length: ~{words} words, ~{int(tokens)} tokens"
            )

            # Save the enhanced prompt
            if self.current_session_dir:
                enhanced_prompt_path = os.path.join(
                    self.current_session_dir, "enhanced_prompt.txt"
                )
                with open(enhanced_prompt_path, "w", encoding="utf-8") as f:
                    f.write(enhanced_prompt)
                self.logger.info(f"Saved enhanced prompt to {enhanced_prompt_path}")

        tasks = []
        model_names = []

        # Add tasks for each available model
        for model in self.available_models:
            # Skip models without get_X_response methods
            handler_method = f"get_{model}_response"
            if not hasattr(self, handler_method):
                self.logger.warning(f"No handler method for model: {model}")
                continue

            tasks.append(getattr(self, handler_method)(enhanced_prompt))
            model_names.append(model)
            self.logger.debug(f"Added task for model: {model}")

        if not tasks:
            error_msg = "No models available for initial responses"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        self.logger.info(f"Running {len(tasks)} model tasks in parallel")
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any failed responses
        results = {}
        for model, response in zip(model_names, responses):
            if isinstance(response, Exception):
                self.logger.error(f"Error from {model}: {response}")
                continue

            # Safely check if response is valid and has a length
            if response and not isinstance(response, Exception):
                try:
                    self.logger.info(
                        f"Got response from {model} ({len(str(response))} chars)"
                    )
                    results[model] = str(response)
                except Exception as e:
                    self.logger.error(f"Error processing response from {model}: {e}")
            else:
                self.logger.warning(f"Empty response from {model}")

        if not results:
            error_msg = "All models failed to provide responses"
            self.logger.error(error_msg)
            raise APIError(error_msg)

        self.logger.info(
            f"Got initial responses from {len(results)} models: {', '.join(results.keys())}"
        )
        return results

    async def get_meta_responses(
        self, initial_responses: Dict[str, str], original_prompt: str
    ) -> Dict[str, str]:
        """Get meta-level responses from available models"""
        self.logger.info("Getting meta-level responses")

        meta_responses = {}
        tasks = []
        model_names = []

        for model, response in initial_responses.items():
            if model not in self.available_models:
                self.logger.warning(
                    f"Model {model} is no longer available, skipping meta analysis"
                )
                continue

            # Create context for this model's meta analysis
            other_responses = {k: v for k, v in initial_responses.items() if k != model}
            context = {
                "original_prompt": original_prompt,
                "own_response": response,
                "other_responses": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in other_responses.items()
                ),
            }

            # Add task for this model
            handler_method = f"get_{model}_response"
            if not hasattr(self, handler_method):
                self.logger.warning(f"No handler method for model: {model}")
                continue

            prompt = self._create_stage_prompt("meta", context)
            tasks.append(getattr(self, handler_method)(prompt))
            model_names.append(model)

        if not tasks:
            error_msg = "No models available for meta responses"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        self.logger.info(f"Running {len(tasks)} model tasks for meta analysis")
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for model, response in zip(model_names, responses):
            if isinstance(response, Exception):
                self.logger.error(
                    f"Error getting meta response from {model}: {response}"
                )
                continue

            # Safe response handling
            if response and not isinstance(response, Exception):
                try:
                    self.logger.info(
                        f"Got meta response from {model} ({len(str(response))} chars)"
                    )
                    meta_responses[model] = str(response)
                except Exception as e:
                    self.logger.error(
                        f"Error processing meta response from {model}: {e}"
                    )
            else:
                self.logger.warning(f"Empty meta response from {model}")

        if not meta_responses:
            self.logger.warning(
                "No successful meta responses received, using initial responses instead"
            )
            return initial_responses

        return meta_responses

    async def get_hyper_responses(
        self,
        meta_responses: Dict[str, str],
        initial_responses: Dict[str, str],
        original_prompt: str,
    ) -> Dict[str, str]:
        """Get hyper-level responses from available models"""
        self.logger.info("Getting hyper-level responses")

        hyper_responses = {}
        tasks = []
        model_names = []

        for model, meta_response in meta_responses.items():
            if model not in self.available_models:
                self.logger.warning(
                    f"Model {model} is no longer available, skipping hyper analysis"
                )
                continue

            # Create context for this model's hyper analysis
            context = {
                "original_prompt": original_prompt,
                "own_meta": meta_response,
                "other_meta_responses": "\n\n".join(
                    f"{k.upper()}:\n{v}"
                    for k, v in meta_responses.items()
                    if k != model
                ),
                "own_response": initial_responses.get(model, ""),
                "critiques": "\n\n".join(
                    f"{k.upper()}:\n{v}"
                    for k, v in meta_responses.items()
                    if k != model
                ),
                "fact_checks": "\n\n".join(
                    f"{k.upper()}:\n{v}"
                    for k, v in meta_responses.items()
                    if k != model
                ),
            }

            # Add task for this model
            handler_method = f"get_{model}_response"
            if not hasattr(self, handler_method):
                self.logger.warning(f"No handler method for model: {model}")
                continue

            prompt = self._create_stage_prompt("hyper", context)
            tasks.append(getattr(self, handler_method)(prompt))
            model_names.append(model)

        if not tasks:
            error_msg = "No models available for hyper responses"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        self.logger.info(f"Running {len(tasks)} model tasks for hyper analysis")
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for model, response in zip(model_names, responses):
            if isinstance(response, Exception):
                self.logger.error(
                    f"Error getting hyper response from {model}: {response}"
                )
                continue
            if response:
                self.logger.info(
                    f"Got hyper response from {model} ({len(response)} chars)"
                )
                hyper_responses[model] = response
            else:
                self.logger.warning(f"Empty hyper response from {model}")

        if not hyper_responses:
            self.logger.warning(
                "No successful hyper responses received, using meta responses instead"
            )
            return meta_responses

        return hyper_responses

    async def get_ultra_response(
        self, hyper_responses: Dict[str, str], original_prompt: str
    ) -> str:
        """Get final ultra-level synthesis"""
        self.logger.info(f"Getting ultra-level synthesis using {self.ultra_model}")

        if not self.ultra_model:
            error_msg = "No ultra model selected"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        if self.ultra_model not in self.available_models:
            error_msg = f"Selected ultra model '{self.ultra_model}' is not available. Available models: {', '.join(self.available_models)}"
            self.logger.error(error_msg)

            # Try to select an alternative model
            if hyper_responses:
                alternative = list(hyper_responses.keys())[0]
                self.logger.info(
                    f"Using alternative model for ultra synthesis: {alternative}"
                )
                self.ultra_model = alternative
            else:
                raise ValidationError(error_msg)

        context = {
            "original_prompt": original_prompt,
            "hyper_responses": "\n\n".join(
                f"{k.upper()}:\n{v}" for k, v in hyper_responses.items()
            ),
        }

        # Get the prompt for ultra stage
        try:
            prompt = self._create_stage_prompt("ultra", context)
        except Exception as e:
            self.logger.error(f"Error creating ultra prompt: {e}")
            raise ValidationError(f"Error creating ultra prompt: {str(e)}")

        # Get the ultra response
        handler_method = f"get_{self.ultra_model}_response"
        if not hasattr(self, handler_method):
            error_msg = f"No handler method for model: {self.ultra_model}"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            self.logger.info(f"Calling {self.ultra_model} for ultra synthesis")
            ultra_response = await getattr(self, handler_method)(prompt)

            if not ultra_response:
                self.logger.warning(f"Empty ultra response from {self.ultra_model}")
                # Try to use the best hyper response as fallback
                if hyper_responses:
                    self.logger.info(
                        "Using best hyper response as ultra response fallback"
                    )
                    return list(hyper_responses.values())[0]
                else:
                    raise APIError(
                        f"Empty response from {self.ultra_model} and no fallback available"
                    )

            self.logger.info(f"Got ultra response ({len(ultra_response)} chars)")
            return ultra_response
        except Exception as e:
            self.logger.error(
                f"Error getting ultra response from {self.ultra_model}: {e}"
            )

            # Try with another model if available
            if self.ultra_model in hyper_responses:
                self.logger.warning(
                    f"Using {self.ultra_model}'s hyper response as fallback"
                )
                return hyper_responses[self.ultra_model]

            # Or use any hyper response
            if hyper_responses:
                fallback_model = list(hyper_responses.keys())[0]
                self.logger.warning(
                    f"Using {fallback_model}'s hyper response as fallback"
                )
                return hyper_responses[fallback_model]

            raise APIError(
                f"Error getting ultra response and no fallback available: {str(e)}"
            )

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        """Execute the full orchestration process"""
        # Safely access pattern name
        pattern_name = (
            self.pattern.name
            if self.pattern and hasattr(self.pattern, "name")
            else "unknown_pattern"
        )
        self.logger.info(f"Running pattern: {pattern_name}")

        # Create a session directory for this analysis
        self._create_session_directory(prompt)

        # Save the prompt
        self._save_response(prompt, "prompt")

        # Get initial responses from all available models
        self.logger.info("Getting initial responses...")
        initial_responses = await self.get_initial_responses(prompt)

        # Save initial responses
        for model, response in initial_responses.items():
            self._save_response(response, "initial", model)

        # Get meta-level responses
        self.logger.info("Running meta-level analysis...")
        meta_responses = await self.get_meta_responses(initial_responses, prompt)

        # Save meta responses
        for model, response in meta_responses.items():
            self._save_response(response, "meta", model)

        # Get hyper-level responses
        self.logger.info("Running hyper-level synthesis...")
        hyper_responses = await self.get_hyper_responses(
            meta_responses, initial_responses, prompt
        )

        # Save hyper responses
        for model, response in hyper_responses.items():
            self._save_response(response, "hyper", model)

        # Prepare final ultra-level synthesis
        self.logger.info("Producing final ultra-level synthesis...")
        ultra_response = await self.get_ultra_response(hyper_responses, prompt)

        # Save ultra response
        self._save_response(ultra_response, "ultra")

        # Use a default value if ultra_model is None
        ultra_model_safe = self.ultra_model if self.ultra_model else "unknown"

        # Save metadata
        self._save_metadata(
            prompt=prompt,
            pattern=pattern_name,
            models=list(initial_responses.keys()),
            ultra_model=ultra_model_safe,
        )

        self.logger.info("Pattern execution complete")

        # Collect performance metrics
        performance_metrics = {
            "num_models": len(initial_responses),
            "models_used": list(initial_responses.keys()),
            "ultra_model": ultra_model_safe,
            "pattern": pattern_name,
            "has_attachments": len(self.file_attachments) > 0,
            "num_attachments": len(self.file_attachments),
            "attachment_files": [os.path.basename(f) for f in self.file_attachments],
        }

        # Save performance metrics
        perf_data = json.dumps(performance_metrics, indent=2)
        self._save_response(perf_data, "performance")

        # Create output mapping for returning
        result = {
            "pattern": pattern_name,
            "initial_responses": initial_responses,
            "meta_responses": meta_responses,
            "hyper_responses": hyper_responses,
            "ultra_response": ultra_response,
            "performance": performance_metrics,
            "output_dir": self.current_session_dir,
            "attachments": (
                [os.path.basename(f) for f in self.file_attachments]
                if self.file_attachments
                else []
            ),
        }

        print("\n=========== FINAL RESULT ===========")
        print(f"```markdown\n{ultra_response}\n```")
        print("====================================")
        print(f"\nAll results saved to: {self.current_session_dir}")

        if self.file_attachments:
            print(f"\nAnalysis included {len(self.file_attachments)} attached files:")
            for i, file_path in enumerate(self.file_attachments, 1):
                print(f"  {i}. {os.path.basename(file_path)}")

        return result

    def _get_pattern(self, pattern: str) -> Optional[AnalysisPattern]:
        """Get the analysis pattern configuration"""
        patterns = {
            "gut": get_pattern_mapping().get("gut"),
            "confidence": get_pattern_mapping().get("confidence"),
            "critique": get_pattern_mapping().get("critique"),
            "fact_check": get_pattern_mapping().get("fact_check"),
            "perspective": get_pattern_mapping().get("perspective"),
            "scenario": get_pattern_mapping().get("scenario"),
        }
        if pattern not in patterns:
            raise ValueError(f"Unknown pattern: {pattern}")
        return patterns[pattern]

    def _get_formatter(self, output_format: str):
        """Get the output formatter function"""
        formatters = {
            "plain": lambda x: x,
            "markdown": lambda x: f"```markdown\n{x}\n```",
            "json": lambda x: json.dumps({"response": x}, indent=2),
        }
        if output_format not in formatters:
            raise ValueError(f"Unknown output format: {output_format}")
        return formatters[output_format]

    # Main execution function
    async def execute(self, prompt: str) -> str:
        """Execute the full pattern-based orchestration for a given prompt"""
        # Safely access pattern name
        pattern_name = (
            self.pattern.name
            if self.pattern and hasattr(self.pattern, "name")
            else "unknown_pattern"
        )
        self.logger.info(f"Running pattern: {pattern_name}")

        # Initial responses
        self.logger.info("Getting initial responses...")
        initial_responses = await self.get_initial_responses(prompt)
        if not initial_responses:
            raise ValueError(
                "No successful responses received from any models. Please check your API keys and model availability."
            )

        # Meta-level analysis
        self.logger.info("Running meta-level analysis...")
        meta_responses = await self.get_meta_responses(initial_responses, prompt)
        if not meta_responses:
            raise ValueError(
                "No successful meta responses received. Please check model availability."
            )

        # Hyper-level synthesis
        self.logger.info("Running hyper-level synthesis...")
        hyper_responses = await self.get_hyper_responses(
            meta_responses, initial_responses, prompt
        )
        if not hyper_responses:
            raise ValueError(
                "No successful hyper responses received. Please check model availability."
            )

        # Ultra-level synthesis
        self.logger.info("Producing final ultra-level synthesis...")
        ultra_response = await self.get_ultra_response(hyper_responses, prompt)

        self.logger.info("Pattern execution complete")
        return self.formatter(ultra_response)

    def _sanitize_filename(self, text: str) -> str:
        """Create a safe filename from text"""
        # Remove any characters that aren't alphanumeric, underscore, or dash
        sanitized = re.sub(r"[^\w\-]", "_", text)
        # Truncate to a reasonable length
        return sanitized[:50]

    def _create_session_directory(self, prompt: str):
        """Create a new session directory to store all outputs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_summary = self._sanitize_filename(prompt[:30])
        session_dir = os.path.join(self.outputs_dir, f"{timestamp}_{prompt_summary}")
        os.makedirs(session_dir, exist_ok=True)
        self.current_session_dir = session_dir
        return session_dir

    def _save_response(self, response: str, stage: str, model: Optional[str] = None):
        """Save a response to a file in the current session directory"""
        if not self.current_session_dir:
            self.logger.warning("No session directory available, cannot save response")
            return None

        filename = f"{stage}"
        if model:
            filename += f"_{model}"
        filename += ".txt"

        filepath = os.path.join(self.current_session_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response)
            self.logger.info(f"Saved {stage} response to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error saving response to {filepath}: {e}")
            return None

    def _save_metadata(
        self, prompt: str, pattern: str, models: List[str], ultra_model: str
    ):
        """Save metadata about this analysis session"""
        if not self.current_session_dir:
            return None

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "pattern": pattern,
            "models_used": models,
            "ultra_model": ultra_model,
            "system_info": {
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
        }

        # Add file attachment info if available
        if self.file_attachments:
            metadata["attachments"] = {
                "count": len(self.file_attachments),
                "files": [
                    {
                        "filename": os.path.basename(path),
                        "path": path,
                        "size_bytes": (
                            os.path.getsize(path) if os.path.exists(path) else 0
                        ),
                        "extension": os.path.splitext(path)[1].lower(),
                    }
                    for path in self.file_attachments
                ],
            }

        filepath = os.path.join(self.current_session_dir, "metadata.json")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
            self.logger.info(f"Saved session metadata to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error saving metadata to {filepath}: {e}")
            return None

    def attach_file(self, file_path: str) -> bool:
        """
        Attach a file to be used as context for the analysis.

        Args:
            file_path: Path to the file to attach

        Returns:
            bool: True if the file was successfully attached, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False

        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Check if file type is supported
        if not self.documents_processor:
            self.logger.error("Document processor not available")
            return False

        supported_formats = self.documents_processor.supported_formats.keys()
        if ext not in supported_formats:
            self.logger.error(
                f"Unsupported file format: {ext}. Supported formats: {', '.join(supported_formats)}"
            )
            return False

        # Add file to attachments
        self.file_attachments.append(file_path)
        self.logger.info(f"File attached: {file_path}")
        return True

    def clear_attachments(self):
        """Clear all attached files"""
        self.file_attachments = []
        self.logger.info("All file attachments cleared")

    def _process_attachments(self) -> Optional[str]:
        """
        Process all attached files and return their contents.

        Returns:
            str: Combined content from all attached files, or None if processing failed
        """
        if not self.file_attachments:
            self.logger.info("No file attachments to process")
            return None

        if not self.documents_processor:
            self.logger.error("Document processor not available")
            return None

        try:
            # Use the enhanced RAG-based processing if available
            if hasattr(self.documents_processor, "process_query_with_documents"):
                # This method automatically handles chunking and semantic retrieval
                prompt = (
                    "Please analyze these documents"  # Generic prompt for embedding
                )
                enhanced_prompt = self.documents_processor.process_query_with_documents(
                    prompt, self.file_attachments, max_chunks=10
                )

                # Remove the generic prompt and instructions as we'll add our own
                if "--- RELEVANT DOCUMENT EXCERPTS ---" in enhanced_prompt:
                    try:
                        _, content = enhanced_prompt.split(
                            "--- RELEVANT DOCUMENT EXCERPTS ---", 1
                        )
                        content, _ = content.split(
                            "Please provide a comprehensive response", 1
                        )
                        return content.strip()
                    except ValueError:
                        # If split fails, return the whole content
                        return enhanced_prompt
                elif "--- CONTENT FROM ATTACHED DOCUMENTS ---" in enhanced_prompt:
                    try:
                        _, content = enhanced_prompt.split(
                            "--- CONTENT FROM ATTACHED DOCUMENTS ---", 1
                        )
                        content, _ = content.split("Based on the above documents", 1)
                        return content.strip()
                    except ValueError:
                        # If split fails, return the whole content
                        return enhanced_prompt

                # Fallback: return the whole processed prompt
                return enhanced_prompt

            # Fallback to the original document processing
            results = self.documents_processor.process_documents(self.file_attachments)

            # Format the results
            formatted_content = []
            for i, (file_path, content) in enumerate(results.items()):
                if content.startswith("Error:"):
                    self.logger.error(f"Error processing {file_path}: {content}")
                    continue

                filename = os.path.basename(file_path)

                # Truncate very long content for better prompt management
                max_length = 8000  # Character limit per document
                if len(content) > max_length:
                    content = (
                        content[:max_length]
                        + f"... [Document truncated, {len(content)} total characters]"
                    )

                formatted_content.append(f"[DOCUMENT {i+1}: {filename}]\n{content}\n")

            if not formatted_content:
                self.logger.warning("No content extracted from attached files")
                return None

            combined_content = "\n".join(formatted_content)

            # Save attachments to the session directory
            if self.current_session_dir:
                attachment_info = {
                    "files": [
                        {
                            "filename": os.path.basename(path),
                            "path": path,
                            "size_bytes": (
                                os.path.getsize(path) if os.path.exists(path) else 0
                            ),
                            "extension": os.path.splitext(path)[1].lower(),
                        }
                        for path in self.file_attachments
                    ]
                }
                attachments_file = os.path.join(
                    self.current_session_dir, "attachments.json"
                )
                with open(attachments_file, "w", encoding="utf-8") as f:
                    json.dump(attachment_info, f, indent=2)
                self.logger.info(f"Saved attachments info to {attachments_file}")

            return combined_content

        except Exception as e:
            self.logger.error(f"Error processing attachments: {e}")
            return None

    def configure_gemini(self):
        """Configure the Gemini API client"""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ConfigurationError(
                    "GEMINI_API_KEY is missing from environment variables"
                )

            # Use the public API for configuration
            genai.configure(api_key=api_key)

            self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-pro")
            self.logger.info("Gemini API configured successfully")
        except Exception as e:
            self.logger.error("Error configuring Gemini API: %s", str(e))
            raise ConfigurationError(f"Failed to configure Gemini API: {str(e)}")

    def error_handler(self, e, attempt, max_attempts, provider, task=None):
        """Handle API errors with exponential backoff"""
        # Check if it's a rate limit error
        is_rate_limit = isinstance(e, RateLimitError)

        # Use str(e) instead of len(e) to check if there's an error message
        error_str = str(e)
        has_error_message = bool(error_str)

        # ... rest of the method ...

    def iterate_results(self, results):
        """Safely iterate over results, handling various result types"""
        if results is None:
            return []
        if isinstance(results, dict):
            return [results]
        if isinstance(results, list):
            return results
        return [results]  # Convert any other type to a single-item list

    def create_prompt(self, stage, pattern=None):
        """Create a prompt for the given stage and pattern"""
        try:
            # ... existing code ...
            self.logger.error(
                "Failed to create prompt for stage '%s': %s", stage, str(e)
            )
            raise ValidationError(
                f"Failed to create prompt for stage '{stage}': {str(e)}"
            ) from e

        except Exception as e:
            self.logger.error(
                "Error getting ultra response and no fallback available: %s", str(e)
            )
            raise APIError(
                f"Error getting ultra response and no fallback available: {str(e)}"
            ) from e

    def create_ultra_prompt(self, template_name, substitutions):
        """Create a prompt from a template with substitutions"""
        try:
            # ... existing code ...
            template = self.get_template(template_name)
            if not template:
                raise ValidationError(f"Template {template_name} not found")

            return template.substitute(substitutions)
        except Exception as e:
            self.logger.error("Error creating ultra prompt: %s", str(e))
            raise ValidationError(f"Error creating ultra prompt: {str(e)}") from e

        except Exception as e:
            self.logger.error(
                "Error getting ultra response and no fallback available: %s", str(e)
            )
            raise APIError(
                f"Error getting ultra response and no fallback available: {str(e)}"
            ) from e


class ResponseFormatter:
    @staticmethod
    def format_plain(text: str) -> str:
        return text

    @staticmethod
    def format_markdown(text: str) -> str:
        return text

    @staticmethod
    def format_json(text: str) -> str:
        return json.dumps({"response": text}, indent=2)


async def test_env() -> bool:
    """Test if all required environment variables are set"""
    required_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        print(f"\nError: {error_msg}")
        print("\nPlease set these variables in your .env file")
        raise ConfigurationError(error_msg)

    # Check for optional variables
    optional_vars = ["MISTRAL_API_KEY", "PERPLEXITY_API_KEY", "COHERE_API_KEY"]

    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_optional:
        logger.info(f"Optional API keys not set: {', '.join(missing_optional)}")
        print("\nNote: Optional API keys not set:")
        for var in missing_optional:
            print(f"- {var}")
        print("These services will not be available for use.")

    logger.info("All required environment variables are set")
    print("\nAll required environment variables are set")
    return True


async def main():
    # Initialize the orchestrator
    print("\nInitializing Pattern Orchestrator...")

    try:
        # Test environment
        await test_env()

        # Get the analysis patterns
        analysis_patterns = get_pattern_mapping()
        patterns = [
            analysis_patterns.get("gut"),
            analysis_patterns.get("confidence"),
            analysis_patterns.get("critique"),
            analysis_patterns.get("fact_check"),
            analysis_patterns.get("perspective"),
            analysis_patterns.get("scenario"),
            analysis_patterns.get("stakeholder"),
            analysis_patterns.get("systems"),
            analysis_patterns.get("time"),
            analysis_patterns.get("innovation"),
        ]

        # Filter out None patterns
        patterns = [p for p in patterns if p is not None]

        # Display available patterns
        print("\nAvailable analysis patterns:")
        for i, pattern in enumerate(patterns, 1):
            pattern_name = pattern.name if hasattr(pattern, "name") else f"Pattern {i}"
            print(f"{i}. {pattern_name}")

        # Get user choice
        choice = int(input("\nEnter your choice (1-10): ")) - 1
        if choice < 0 or choice >= len(patterns):
            print("Invalid choice. Exiting.")
            return

        pattern = patterns[choice]
        pattern_name = pattern.name if hasattr(pattern, "name") else "unknown"

        # Get user choice for ultra model
        print("\nSelect the LLM for ultra synthesis:")
        print("1. Claude (Recommended for complex synthesis)")
        print("2. ChatGPT")
        print("3. Gemini")
        print("4. Llama (If you have Ollama installed)")

        model_choice = int(input("\nEnter your choice (1-4): "))
        if model_choice == 1:
            ultra_model = "claude"
        elif model_choice == 2:
            ultra_model = "chatgpt"
        elif model_choice == 3:
            ultra_model = "gemini"
        elif model_choice == 4:
            ultra_model = "llama"
        else:
            print("Invalid choice. Using Claude as default.")
            ultra_model = "claude"

        # Initialize orchestrator with the selected pattern and model
        pattern_name_map = {
            "Gut Analysis": "gut",
            "Confidence Analysis": "confidence",
            "Critique Analysis": "critique",
            "Fact Check Analysis": "fact_check",
            "Perspective Analysis": "perspective",
            "Scenario Analysis": "scenario",
        }

        # Get pattern ID safely
        pattern_id = (
            pattern_name_map.get(pattern_name)
            if pattern_name in pattern_name_map
            else "gut"
        )

        # Filter None values from API keys
        api_keys = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "google": os.getenv("GOOGLE_API_KEY", ""),
            "perplexity": os.getenv("PERPLEXITY_API_KEY", ""),
            "cohere": os.getenv("COHERE_API_KEY", ""),
            "mistral": os.getenv("MISTRAL_API_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
        }
        # Remove empty keys
        api_keys = {k: v for k, v in api_keys.items() if v}

        orchestrator = PatternOrchestrator(
            api_keys=api_keys, pattern=pattern_id, output_format="markdown"
        )
        orchestrator.pattern = pattern  # Set the full pattern object
        orchestrator.ultra_model = ultra_model

        # File attachment option
        attach_files = (
            input("\nWould you like to attach files for analysis? (y/n): ")
            .lower()
            .strip()
        )
        if attach_files == "y":
            print("\nSupported file formats: .pdf, .txt, .md, .docx")

            while True:
                file_path = input(
                    "\nEnter the file path (or press Enter to stop adding files): "
                ).strip()
                if not file_path:
                    break

                # Try to attach the file
                if orchestrator.attach_file(file_path):
                    print(f"File attached: {file_path}")
                else:
                    print(f"Could not attach file: {file_path}")

            # Summary of attached files
            if orchestrator.file_attachments:
                print(f"\n{len(orchestrator.file_attachments)} files attached:")
                for i, file_path in enumerate(orchestrator.file_attachments, 1):
                    print(f"  {i}. {file_path}")
            else:
                print("\nNo files attached.")

        # Get user prompt
        default_prompt = (
            "What are the most common misconceptions about artificial intelligence?"
        )
        user_prompt = input("\nEnter your prompt (press Enter to use default): ")
        if not user_prompt:
            user_prompt = default_prompt

        # Safe access to pattern name
        start_pattern_name = pattern.name if hasattr(pattern, "name") else "unknown"
        print(
            f"\nStarting {start_pattern_name} process with {ultra_model.upper()} for ultra synthesis..."
        )
        if orchestrator.file_attachments:
            print(
                f"Including {len(orchestrator.file_attachments)} attached files in the analysis."
            )

        # Execute the pattern
        result = await orchestrator.orchestrate_full_process(user_prompt)

        # Display result
        print("\n=========== FINAL RESULT ===========")
        print(result["ultra_response"])
        print("====================================")

    except Exception as e:
        print(f"Error: {e}")
        if (
            "ANTHROPIC_API_KEY" in str(e)
            or "OPENAI_API_KEY" in str(e)
            or "GOOGLE_API_KEY" in str(e)
        ):
            print("\nPlease ensure all required API keys are set in your .env file:")
            print("- ANTHROPIC_API_KEY for Claude")
            print("- OPENAI_API_KEY for ChatGPT/GPT-4")
            print("- GOOGLE_API_KEY for Gemini")


if __name__ == "__main__":
    asyncio.run(main())
