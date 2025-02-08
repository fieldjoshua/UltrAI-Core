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

# Create API endpoint
@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        # Initialize the orchestrator
        orchestrator = TriLLMOrchestrator(
            api_keys={
                "openai": os.getenv("OPENAI_API_KEY"),
                "google": os.getenv("GOOGLE_API_KEY")
            },
            ultra_engine=request.engine
        )
        
        # Process the prompt
        results = await orchestrator.orchestrate_full_process(request.prompt)
        
        return {
            "status": "success",
            "data": results,
            "output_directory": orchestrator.run_dir
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@dataclass
class PromptTemplate:
    initial: str = "Please analyze the following: {prompt}"
    meta: str = "Analyze these responses and create an improved version: {responses}"
    ultra: str = "Create a final synthesis of these analyses: {responses}"
    hyper: str = "Perform a hyper-level analysis of all previous responses: {responses}"

@dataclass
class RateLimits:
    llama: int = 5
    chatgpt: int = 3
    gemini: int = 10

class TriLLMOrchestrator:
    def __init__(self, 
                 api_keys: Dict[str, str],
                 prompt_templates: Optional[PromptTemplate] = None,
                 rate_limits: Optional[RateLimits] = None,
                 output_format: str = "plain",
                 ultra_engine: str = "chatgpt"):
        
        print("Initializing TriLLMOrchestrator...")
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Store available models
        self.available_models = []
        
        print("\nChecking API keys and services...")
        self.api_keys = api_keys
        
        # Initialize clients and track which are available
        self._initialize_clients()
        
        self.prompt_templates = prompt_templates or PromptTemplate()
        self.rate_limits = rate_limits or RateLimits()
        self.last_request_time = {"llama": 0, "chatgpt": 0, "gemini": 0}
        self.ultra_engine = ultra_engine
        
        # Set output format
        self.output_format = output_format
        
        # Add hardware detection
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.max_threads = psutil.cpu_count(logical=False)  # Physical cores only
        self.executor = ThreadPoolExecutor(max_workers=self.max_threads)
        
        # Configure Metal backend
        if self.device == "mps":
            torch.backends.mps.enable_fallback_to_cpu = True
            
        # Print hardware configuration
        print("\nHardware Configuration:")
        print(f"Device: {self.device}")
        print(f"Processor: {platform.processor()}")
        print(f"Physical Cores: {self.max_threads}")
        print(f"Memory Available: {psutil.virtual_memory().available / (1024 * 1024 * 1024):.2f} GB")
        if self.device == "mps":
            print("Apple Silicon GPU acceleration enabled")
            print("GPU Cores: 30")
            print("Metal backend: Active")

    def _get_keyword_from_prompt(self, prompt: str) -> str:
        """Extract a meaningful keyword from the prompt"""
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'please', 'edit', 'following'}
        
        words = prompt.lower().split()
        keyword = next((word for word in words if word not in common_words and len(word) > 2), 'task')
        
        keyword = ''.join(c for c in keyword if c.isalnum())
        return keyword[:15]

    def _initialize_clients(self):
        """Initialize API clients for each service"""
        # Try Llama
        print("Checking Llama availability...")
        try:
            response = requests.get('http://localhost:11434/api/version', timeout=2)
            if response.status_code == 200:
                print("✓ Llama available")
                self.available_models.append('llama')
            else:
                print("✗ Llama not available (status code error)")
        except Exception as e:
            print(f"✗ Llama not available ({str(e)})")

        # Initialize OpenAI
        print("Initializing OpenAI...")
        try:
            self.openai_client = OpenAI(api_key=self.api_keys["openai"])
            self.available_models.append('chatgpt')
            print("✓ OpenAI initialized successfully")
        except Exception as e:
            print(f"✗ OpenAI initialization failed: {str(e)}")

        # Initialize Gemini
        print("Initializing Gemini...")
        try:
            genai.configure(api_key=self.api_keys["google"])
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            self.available_models.append('gemini')
            print("✓ Gemini initialized successfully")
        except Exception as e:
            print(f"✗ Gemini initialization failed: {str(e)}")
            
        if not self.available_models:
            raise Exception("No AI models available. Please check your configuration.")
        
        print(f"\nAvailable models: {', '.join(self.available_models)}")

    def _setup_directory(self):
        """Create directory for this run"""
        os.makedirs(self.run_dir, exist_ok=True)

    def formatter(self, text: str) -> str:
        """Format the output based on specified format"""
        if self.output_format == "plain":
            return text
        # Add more format options as needed
        return text

    async def _respect_rate_limit(self, service: str):
        """Ensure we don't exceed rate limits"""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time[service]
        
        if time_since_last < self.rate_limits.__dict__[service]:
            await asyncio.sleep(self.rate_limits.__dict__[service] - time_since_last)
        
        self.last_request_time[service] = current_time

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_llama_response(self, prompt: str) -> str:
        await self._respect_rate_limit("llama")
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',
                    'prompt': prompt,
                    'stream': False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return self.formatter(result['response'])
            else:
                raise Exception(f"Llama HTTP error: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error with Llama API: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_chatgpt_response(self, prompt: str) -> str:
        await self._respect_rate_limit("chatgpt")
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}]
            )
            return self.formatter(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"Error with ChatGPT API: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_gemini_response(self, prompt: str) -> str:
        await self._respect_rate_limit("gemini")
        try:
            response = self.gemini_model.generate_content(prompt)
            if hasattr(response, 'text'):
                return self.formatter(response.text)
            elif hasattr(response, 'parts'):
                return self.formatter(response.parts[0].text)
            else:
                raise Exception("Unexpected Gemini response format")
        except Exception as e:
            self.logger.error(f"Error with Gemini API: {str(e)}")
            raise

    def _create_meta_prompt(self, responses: Dict[str, str], original_prompt: str) -> str:
        return self.prompt_templates.meta.format(
            responses=json.dumps(responses, indent=2),
            original_prompt=original_prompt
        )

    def _create_ultra_prompt(self, responses: Dict[str, str], original_prompt: str) -> str:
        return self.prompt_templates.ultra.format(
            responses=json.dumps(responses, indent=2),
            original_prompt=original_prompt
        )

    async def get_initial_responses(self, prompt: str) -> Dict[str, str]:
        print("\nGetting initial responses...")
        results = {}
        
        tasks = []
        if 'llama' in self.available_models:
            tasks.append(('llama', self.get_llama_response(prompt)))
        if 'chatgpt' in self.available_models:
            tasks.append(('chatgpt', self.get_chatgpt_response(prompt)))
        if 'gemini' in self.available_models:
            tasks.append(('gemini', self.get_gemini_response(prompt)))
        
        for model, task in tasks:
            try:
                response = await task
                results[model] = response
                print(f"✓ Got response from {model}")
            except Exception as e:
                print(f"✗ Error getting {model} response: {str(e)}")
                results[model] = f"Error: {str(e)}"
        
        return results

    async def get_meta_responses(self, initial_responses: Dict[str, str], original_prompt: str) -> Dict[str, str]:
        print("Getting meta responses...")
        results = {}
        
        tasks = []
        if 'llama' in self.available_models:
            tasks.append(('llama', self.get_llama_response(self._create_meta_prompt(initial_responses, original_prompt))))
        if 'chatgpt' in self.available_models:
            tasks.append(('chatgpt', self.get_chatgpt_response(self._create_meta_prompt(initial_responses, original_prompt))))
        if 'gemini' in self.available_models:
            tasks.append(('gemini', self.get_gemini_response(self._create_meta_prompt(initial_responses, original_prompt))))
        
        for model, task in tasks:
            try:
                response = await task
                results[model] = response
                print(f"✓ Got meta response from {model}")
            except Exception as e:
                print(f"✗ Error getting meta response from {model}: {str(e)}")
                results[model] = f"Error: {str(e)}"
        
        return results

    async def get_ultra_responses(self, meta_responses: Dict[str, str], original_prompt: str) -> Dict[str, str]:
        print("Getting ultra responses...")
        results = {}
        
        tasks = []
        if 'llama' in self.available_models:
            tasks.append(('llama', self.get_llama_response(self._create_ultra_prompt(meta_responses, original_prompt))))
        if 'chatgpt' in self.available_models:
            tasks.append(('chatgpt', self.get_chatgpt_response(self._create_ultra_prompt(meta_responses, original_prompt))))
        if 'gemini' in self.available_models:
            tasks.append(('gemini', self.get_gemini_response(self._create_ultra_prompt(meta_responses, original_prompt))))
        
        for model, task in tasks:
            try:
                response = await task
                results[model] = response
                print(f"✓ Got ultra response from {model}")
            except Exception as e:
                print(f"✗ Error getting ultra response from {model}: {str(e)}")
                results[model] = f"Error: {str(e)}"
        
        return results

    async def get_hyper_response(self, ultra_responses: Dict[str, str], 
                                meta_responses: Dict[str, str], 
                                initial_responses: Dict[str, str], 
                                original_prompt: str) -> str:
        """Generate final hyper synthesis using chosen engine"""
        try:
            hyper_prompt = f"""Perform a hyper-level synthesis of all previous responses including multiple ultra perspectives.

Original Prompt:
{original_prompt}

Initial Responses:
{json.dumps(initial_responses, indent=2)}

Meta Responses:
{json.dumps(meta_responses, indent=2)}

Ultra Responses from Each Engine:
{json.dumps(ultra_responses, indent=2)}

Create the ultimate synthesis that:
1. Incorporates unique insights from each model at each level
2. Identifies patterns across all processing layers
3. Synthesizes the most valuable elements
4. Provides novel perspectives visible only at this hyper level
"""

            # Use chosen engine for final hyper synthesis
            if self.ultra_engine == 'llama':
                final_hyper = await self.get_llama_response(hyper_prompt)
            elif self.ultra_engine == 'chatgpt':
                final_hyper = await self.get_chatgpt_response(hyper_prompt)
            else:
                final_hyper = await self.get_gemini_response(hyper_prompt)
                
            self._save_response(final_hyper, 'hyper_final')
            return final_hyper
            
        except Exception as e:
            self.logger.error(f"Error getting hyper response: {str(e)}")
            raise

    async def _analyze_self_for_patent(self):
        """Analyze Ultra's code for patent application purposes"""
        try:
            # Get Ultra's own code
            with open(__file__, 'r') as f:
                code = f.read()
            
            patent_analysis_prompt = f"""Evaluate the functionality of the following code and prepare a description that is appropriate for a provisional patent application. Include both the technical description and the original code.

Focus on:
1. Novel technical aspects of the orchestration system
2. The unique interaction between multiple AI models
3. The workflow and processing methodology
4. Technical implementation details
5. Specific claims about the system's functionality

Then include the complete code as reference.

Code to analyze:

{code}

Please format the response in standard patent application style, including:
- Technical Field
- Background
- Summary of the Invention
- Detailed Description
- Claims
- Code Implementation
"""
            
            # Get analysis from each model
            responses = await asyncio.gather(
                self.get_llama_response(patent_analysis_prompt),
                self.get_chatgpt_response(patent_analysis_prompt),
                self.get_gemini_response(patent_analysis_prompt)
            )
            
            # Save patent analyses
            for model, response in zip(['llama', 'chatgpt', 'gemini'], responses):
                self._save_response(response, f'patent_analysis_{model}')
                
        except Exception as e:
            self.logger.error(f"Patent analysis error (non-critical): {str(e)}")

    def _save_response(self, response: str, filename: str):
        """Save a response to a file in the run directory"""
        filepath = os.path.join(self.run_dir, f'{self.keyword}_{filename}.txt')
        with open(filepath, 'w') as f:
            f.write(response)

    async def _monitor_performance(self):
        """Monitor system performance during processing"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            performance_data = {
                "cpu_usage": cpu_percent,
                "memory_used": f"{memory.percent}%",
                "memory_available": f"{memory.available / (1024 * 1024 * 1024):.2f} GB"
            }
            
            self._save_response(json.dumps(performance_data, indent=2), 'performance')
            
        except Exception as e:
            self.logger.error(f"Performance monitoring error: {str(e)}")

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        start_time = datetime.now()
        self.prompt = prompt
        self.keyword = self._get_keyword_from_prompt(prompt)
        
        # Create timestamped directory with keyword
        self.run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = os.path.join(os.getcwd(), 'responses', f"{self.keyword}_{self.run_timestamp}")
        self._setup_directory()
        
        # Start patent analysis in parallel
        patent_task = asyncio.create_task(self._analyze_self_for_patent())
        
        # Add performance monitoring
        monitor_task = asyncio.create_task(self._monitor_performance())
        
        try:
            # Save the original prompt
            self._save_response(prompt, 'prompt')
            
            # Get and save initial responses
            initial_responses = await self.get_initial_responses(prompt)
            for model, response in initial_responses.items():
                self._save_response(response, f'initial_{model}')
            
            # Get and save meta responses
            meta_responses = await self.get_meta_responses(initial_responses, prompt)
            for model, response in meta_responses.items():
                self._save_response(response, f'meta_{model}')
            
            # Get and save ultra responses
            ultra_responses = await self.get_ultra_responses(meta_responses, prompt)
            for model, response in ultra_responses.items():
                self._save_response(response, f'ultra_{model}')
            
            # Get and save hyper response
            hyper_response = await self.get_hyper_response(
                ultra_responses, 
                meta_responses, 
                initial_responses, 
                prompt
            )
            self._save_response(hyper_response, 'hyper')
            
            # Save metadata
            metadata = {
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "prompt": prompt,
                "keyword": self.keyword,
                "success": True
            }
            self._save_response(json.dumps(metadata, indent=2), 'metadata')
            
            # Wait for patent analysis but don't let it block the main process
            try:
                await asyncio.wait_for(patent_task, timeout=60)
            except asyncio.TimeoutError:
                pass
            
            # Wait for monitoring to complete
            await asyncio.wait_for(monitor_task, timeout=5)
            
            return {
                "original_prompt": prompt,
                "initial_responses": initial_responses,
                "meta_responses": meta_responses,
                "ultra_responses": ultra_responses,
                "hyper_response": hyper_response,
                "metadata": metadata
            }
            
        except Exception as e:
            error_msg = f"Error during orchestration: {str(e)}"
            self.logger.error(error_msg)
            metadata = {
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "prompt": prompt,
                "keyword": self.keyword,
                "success": False,
                "error": str(e)
            }
            self._save_response(json.dumps(metadata, indent=2), 'metadata')
            raise

async def test_env() -> bool:
    """Test environment variables"""
    print("Testing environment variables...")
    
    # Check OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    print(f"✓ OPENAI_API_KEY: {openai_key[:5]}...{openai_key[-4:]} (Length: {len(openai_key)})")
    
    # Check Google API key
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    print(f"✓ GOOGLE_API_KEY: {google_key[:5]}...{google_key[-4:]} (Length: {len(google_key)})")
    
    # Check Llama
    try:
        response = requests.get('http://localhost:11434/api/version')
        if response.status_code == 200:
            print("✓ Llama: Connected successfully")
        else:
            print("❌ Llama: Connection failed")
            return False
    except Exception as e:
        print(f"❌ Llama: Connection error - {str(e)}")
        return False
    
    print("\nAll services are available! ✓")
    return True

async def test_apis():
    """Test each API individually"""
    print("\nTesting APIs individually...")
    
    print("\nTesting Llama...")
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',
                'prompt': 'Say "Llama test successful!"',
                'stream': False
            }
        )
        if response.status_code == 200:
            print("Llama test successful!")
        else:
            print(f"Llama test failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Llama test failed with error: {str(e)}")
    
    print("\nTesting OpenAI...")
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Say 'OpenAI test successful!'"}]
        )
        print("OpenAI test successful!")
    except Exception as e:
        print(f"OpenAI test failed with error: {str(e)}")
    
    print("\nTesting Gemini...")
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Gemini test successful!'")
        print("Gemini test successful!")
    except Exception as e:
        print(f"Gemini test failed with error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
