import os
import json
import asyncio
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from openai import OpenAI

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dataclasses import dataclass
from dotenv import load_dotenv
import torch
import platform
import psutil
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()  # This needs to be called before accessing any env vars

# Create FastAPI app
app = FastAPI(
    title="Ultra Hyper API",
    description="API for orchestrating multiple AI models",
    version="1.0.0",
    docs_url="/",  # This makes the Swagger UI appear at the root URL
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class AnalyzeRequest(BaseModel):
    prompt: str
    engine: str
    selectedEngines: list[str]
    options: dict = {
        "keepDataPrivate": False,
        "useNoTraceEncryption": False
    }

@dataclass
class PromptTemplate:
    initial: str = "Please analyze the following: {prompt}"
    refinement: str = (
        "Here are the initial responses from other models:\n{other_responses}\n"
        "Please review and refine your previous response based on this information. "
        "Do not assume that these responses are accurate. Provide any updates or corrections you deem necessary."
    )
    synthesis: str = "Create a final synthesis of these refined analyses: {refined_responses}"

class TriLLMOrchestrator:
    def __init__(self, api_keys: Dict[str, str], ultra_engine: str):
        self.api_keys = api_keys
        self.ultra_engine = ultra_engine
        self.run_dir = self.setup_run_directory()
        self.logger = self.setup_logging()
        self.prompt_template = PromptTemplate()
        self.validate_api_keys()  # Validate API keys during initialization
        # Initialize any other necessary components

    def setup_run_directory(self) -> str:
        """Sets up a directory to store run outputs."""
        run_dir = os.path.join("runs", datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(run_dir, exist_ok=True)
        return run_dir

    def setup_logging(self) -> logging.Logger:
        """Configures logging for the orchestrator."""
        logger = logging.getLogger("TriLLMOrchestrator")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(os.path.join(self.run_dir, "orchestrator.log"))
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def validate_api_keys(self):
        """Validate API keys and check connectivity."""
        try:
            # Check OpenAI API key
            # Use a simple chat completion to check key validity
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "This is a test."}])
            self.logger.info("OpenAI API key is valid.")
        except Exception as e:
            self.logger.error(f"OpenAI API key validation failed: {e}")
            raise

        try:
            # Check Google Generative AI API key
            genai.configure(api_key=self.api_keys.get("google"))
            model = genai.GenerativeModel('gemini-pro')
            model.generate_content("Test")  # Simple call to check key validity
            self.logger.info("Google Generative AI API key is valid.")
        except Exception as e:
            self.logger.error(f"Google Generative AI API key validation failed: {e}")
            raise

        try:
            # Check Llama API (assuming a simple health check endpoint)
            response = requests.get('http://localhost:11434/api/health')
            if response.status_code == 200:
                self.logger.info("Llama API is accessible.")
            else:
                self.logger.error("Llama API health check failed.")
                raise Exception("Llama API health check failed.")
        except Exception as e:
            self.logger.error(f"Llama API validation failed: {e}")
            raise

    def chunk_input(self, input_text: str, max_chunk_size: int = 1000) -> list:
        """Splits the input text into smaller chunks."""
        return [input_text[i:i + max_chunk_size] for i in range(0, len(input_text), max_chunk_size)]

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        # Split the prompt into chunks
        chunks = self.chunk_input(prompt)
        all_results = {
            "initial": {},
            "refined": {},
            "synthesis": {},
            "aggregated_initial": "",
            "aggregated_refined": "",
            "run_dir": self.run_dir
        }

        for idx, chunk in enumerate(chunks):
            self.logger.info(f"Processing chunk {idx + 1}/{len(chunks)}")

            # Step 1: Initial Generation
            self.logger.info("Starting initial generation phase.")
            initial_tasks = {
                "chatgpt": asyncio.create_task(self.call_chatgpt(self.prompt_template.initial.format(prompt=chunk))),
                "gemini": asyncio.create_task(self.call_gemini(self.prompt_template.initial.format(prompt=chunk))),
                "llama": asyncio.create_task(self.call_llama(self.prompt_template.initial.format(prompt=chunk))),
            }
            initial_responses = await asyncio.gather(*initial_tasks.values(), return_exceptions=True)
            initial_results = dict(zip(initial_tasks.keys(), initial_responses))
            self.logger.info(f"Initial responses for chunk {idx + 1}: {initial_results}")

            # Handle Exceptions in Initial Responses
            for model, response in initial_results.items():
                if isinstance(response, Exception):
                    self.logger.error(f"Error in initial response from {model}: {response}")
                    initial_results[model] = f"Error: {str(response)}"

            # Aggregate initial responses for refinement
            aggregated_initial = "\n".join([f"{model.capitalize()}: {resp}" for model, resp in initial_results.items()])

            # Step 2: Dynamic Refinement
            self.logger.info("Starting refinement phase.")
            refinement_tasks = {}
            for model in initial_tasks.keys():
                other_responses = "\n".join(
                    [f"{m.capitalize()}: {r}" for m, r in initial_results.items() if m != model]
                )
                instruction = self.prompt_template.refinement.format(other_responses=other_responses)
                if model == "chatgpt":
                    refinement_tasks[model] = asyncio.create_task(self.call_chatgpt(instruction))
                elif model == "gemini":
                    refinement_tasks[model] = asyncio.create_task(self.call_gemini(instruction))
                elif model == "llama":
                    refinement_tasks[model] = asyncio.create_task(self.call_llama(instruction))

            refined_responses = await asyncio.gather(*refinement_tasks.values(), return_exceptions=True)
            refined_results = dict(zip(refinement_tasks.keys(), refined_responses))
            self.logger.info(f"Refined responses for chunk {idx + 1}: {refined_results}")

            # Handle Exceptions in Refined Responses
            for model, response in refined_results.items():
                if isinstance(response, Exception):
                    self.logger.error(f"Error in refined response from {model}: {response}")
                    refined_results[model] = f"Error: {str(response)}"

            # Aggregate refined responses for synthesis
            aggregated_refined = "\n".join([f"{model.capitalize()}: {resp}" for model, resp in refined_results.items()])

            # Step 3: Optional Final Synthesis
            self.logger.info("Starting synthesis phase.")
            synthesis_tasks = {
                "chatgpt": asyncio.create_task(self.call_chatgpt(self.prompt_template.synthesis.format(refined_responses=aggregated_refined))),
                "gemini": asyncio.create_task(self.call_gemini(self.prompt_template.synthesis.format(refined_responses=aggregated_refined))),
                "llama": asyncio.create_task(self.call_llama(self.prompt_template.synthesis.format(refined_responses=aggregated_refined))),
            }
            synthesis_responses = await asyncio.gather(*synthesis_tasks.values(), return_exceptions=True)
            synthesis_results = dict(zip(synthesis_tasks.keys(), synthesis_responses))
            self.logger.info(f"Synthesis responses for chunk {idx + 1}: {synthesis_results}")

            # Handle Exceptions in Synthesis Responses
            for model, response in synthesis_results.items():
                if isinstance(response, Exception):
                    self.logger.error(f"Error in synthesis response from {model}: {response}")
                    synthesis_results[model] = f"Error: {str(response)}"

            # Aggregate all results for this chunk
            all_results["initial"].update(initial_results)
            all_results["refined"].update(refined_results)
            all_results["synthesis"].update(synthesis_results)
            all_results["aggregated_initial"] += aggregated_initial + "\n"
            all_results["aggregated_refined"] += aggregated_refined + "\n"

        return all_results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_chatgpt(self, instruction: str) -> str:
        """Calls the ChatGPT API with the given instruction."""
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": instruction}])
            text = response.choices[0].message.content.strip()
            return text
        except Exception as e:
            self.logger.error(f"ChatGPT API call failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_gemini(self, instruction: str) -> str:
        """Calls the Gemini API with the given instruction."""
        try:
            genai.configure(api_key=self.api_keys.get("google"))
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(instruction)
            return response.strip()
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def call_llama(self, instruction: str) -> str:
        """Calls the Llama API with the given instruction."""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',
                    'prompt': instruction,
                    'stream': False
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('response', '').strip()
        except Exception as e:
            self.logger.error(f"Llama API call failed: {e}")
            raise

@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        orchestrator = TriLLMOrchestrator(
            api_keys={
                "openai": os.getenv("OPENAI_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY"),
                "llama": os.getenv("LLAMA_API_KEY")  # Ensure this key is set
            },
            ultra_engine=request.engine
        )

        results = await orchestrator.orchestrate_full_process(request.prompt)

        return {
            "status": "success",
            "data": results,
            "output_directory": orchestrator.run_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ... (additional existing code, functions, and classes) ...
# For example, health check endpoints, utility functions, etc.

# Example of running the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
