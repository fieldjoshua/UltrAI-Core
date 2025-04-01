from typing import Dict, Any, Optional, List
import asyncio
import requests
import google.generativeai as genai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from ultra_base import UltraBase, PromptTemplate, RateLimits

class UltraLLM(UltraBase):
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None,
        ultra_engine: str = "chatgpt"
    ):
        super().__init__(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features
        )
        self.ultra_engine = ultra_engine
        self.available_models = []
    
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_chatgpt(self, prompt: str) -> str:
        """Call OpenAI's ChatGPT API."""
        if not self.is_feature_enabled("openai"):
            return "Error: OpenAI feature not enabled"
            
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an intelligent assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            self.logger.info(f"Raw ChatGPT response: {response}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"ChatGPT API call failed: {e}")
            return str(e)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_gemini(self, prompt: str) -> str:
        """Call Google's Gemini API."""
        if not self.is_feature_enabled("gemini"):
            return "Error: Gemini feature not enabled"
            
        try:
            response = await asyncio.to_thread(genai.generate_content, prompt=prompt, model="gemini-model", max_tokens=1500)
            self.logger.info(f"Raw Gemini response: {response}")
            return response['text'].strip()
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            return str(e)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def call_llama(self, prompt: str) -> str:
        """Call Llama API."""
        if not self.is_feature_enabled("llama"):
            return "Error: Llama feature not enabled"
            
        try:
            api_url = "http://localhost:5000/generate"
            headers = {"Authorization": f"Bearer {self.api_keys.get('llama')}"}
            payload = {"prompt": prompt, "max_tokens": 1500}
            response = await asyncio.to_thread(requests.post, api_url, headers=headers, json=payload)
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
                elif model == "llama":
                    response = await self.call_llama("Test prompt for Llama.")
                
                if response and not response.startswith("Error:"):
                    print(f"{model} test successful!\n")
                else:
                    print(f"{model} test failed: {response}\n")
            except Exception as e:
                print(f"{model} test failed with error: {e}\n") 