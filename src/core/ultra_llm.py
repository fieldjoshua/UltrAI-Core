import asyncio
from typing import Any, Dict, List, Optional, Union

import google.generativeai as genai
import requests
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from ultra_base import PromptTemplate, RateLimits, UltraBase
from ultra_documents import UltraDocuments


class UltraLLM(UltraBase):
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None,
        ultra_engine: str = "chatgpt",
    ):
        super().__init__(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features,
        )
        self.ultra_engine = ultra_engine
        self.available_models = []
        self.documents = UltraDocuments(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features,
        )

    def _initialize_clients(self):
        """Initialize API clients based on enabled features."""
        # Initialize OpenAI client
        if "openai" in self.enabled_features:
            openai_api_key = self.api_keys.get("openai")
            if openai_api_key:
                self.openai_client = AsyncOpenAI(api_key=openai_api_key)
                self.available_models.append("openai")
                print("OpenAI client initialized.")
                self.logger.info("OpenAI client initialized.")
            else:
                print("OpenAI API key not found.")
                self.logger.error("OpenAI API key not found.")

        # Initialize Google Gemini client
        if "gemini" in self.enabled_features:
            google_api_key = self.api_keys.get("google")
            if google_api_key:
                genai.configure(api_key=google_api_key)
                self.available_models.append("gemini")
                print("Google Gemini client initialized.")
                self.logger.info("Google Gemini client initialized.")
            else:
                print("Google API key not found.")
                self.logger.error("Google API key not found.")

        # Initialize Anthropic Claude client
        if "anthropic" in self.enabled_features:
            anthropic_api_key = self.api_keys.get("anthropic")
            if anthropic_api_key:
                self.anthropic_client = AsyncOpenAI(
                    api_key=anthropic_api_key, base_url="https://api.anthropic.com/v1"
                )
                self.available_models.append("anthropic")
                print("Anthropic Claude client initialized.")
                self.logger.info("Anthropic Claude client initialized.")
            else:
                print("Anthropic API key not found.")
                self.logger.error("Anthropic API key not found.")

        # Initialize DeepSeek client
        if "deepseek" in self.enabled_features:
            deepseek_api_key = self.api_keys.get("deepseek")
            if deepseek_api_key:
                self.deepseek_client = AsyncOpenAI(
                    api_key=deepseek_api_key, base_url="https://api.deepseek.com/v1"
                )
                self.available_models.append("deepseek")
                print("DeepSeek client initialized.")
                self.logger.info("DeepSeek client initialized.")
            else:
                print("DeepSeek API key not found.")
                self.logger.error("DeepSeek API key not found.")

        # Initialize Mistral client
        if "mistral" in self.enabled_features:
            mistral_api_key = self.api_keys.get("mistral")
            if mistral_api_key:
                self.mistral_client = AsyncOpenAI(
                    api_key=mistral_api_key, base_url="https://api.mistral.ai/v1"
                )
                self.available_models.append("mistral")
                print("Mistral client initialized.")
                self.logger.info("Mistral client initialized.")
            else:
                print("Mistral API key not found.")
                self.logger.error("Mistral API key not found.")

        # Initialize Ollama client (for local models)
        if "ollama" in self.enabled_features:
            self.available_models.append("ollama")
            print("Ollama client initialized.")
            self.logger.info("Ollama client initialized.")

        # Initialize Llama client
        if "llama" in self.enabled_features:
            llama_api_key = self.api_keys.get("llama")
            if llama_api_key:
                self.available_models.append("llama")
                print("Llama client initialized.")
                self.logger.info("Llama client initialized.")
            else:
                print("Llama API key not found.")
                self.logger.error("Llama API key not found.")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_chatgpt(self, prompt: str) -> str:
        """Call OpenAI's ChatGPT API."""
        if not self.is_feature_enabled("openai"):
            return "Error: OpenAI feature not enabled"

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an intelligent assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            self.logger.info(f"Raw ChatGPT response: {response}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"ChatGPT API call failed: {e}")
            return str(e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_gemini(self, prompt: str) -> str:
        """Call Google's Gemini API."""
        if not self.is_feature_enabled("gemini"):
            return "Error: Gemini feature not enabled"

        try:
            response = await asyncio.to_thread(
                genai.generate_content,
                prompt=prompt,
                model="gemini-model",
                max_tokens=1500,
            )
            self.logger.info(f"Raw Gemini response: {response}")
            return response["text"].strip()
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            return str(e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_claude(self, prompt: str) -> str:
        """Call Anthropic's Claude model."""
        try:
            response = await self.anthropic_client.chat.completions.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error calling Claude: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_deepseek(self, prompt: str, model_type: str = "chat") -> str:
        """Call DeepSeek API with support for both chat and code models."""
        if not self.is_feature_enabled("deepseek"):
            return "Error: DeepSeek feature not enabled"

        try:
            # Select model based on type
            model = "deepseek-chat" if model_type == "chat" else "deepseek-coder"

            response = await self.deepseek_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an intelligent assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            self.logger.info(f"Raw DeepSeek response: {response}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"DeepSeek API call failed: {e}")
            return str(e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_mistral(self, prompt: str, model: str = "mistral-tiny") -> str:
        """Call Mistral API with support for different models."""
        if not self.is_feature_enabled("mistral"):
            return "Error: Mistral feature not enabled"

        try:
            response = await self.mistral_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an intelligent assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            self.logger.info(f"Raw Mistral response: {response}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Mistral API call failed: {e}")
            return str(e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_ollama(self, prompt: str, model: str = "mixtral") -> str:
        """Call Ollama API for local model inference."""
        if not self.is_feature_enabled("ollama"):
            return "Error: Ollama feature not enabled"

        try:
            response = await asyncio.to_thread(
                requests.post,
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 2000, "temperature": 0.7},
                },
            )
            response.raise_for_status()
            self.logger.info(f"Raw Ollama response: {response.json()}")
            return response.json().get("response", "").strip()
        except Exception as e:
            self.logger.error(f"Ollama API call failed: {e}")
            return str(e)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_llama(self, prompt: str) -> str:
        """Call Llama API."""
        if not self.is_feature_enabled("llama"):
            return "Error: Llama feature not enabled"

        try:
            api_url = "http://localhost:5000/generate"
            headers = {"Authorization": f"Bearer {self.api_keys.get('llama')}"}
            payload = {"prompt": prompt, "max_tokens": 1500}
            response = await asyncio.to_thread(
                requests.post, api_url, headers=headers, json=payload
            )
            response.raise_for_status()
            self.logger.info(f"Raw Llama response: {response.json()}")
            return response.json().get("text", "").strip()
        except Exception as e:
            self.logger.error(f"Llama API call failed: {e}")
            return str(e)

    async def test_apis(self):
        """Test all enabled API endpoints."""
        print("Testing APIs individually...\n")

        for model in self.available_models:
            print(f"Testing {model}...")
            try:
                if model == "openai":
                    response = await self.call_chatgpt("Test prompt for OpenAI.")
                elif model == "gemini":
                    response = await self.call_gemini("Test prompt for Gemini.")
                elif model == "anthropic":
                    response = await self.call_claude("Test prompt for Claude.")
                elif model == "deepseek":
                    response = await self.call_deepseek("Test prompt for DeepSeek.")
                elif model == "mistral":
                    response = await self.call_mistral("Test prompt for Mistral.")
                elif model == "ollama":
                    response = await self.call_ollama("Test prompt for Ollama.")
                elif model == "llama":
                    response = await self.call_llama("Test prompt for Llama.")

                if response and not response.startswith("Error:"):
                    print(f"{model} test successful!\n")
                else:
                    print(f"{model} test failed: {response}\n")
            except Exception as e:
                print(f"{model} test failed with error: {e}\n")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process_with_documents(
        self, prompt: str, file_paths: List[str]
    ) -> Dict[str, str]:
        """Process a prompt with document context."""
        try:
            # Process documents
            documents = self.documents.process_documents(file_paths)

            # Combine document content with prompt
            context = "\n\n".join(
                [
                    f"Document {i+1}:\n{content}"
                    for i, content in enumerate(documents.values())
                ]
            )
            enhanced_prompt = f"{prompt}\n\nContext from documents:\n{context}"

            # Process with available LLMs
            responses = {}
            for model in self.available_models:
                if model == "openai":
                    responses["chatgpt"] = await self.call_chatgpt(enhanced_prompt)
                elif model == "gemini":
                    responses["gemini"] = await self.call_gemini(enhanced_prompt)
                elif model == "anthropic":
                    responses["claude"] = await self.call_claude(enhanced_prompt)
                elif model == "deepseek":
                    responses["deepseek"] = await self.call_deepseek(enhanced_prompt)
                elif model == "mistral":
                    responses["mistral"] = await self.call_mistral(enhanced_prompt)
                elif model == "ollama":
                    responses["ollama"] = await self.call_ollama(enhanced_prompt)
                elif model == "llama":
                    responses["llama"] = await self.call_llama(enhanced_prompt)

            return responses

        except Exception as e:
            self.logger.error(f"Error processing documents: {str(e)}")
            raise
