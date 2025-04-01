import os
import json
import asyncio
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from openai import AsyncOpenAI
from dataclasses import dataclass
from dotenv import load_dotenv
import torch
import platform

load_dotenv()  # This needs to be called before accessing any env vars

# Retrieve the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client with the API key
aclient = AsyncOpenAI(api_key=openai_api_key)

@dataclass
class PromptTemplate:
    initial: str = "Please provide a comprehensive analysis of the following: {prompt}"
    meta: str = (
        "Consider the following responses to your original prompt. "
        "DO NOT assume they are accurate or unbiased. "
        "Please revise your most initial draft to enhance its effectiveness and clarity."
    )
    ultra: str = (
        "Review the subsequent responses to the original prompt. "
        "DO NOT assume they are accurate or unbiased. "
        "Please revise your most recent draft to further improve its effectiveness."
    )
    hyper: str = (
        "Perform a hyper-level analysis of all previous responses: {responses}. "
        "In a professional and concise report, identify the relevant and insightful similarities and differences among them. "
        "Provide your advice on how the user should apply these analyses based on the original prompt."
    )

@dataclass
class RateLimits:
    llama: int = 5
    chatgpt: int = 3
    gemini: int = 10

class TriLLMOrchestrator:
    def __init__(
        self, 
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        ultra_engine: str = "llama"
    ):
        print("Initializing TriLLMOrchestrator...")

        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            filename='ultra_hyper.log',
            filemode='a',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        # Store the prompt first so we can use it for the directory name
        self.prompt = None
        self.base_dir = os.path.join(os.getcwd(), 'responses')
        os.makedirs(self.base_dir, exist_ok=True)

        print("\nChecking API keys...")
        self.api_keys = api_keys
        if not self.api_keys.get('llama'):
            self.logger.error("Llama API key not found.")
            print("Llama API key not found.")
        else:
            print(f"Llama: {self.api_keys.get('llama', '')[:5]}...{self.api_keys.get('llama', '')[-4:]}")

        if not self.api_keys.get('openai'):
            self.logger.error("OpenAI API key not found.")
            print("OpenAI API key not found.")
        else:
            print(f"OpenAI: {self.api_keys.get('openai', '')[:5]}...{self.api_keys.get('openai', '')[-4:]}")

        if not self.api_keys.get('google'):
            self.logger.error("Google API key not found.")
            print("Google API key not found.")
        else:
            print(f"Google: {self.api_keys.get('google', '')[:5]}...{self.api_keys.get('google', '')[-4:]}")

        print("\nSetting up formatter...")
        self.output_format = output_format

        print("\nInitializing API clients...")
        self._initialize_clients()

        self.prompt_templates = prompt_templates or PromptTemplate()
        self.rate_limits = rate_limits or RateLimits()
        self.last_request_time = {"llama": 0, "chatgpt": 0, "gemini": 0}
        self.ultra_engine = ultra_engine

        # Add hardware detection
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"\nHardware Configuration:")
        print(f"Device: {self.device}")
        print(f"Processor: {platform.processor()}")
        if self.device == "mps":
            print("Apple Silicon GPU acceleration enabled")
            print("GPU Cores: 30")
            # Enable Metal optimizations
            torch.backends.mps.enable_fallback_to_cpu = True

        self.run_dir = os.path.join(self.base_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.run_dir, exist_ok=True)

    def _initialize_clients(self):
        # Initialize OpenAI client
        openai_api_key = self.api_keys.get("openai")
        if openai_api_key:
            print("OpenAI client initialized.")
            self.logger.info("OpenAI client initialized.")
        else:
            print("OpenAI API key not found.")
            self.logger.error("OpenAI API key not found.")

        # Initialize Google Gemini client
        google_api_key = self.api_keys.get("google")
        if google_api_key:
            genai.configure(api_key=google_api_key)
            print("Google Gemini client initialized.")
            self.logger.info("Google Gemini client initialized.")
        else:
            print("Google API key not found.")
            self.logger.error("Google API key not found.")

        # Initialize Llama client (assuming it's a local service)
        llama_api_key = self.api_keys.get("llama")
        if llama_api_key:
            print("Llama client initialized.")
            self.logger.info("Llama client initialized.")
        else:
            print("Llama API key not found.")
            self.logger.error("Llama API key not found.")

    async def orchestrate_full_process(self, user_prompt: str) -> Dict[str, Any]:
        self.logger.info("Starting Orchestration Process")

        # Initial Round
        self.logger.info("Starting Initial Round")
        initial_responses = await self.initial_round(user_prompt)
        self.logger.info("Completed Initial Round")

        # Meta Round
        self.logger.info("Starting Meta Round")
        refined_responses = await self.meta_round(initial_responses)
        self.logger.info("Completed Meta Round")

        # Ultra Round
        self.logger.info("Starting Ultra Round")
        synthesized_response = await self.ultra_round(refined_responses)
        self.logger.info("Completed Ultra Round")

        # Hyper Round
        self.logger.info("Starting Hyper Round")
        hyper_analysis = await self.hyper_round(user_prompt, initial_responses, refined_responses, synthesized_response)
        self.logger.info("Completed Hyper Round")

        # Save responses
        self.logger.info("Saving Responses")
        self.save_responses(initial_responses, refined_responses, synthesized_response, hyper_analysis)
        self.logger.info("Responses Saved Successfully")

        return {
            "initial_responses": initial_responses,
            "refined_responses": refined_responses,
            "synthesized_response": synthesized_response,
            "hyper_analysis": hyper_analysis
        }

    def save_responses(self, initial, refined, synthesized, hyper):
        run_dir = self.run_dir
        os.makedirs(run_dir, exist_ok=True)

        with open(os.path.join(run_dir, "initial_responses.json"), "w") as f:
            json.dump(initial, f, indent=4)

        with open(os.path.join(run_dir, "refined_responses.json"), "w") as f:
            json.dump(refined, f, indent=4)

        with open(os.path.join(run_dir, "synthesized_response.json"), "w") as f:
            json.dump(synthesized, f, indent=4)

        with open(os.path.join(run_dir, "hyper_analysis.json"), "w") as f:
            json.dump(hyper, f, indent=4)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def initial_round(self, prompt: str) -> Dict[str, str]:
        initial_prompt = self.prompt_templates.initial.format(prompt=prompt)
        self.logger.info(f"Initial Prompt: {initial_prompt}")
        responses = await asyncio.gather(
            self.call_chatgpt(initial_prompt),
            self.call_gemini(initial_prompt),
            self.call_llama(initial_prompt),
            return_exceptions=True
        )
        result = {
            "chatgpt": responses[0] if not isinstance(responses[0], Exception) else f"Error: {responses[0]}",
            "gemini": responses[1] if not isinstance(responses[1], Exception) else f"Error: {responses[1]}",
            "llama": responses[2] if not isinstance(responses[2], Exception) else f"Error: {responses[2]}"
        }
        self.logger.info(f"Initial Responses: {result}")
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def meta_round(self, initial_responses: Dict[str, str]) -> Dict[str, str]:
        aggregated_responses = "\n\n".join([resp for resp in initial_responses.values()])
        meta_prompt = self.prompt_templates.meta
        refined_prompt = meta_prompt.format(prompt=aggregated_responses)
        self.logger.info(f"Meta Prompt: {refined_prompt}")
        responses = await asyncio.gather(
            self.call_chatgpt(refined_prompt),
            self.call_gemini(refined_prompt),
            self.call_llama(refined_prompt),
            return_exceptions=True
        )
        result = {
            "chatgpt": responses[0] if not isinstance(responses[0], Exception) else f"Error: {responses[0]}",
            "gemini": responses[1] if not isinstance(responses[1], Exception) else f"Error: {responses[1]}",
            "llama": responses[2] if not isinstance(responses[2], Exception) else f"Error: {responses[2]}"
        }
        self.logger.info(f"Refined Responses: {result}")
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def ultra_round(self, refined_responses: Dict[str, str]) -> Dict[str, str]:
        aggregated_refined = "\n\n".join([resp for resp in refined_responses.values()])
        ultra_prompt = self.prompt_templates.ultra.format(prompt=aggregated_refined)
        self.logger.info(f"Ultra Prompt: {ultra_prompt}")
        responses = await asyncio.gather(
            self.call_chatgpt(ultra_prompt),
            self.call_gemini(ultra_prompt),
            self.call_llama(ultra_prompt),
            return_exceptions=True
        )
        result = {
            "chatgpt": responses[0] if not isinstance(responses[0], Exception) else f"Error: {responses[0]}",
            "gemini": responses[1] if not isinstance(responses[1], Exception) else f"Error: {responses[1]}",
            "llama": responses[2] if not isinstance(responses[2], Exception) else f"Error: {responses[2]}"
        }
        self.logger.info(f"Synthesized Responses: {result}")
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def hyper_round(
        self, 
        user_prompt: str, 
        initial_responses: Dict[str, str],
        refined_responses: Dict[str, str], 
        synthesized_response: Dict[str, str]
    ) -> str:
        hyper_input = "\n\n".join([
            user_prompt,
            "\n\n".join(initial_responses.values()),
            "\n\n".join(refined_responses.values()),
            "\n\n".join(synthesized_response.values())
        ])
        hyper_prompt = self.prompt_templates.hyper.format(responses=hyper_input)
        self.logger.info(f"Hyper Prompt: {hyper_prompt}")
        hyper_response = await self.call_chatgpt(hyper_prompt)
        if isinstance(hyper_response, Exception):
            self.logger.error(f"Hyper Round Error: {hyper_response}")
            return f"Error: {hyper_response}"
        self.logger.info(f"Hyper-Level Analysis: {hyper_response}")
        return hyper_response

    async def call_chatgpt(self, prompt: str) -> str:
        try:
            response = await aclient.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an intelligent assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            # Log the raw response for debugging
            self.logger.info(f"Raw ChatGPT response: {response}")

            # Access the message content directly
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"ChatGPT API call failed: {e}")
            return str(e)

    async def call_gemini(self, prompt: str) -> str:
        try:
            # Ensure the correct method is used for generating content
            response = await asyncio.to_thread(genai.generate_content, prompt=prompt, model="gemini-model", max_tokens=1500)
            self.logger.info(f"Raw Gemini response: {response}")
            return response['text'].strip()
        except AttributeError as e:
            self.logger.error(f"Gemini API call failed: {e}")
            return "Error: Incorrect method or module usage"
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            return str(e)

    async def call_llama(self, prompt: str) -> str:
        try:
            api_url = "http://localhost:5000/generate"  # Ensure this endpoint is correct
            headers = {"Authorization": f"Bearer {self.api_keys.get('llama')}"}
            payload = {"prompt": prompt, "max_tokens": 1500}
            response = await asyncio.to_thread(requests.post, api_url, headers=headers, json=payload)
            response.raise_for_status()
            self.logger.info(f"Raw Llama response: {response.json()}")
            return response.json().get("text", "").strip()
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Llama API call failed with HTTP error: {e}")
            return f"HTTP Error: {e}"
        except Exception as e:
            self.logger.error(f"Llama API call failed: {e}")
            return str(e)

    async def test_apis(self):
        print("Testing APIs individually...\n")

        # Testing Llama
        print("Testing Llama...")
        try:
            response = await self.call_llama("Test prompt for Llama")
            if response and not response.startswith("Error:"):
                print("Llama test successful!\n")
            else:
                print(f"Llama test failed: {response}\n")
        except Exception as e:
            print(f"Llama test failed with error: {e}\n")

        # Testing OpenAI
        print("Testing OpenAI...")
        try:
            response = await self.call_chatgpt("Test prompt for OpenAI.")
            if response and not response.startswith("Error:"):
                print("OpenAI test successful!\n")
            else:
                print(f"OpenAI test failed: {response}\n")
        except Exception as e:
            print(f"OpenAI test failed with error: {e}\n")

        # Testing Gemini
        print("Testing Gemini...")
        try:
            response = await self.call_gemini("Test prompt for Gemini.")
            if response and not response.startswith("Error:"):
                print("Gemini test successful!\n")
            else:
                print(f"Gemini test failed: {response}\n")
        except Exception as e:
            print(f"Gemini test failed with error: {e}\n")

async def main():
    # Load API keys from environment variables
    api_keys = {
        'openai': os.getenv("OPENAI_API_KEY"),
        'google': os.getenv("GOOGLE_API_KEY"),
        'llama': os.getenv("LLAMA_API_KEY"),
    }

    orchestrator = TriLLMOrchestrator(api_keys=api_keys)

    # Test APIs
    await orchestrator.test_apis()

    # Get user input for prompt
    print("\nEnter your prompt (press Enter twice when finished):")
    prompt_lines = []
    while True:
        line = input()
        if line == "":
            break
        prompt_lines.append(line)
    user_prompt = "\n".join(prompt_lines)

    print("\nProcessing...")
    results = await orchestrator.orchestrate_full_process(user_prompt)

    print("\nFinal Hyper-Level Analysis:")
    print(results["hyper_analysis"])

if __name__ == "__main__":
    asyncio.run(main())
