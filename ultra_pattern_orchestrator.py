import asyncio
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime, timedelta
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import os
from dotenv import load_dotenv
from string import Template
import httpx
from llama_cpp import Llama
import sys
import traceback
import platform
import shutil
import re

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
import google.generativeai as genai
from google.generativeai import GenerativeModel
from mistralai.async_client import MistralAsyncClient
import cohere

from ultra_analysis_patterns import AnalysisPatterns, AnalysisPattern
from ultra_error_handling import ValidationError, ConfigurationError, APIError, RateLimitError

# Define custom exception classes
class UltraError(Exception):
    """Base exception for Ultra platform errors."""
    pass

class APIError(UltraError):
    """Exception for API-related errors."""
    pass

class RateLimitError(UltraError):
    """Exception for rate limit violations."""
    pass

class ConfigurationError(UltraError):
    """Exception for configuration-related errors."""
    pass

class ValidationError(UltraError):
    """Exception for input validation errors."""
    pass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultra_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PatternOrchestrator:
    def __init__(self, 
                 api_keys: Dict[str, str],
                 pattern: str = "gut",
                 output_format: str = "plain"):
        """Initialize the Pattern Orchestrator"""
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
        
        # Load pattern
        self.pattern = AnalysisPatterns().get_pattern(pattern)
        if not self.pattern:
            raise ValidationError(f"Invalid pattern: {pattern}")
            
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
        
        # Initialize API clients
        self._initialize_clients()
            
    def _initialize_clients(self):
        """Initialize API clients and check which models are available"""
        try:
            # Claude (Anthropic)
            if self.anthropic_key:
                self.anthropic = AsyncAnthropic(api_key=self.anthropic_key)
                self.available_models.append("claude")
                self.last_request["claude"] = datetime.now()
                self.logger.info("Claude client initialized")
            else:
                self.logger.warning("Claude not available - API key missing")
            
            # ChatGPT (OpenAI)
            if self.openai_key:
                self.openai = AsyncOpenAI(api_key=self.openai_key)
                self.available_models.append("chatgpt")
                self.last_request["chatgpt"] = datetime.now()
                self.logger.info("ChatGPT client initialized")
            else:
                self.logger.warning("ChatGPT not available - API key missing")
            
            # Gemini (Google)
            if self.google_key:
                genai.configure(api_key=self.google_key)
                self.available_models.append("gemini")
                self.last_request["gemini"] = datetime.now()
                self.logger.info("Gemini client initialized")
            else:
                self.logger.warning("Gemini not available - API key missing")
            
            # Perplexity
            if self.perplexity_key:
                self.available_models.append("perplexity")
                self.last_request["perplexity"] = datetime.now()
                self.logger.info("Perplexity client initialized")
            else:
                self.logger.warning("Perplexity not available - API key missing")
            
            # Cohere
            if self.cohere_key:
                self.cohere = cohere.Client(api_key=self.cohere_key)
                self.available_models.append("cohere")
                self.last_request["cohere"] = datetime.now()
                self.logger.info("Cohere client initialized")
            else:
                self.logger.warning("Cohere not available - API key missing")
                
            # Mistral
            if self.mistral_key:
                self.mistral = MistralAsyncClient(api_key=self.mistral_key)
                self.available_models.append("mistral")
                self.last_request["mistral"] = datetime.now()
                self.logger.info("Mistral client initialized")
            else:
                self.logger.warning("Mistral not available - API key missing")
                
            # DeepSeek
            if self.deepseek_key:
                self.deepseek = AsyncOpenAI(
                    api_key=self.deepseek_key,
                    base_url="https://api.deepseek.com/v1"
                )
                self.available_models.append("deepseek")
                self.last_request["deepseek"] = datetime.now()
                self.logger.info("DeepSeek client initialized")
            else:
                self.logger.warning("DeepSeek not available - API key missing")
            
            # Llama will be checked on first use
            self.last_request["llama"] = datetime.now()
            
            if not self.available_models:
                raise ConfigurationError("No API clients could be initialized. Please check your API keys.")
                
            self.logger.info(f"Available models: {', '.join(self.available_models)}")
            
        except Exception as e:
            self.logger.error(f"Error initializing clients: {e}")
            raise ConfigurationError(f"Failed to initialize API clients: {str(e)}")
            
    async def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running and accessible"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:11434/api/version")
                response.raise_for_status()
                return True
            except Exception as e:
                raise Exception(f"Ollama not available: {e}")

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def get_claude_response(self, prompt: str) -> str:
        """Get response from Claude API"""
        if "claude" not in self.available_models:
            self.logger.warning("Claude is not available")
            return ""
            
        await self._respect_rate_limit("claude")
        try:
            message = await self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
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
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def get_chatgpt_response(self, prompt: str) -> str:
        """Get response from ChatGPT"""
        if "chatgpt" not in self.available_models:
            self.logger.warning("ChatGPT is not available")
            return ""
            
        await self._respect_rate_limit("chatgpt")
        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            return response.choices[0].message.content
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
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini API"""
        if "gemini" not in self.available_models:
            self.logger.warning("Gemini is not available")
            return ""
            
        await self._respect_rate_limit("gemini")
        try:
            # Different versions of the API have different structures
            try:
                # Newer API version
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = await model.generate_content_async(prompt)
                return response.text
            except (AttributeError, TypeError):
                # Older API version fallback
                response = await asyncio.to_thread(
                    genai.generate_text,
                    model="gemini-pro",
                    prompt=prompt,
                    temperature=0.7
                )
                return response.text
        except Exception as e:
            if "rate limit" in str(e).lower():
                self.logger.error(f"Gemini rate limit exceeded: {e}")
                raise RateLimitError(f"Gemini rate limit exceeded: {e}")
            else:
                self.logger.error(f"Error with Gemini API: {e}")
                raise APIError(f"Error with Gemini API: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_perplexity_response(self, prompt: str) -> str:
        """Get response from Perplexity API"""
        try:
            await self._respect_rate_limit("perplexity")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "pplx-7b-online",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"Error with Perplexity API: {e}")
            return ""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_cohere_response(self, prompt: str) -> str:
        """Get response from Cohere API"""
        try:
            await self._respect_rate_limit("cohere")
            response = self.cohere.chat(
                message=prompt,
                model="command"
            )
            return response.text
        except Exception as e:
            logging.error(f"Error with Cohere API: {e}")
            return ""

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def get_llama_response(self, prompt: str) -> str:
        """Get response from Ollama's Llama model"""
        # Check Ollama availability if we haven't yet
        if self.ollama_available is None:
            try:
                await self._check_ollama_availability()
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
                    model_check = await client.get("http://localhost:11434/api/tags")
                    model_check.raise_for_status()
                    available_models = model_check.json()
                    
                    # Check if either model exists in the response
                    models = [m["name"] for m in available_models.get("models", [])]
                    if not any(m.startswith("llama3") for m in models):
                        if not any(m.startswith("llama2") for m in models):
                            # Neither model exists
                            self.logger.warning("Neither llama3 nor llama2 found in Ollama. Using default model.")
                            model_to_use = "llama2"  # Default to llama2 even if not found
                        else:
                            model_to_use = "llama2"
                except Exception as e:
                    # If we can't check the models, default to llama2
                    self.logger.warning(f"Could not check available models: {e}. Using llama2 as default.")
                    model_to_use = "llama2"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": f"{model_to_use}:latest",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "num_predict": 1024
                        }
                    }
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            self.logger.error(f"Error with Ollama: {e}")
            # Don't retry for Ollama errors as they're likely local issues
            return ""

    async def _respect_rate_limit(self, model: str):
        """Respect rate limits between API calls"""
        try:
            current_time = datetime.now()
            last_call = self.last_request.get(model, current_time - timedelta(seconds=10))
            
            # Set different wait times based on model type
            wait_seconds = {
                "claude": 1.0,    # 60 RPM (requests per minute)
                "chatgpt": 3.0,   # 20 RPM 
                "gemini": 1.0,    # 60 RPM
                "perplexity": 3.0, # 20 RPM
                "cohere": 2.0,    # 30 RPM
                "mistral": 2.0,   # 30 RPM
                "deepseek": 1.0,  # 60 RPM
                "llama": 0.5      # 120 RPM (local, so faster)
            }.get(model, 2.0)     # Default 2s (30 RPM)
            
            wait_time = max(0, wait_seconds - (current_time - last_call).total_seconds())
            
            if wait_time > 0:
                self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {model}")
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
            template = self.pattern.templates.get(stage)
            if not template:
                raise ValidationError(f"Unknown stage: {stage}")
                
            # Apply template variables
            return Template(template).safe_substitute(context)
        except Exception as e:
            self.logger.error(f"Error creating prompt for stage '{stage}': {e}")
            raise ValidationError(f"Failed to create prompt for stage '{stage}': {str(e)}")

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
            
        tasks = []
        model_names = []
        
        # Add tasks for each available model
        for model in self.available_models:
            # Skip models without get_X_response methods
            handler_method = f"get_{model}_response"
            if not hasattr(self, handler_method):
                self.logger.warning(f"No handler method for model: {model}")
                continue
                
            tasks.append(getattr(self, handler_method)(prompt))
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
            if response:  # Only add non-empty responses
                self.logger.info(f"Got response from {model} ({len(response)} chars)")
                results[model] = response
            else:
                self.logger.warning(f"Empty response from {model}")
                
        if not results:
            error_msg = "All models failed to provide responses"
            self.logger.error(error_msg)
            raise APIError(error_msg)
            
        self.logger.info(f"Got initial responses from {len(results)} models: {', '.join(results.keys())}")
        return results

    async def get_meta_responses(self, initial_responses: Dict[str, str], 
                               original_prompt: str) -> Dict[str, str]:
        """Get meta-level responses from available models"""
        self.logger.info("Getting meta-level responses")
        
        meta_responses = {}
        tasks = []
        model_names = []
        
        for model, response in initial_responses.items():
            if model not in self.available_models:
                self.logger.warning(f"Model {model} is no longer available, skipping meta analysis")
                continue
                
            # Create context for this model's meta analysis
            other_responses = {k: v for k, v in initial_responses.items() if k != model}
            context = {
                "original_prompt": original_prompt,
                "own_response": response,
                "other_responses": "\n\n".join(f"{k.upper()}:\n{v}" for k, v in other_responses.items())
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
                self.logger.error(f"Error getting meta response from {model}: {response}")
                continue
            if response:
                self.logger.info(f"Got meta response from {model} ({len(response)} chars)")
                meta_responses[model] = response
            else:
                self.logger.warning(f"Empty meta response from {model}")
                
        if not meta_responses:
            self.logger.warning("No successful meta responses received, using initial responses instead")
            return initial_responses
                
        return meta_responses

    async def get_hyper_responses(self, meta_responses: Dict[str, str],
                                initial_responses: Dict[str, str],
                                original_prompt: str) -> Dict[str, str]:
        """Get hyper-level responses from available models"""
        self.logger.info("Getting hyper-level responses")
        
        hyper_responses = {}
        tasks = []
        model_names = []
        
        for model, meta_response in meta_responses.items():
            if model not in self.available_models:
                self.logger.warning(f"Model {model} is no longer available, skipping hyper analysis")
                continue
                
            # Create context for this model's hyper analysis
            context = {
                "original_prompt": original_prompt,
                "own_meta": meta_response,
                "other_meta_responses": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in meta_responses.items() if k != model
                ),
                "own_response": initial_responses.get(model, ""),
                "critiques": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in meta_responses.items() if k != model
                ),
                "fact_checks": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in meta_responses.items() if k != model
                )
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
                self.logger.error(f"Error getting hyper response from {model}: {response}")
                continue
            if response:
                self.logger.info(f"Got hyper response from {model} ({len(response)} chars)")
                hyper_responses[model] = response
            else:
                self.logger.warning(f"Empty hyper response from {model}")
                
        if not hyper_responses:
            self.logger.warning("No successful hyper responses received, using meta responses instead")
            return meta_responses
                
        return hyper_responses

    async def get_ultra_response(self, hyper_responses: Dict[str, str],
                               original_prompt: str) -> str:
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
                self.logger.info(f"Using alternative model for ultra synthesis: {alternative}")
                self.ultra_model = alternative
            else:
                raise ValidationError(error_msg)
            
        context = {
            "original_prompt": original_prompt,
            "hyper_responses": "\n\n".join(
                f"{k.upper()}:\n{v}" for k, v in hyper_responses.items()
            )
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
                    self.logger.info("Using best hyper response as ultra response fallback")
                    return list(hyper_responses.values())[0]
                else:
                    raise APIError(f"Empty response from {self.ultra_model} and no fallback available")
                    
            self.logger.info(f"Got ultra response ({len(ultra_response)} chars)")
            return ultra_response
        except Exception as e:
            self.logger.error(f"Error getting ultra response from {self.ultra_model}: {e}")
            
            # Try with another model if available
            if self.ultra_model in hyper_responses:
                self.logger.warning(f"Using {self.ultra_model}'s hyper response as fallback")
                return hyper_responses[self.ultra_model]
                
            # Or use any hyper response
            if hyper_responses:
                fallback_model = list(hyper_responses.keys())[0]
                self.logger.warning(f"Using {fallback_model}'s hyper response as fallback")
                return hyper_responses[fallback_model]
                
            raise APIError(f"Error getting ultra response and no fallback available: {str(e)}")

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        """Execute the full orchestration process"""
        self.logger.info(f"Running pattern: {self.pattern.name}")
        
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
        hyper_responses = await self.get_hyper_responses(meta_responses, initial_responses, prompt)
        
        # Save hyper responses
        for model, response in hyper_responses.items():
            self._save_response(response, "hyper", model)
        
        # Prepare final ultra-level synthesis
        self.logger.info("Producing final ultra-level synthesis...")
        ultra_response = await self.get_ultra_response(hyper_responses, prompt)
        
        # Save ultra response
        self._save_response(ultra_response, "ultra")
        
        # Save metadata
        self._save_metadata(
            prompt=prompt,
            pattern=self.pattern.name,
            models=list(initial_responses.keys()),
            ultra_model=self.ultra_model
        )
        
        self.logger.info("Pattern execution complete")
        
        # Collect performance metrics
        performance_metrics = {
            "num_models": len(initial_responses),
            "models_used": list(initial_responses.keys()),
            "ultra_model": self.ultra_model,
            "pattern": self.pattern.name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save performance metrics
        perf_data = json.dumps(performance_metrics, indent=2)
        self._save_response(perf_data, "performance")
        
        # Create output mapping for returning
        result = {
            "pattern": self.pattern.name,
            "initial_responses": initial_responses,
            "meta_responses": meta_responses,
            "hyper_responses": hyper_responses,
            "ultra_response": ultra_response,
            "performance": performance_metrics,
            "output_dir": self.current_session_dir
        }
        
        print("\n=========== FINAL RESULT ===========")
        print(f"```markdown\n{ultra_response}\n```")
        print("====================================")
        print(f"\nAll results saved to: {self.current_session_dir}")
        
        return result

    def _get_pattern(self, pattern: str) -> Dict[str, Any]:
        """Get the analysis pattern configuration"""
        patterns = {
            "gut": AnalysisPatterns().get_pattern("gut"),
            "confidence": AnalysisPatterns().get_pattern("confidence"),
            "critique": AnalysisPatterns().get_pattern("critique"),
            "fact_check": AnalysisPatterns().get_pattern("fact_check"),
            "perspective": AnalysisPatterns().get_pattern("perspective"),
            "scenario": AnalysisPatterns().get_pattern("scenario")
        }
        if pattern not in patterns:
            raise ValueError(f"Unknown pattern: {pattern}")
        return patterns[pattern]

    def _get_formatter(self, output_format: str):
        """Get the output formatter function"""
        formatters = {
            "plain": lambda x: x,
            "markdown": lambda x: f"```markdown\n{x}\n```",
            "json": lambda x: json.dumps({"response": x}, indent=2)
        }
        if output_format not in formatters:
            raise ValueError(f"Unknown output format: {output_format}")
        return formatters[output_format]

    # Main execution function
    async def execute(self, prompt: str) -> str:
        """Execute the full pattern-based orchestration for a given prompt"""
        self.logger.info(f"Running pattern: {self.pattern.name}")
        
        # Initial responses
        self.logger.info("Getting initial responses...")
        initial_responses = await self.get_initial_responses(prompt)
        if not initial_responses:
            raise ValueError("No successful responses received from any models. Please check your API keys and model availability.")
        
        # Meta-level analysis
        self.logger.info("Running meta-level analysis...")
        meta_responses = await self.get_meta_responses(initial_responses, prompt)
        if not meta_responses:
            raise ValueError("No successful meta responses received. Please check model availability.")
        
        # Hyper-level synthesis
        self.logger.info("Running hyper-level synthesis...")
        hyper_responses = await self.get_hyper_responses(meta_responses, initial_responses, prompt)
        if not hyper_responses:
            raise ValueError("No successful hyper responses received. Please check model availability.")
        
        # Ultra-level synthesis
        self.logger.info("Producing final ultra-level synthesis...")
        ultra_response = await self.get_ultra_response(hyper_responses, prompt)
        
        self.logger.info("Pattern execution complete")
        return self.formatter(ultra_response)

    def _sanitize_filename(self, text: str) -> str:
        """Create a safe filename from text"""
        # Remove any characters that aren't alphanumeric, underscore, or dash
        sanitized = re.sub(r'[^\w\-]', '_', text)
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
        
    def _save_response(self, response: str, stage: str, model: str = None):
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
            
    def _save_metadata(self, prompt: str, pattern: str, models: List[str], ultra_model: str):
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
                "python": platform.python_version()
            }
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
    required_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY"
    ]
    
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
    optional_vars = [
        "MISTRAL_API_KEY",
        "PERPLEXITY_API_KEY",
        "COHERE_API_KEY"
    ]
    
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
        analysis_patterns = AnalysisPatterns()
        patterns = [
            analysis_patterns.get_pattern("gut"),
            analysis_patterns.get_pattern("confidence"),
            analysis_patterns.get_pattern("critique"),
            analysis_patterns.get_pattern("fact_check"),
            analysis_patterns.get_pattern("perspective"),
            analysis_patterns.get_pattern("scenario")
        ]
        
        # Display available patterns
        print("\nAvailable analysis patterns:")
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern.name}")
            
        # Get user choice
        choice = int(input("\nEnter your choice (1-6): ")) - 1
        if choice < 0 or choice >= len(patterns):
            print("Invalid choice. Exiting.")
            return
            
        pattern = patterns[choice]
        
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
            "Scenario Analysis": "scenario"
        }
        
        pattern_id = pattern_name_map.get(pattern.name)
        orchestrator = PatternOrchestrator(
            api_keys={
                "anthropic": os.getenv("ANTHROPIC_API_KEY"),
                "openai": os.getenv("OPENAI_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY"),
                "perplexity": os.getenv("PERPLEXITY_API_KEY"),
                "cohere": os.getenv("COHERE_API_KEY")
            },
            pattern=pattern_id,
            output_format="markdown"
        )
        orchestrator.pattern = pattern  # Set the full pattern object
        orchestrator.ultra_model = ultra_model
        
        # Get user prompt
        default_prompt = "What are the most common misconceptions about artificial intelligence?"
        user_prompt = input(f"\nEnter your prompt (press Enter to use default): ")
        if not user_prompt:
            user_prompt = default_prompt
            
        print(f"\nStarting {pattern.name} process with {ultra_model.upper()} for ultra synthesis...")
        
        # Execute the pattern
        result = await orchestrator.orchestrate_full_process(user_prompt)
        
        # Display result
        print("\n=========== FINAL RESULT ===========")
        print(result)
        print("====================================")
        
    except Exception as e:
        print(f"Error: {e}")
        if "ANTHROPIC_API_KEY" in str(e) or "OPENAI_API_KEY" in str(e) or "GOOGLE_API_KEY" in str(e):
            print("\nPlease ensure all required API keys are set in your .env file:")
            print("- ANTHROPIC_API_KEY for Claude")
            print("- OPENAI_API_KEY for ChatGPT/GPT-4")
            print("- GOOGLE_API_KEY for Gemini")

if __name__ == "__main__":
    asyncio.run(main()) 