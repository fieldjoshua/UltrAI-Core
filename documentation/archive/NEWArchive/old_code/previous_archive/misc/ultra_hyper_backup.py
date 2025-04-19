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

load_dotenv()  # This needs to be called before accessing any env vars

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
                 ultra_engine: str = "llama"):
        
        print("Initializing TriLLMOrchestrator...")
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Store the prompt first so we can use it for the directory name
        self.prompt = None
        self.base_dir = os.path.join(os.getcwd(), 'responses')
        
        print("\nChecking API keys...")
        self.api_keys = api_keys
        print(f"OpenAI: {api_keys.get('openai', '')[:5]}...{api_keys.get('openai', '')[-4:]}")
        print(f"Google: {api_keys.get('google', '')[:5]}...{api_keys.get('google', '')[-4:]}")
        
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

    def _get_keyword_from_prompt(self, prompt: str) -> str:
        """Extract a meaningful keyword from the prompt"""
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'please', 'edit', 'following'}
        
        words = prompt.lower().split()
        keyword = next((word for word in words if word not in common_words and len(word) > 2), 'task')
        
        keyword = ''.join(c for c in keyword if c.isalnum())
        return keyword[:15]

    def _initialize_clients(self):
        """Initialize API clients for each service"""
        print("Initializing Llama...")
        # Llama uses local API, no initialization needed
        print("Llama initialized successfully")
        
        print("Initializing OpenAI...")
        self.openai_client = OpenAI(api_key=self.api_keys["openai"])
        print("OpenAI initialized successfully")
        
        print("Initializing Gemini...")
        genai.configure(api_key=self.api_keys["google"])
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        print("Gemini initialized successfully")

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
        print("\nStarting get_initial_responses...")
        try:
            print("Creating tasks...")
            tasks = []
            
            print("Adding Llama task...")
            tasks.append(self.get_llama_response(prompt))
            
            print("Adding ChatGPT task...")
            tasks.append(self.get_chatgpt_response(prompt))
            
            print("Adding Gemini task...")
            tasks.append(self.get_gemini_response(prompt))
            
            print("Awaiting responses...")
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = {}
            
            if not isinstance(responses[0], Exception):
                results["llama"] = responses[0]
            else:
                results["llama"] = f"Error: {str(responses[0])}"
                
            if not isinstance(responses[1], Exception):
                results["chatgpt"] = responses[1]
            else:
                results["chatgpt"] = f"Error: {str(responses[1])}"
                
            if not isinstance(responses[2], Exception):
                results["gemini"] = responses[2]
            else:
                results["gemini"] = f"Error: {str(responses[2])}"
            
            return results
                
        except Exception as e:
            self.logger.error(f"Error getting initial responses: {str(e)}")
            print(f"Error in get_initial_responses: {str(e)}")
            raise

    async def get_meta_responses(self, initial_responses: Dict[str, str], 
                               original_prompt: str) -> Dict[str, str]:
        print("Getting meta responses...")
        try:
            meta_prompt = self._create_meta_prompt(initial_responses, original_prompt)
            
            tasks = [
                self.get_llama_response(meta_prompt),
                self.get_chatgpt_response(meta_prompt),
                self.get_gemini_response(meta_prompt)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = {}
            models = ['llama', 'chatgpt', 'gemini']
            
            for model, response in zip(models, responses):
                if not isinstance(response, Exception):
                    results[model] = response
                else:
                    results[model] = f"Error: {str(response)}"
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting meta responses: {str(e)}")
            raise

    async def get_ultra_response(self, meta_responses: Dict[str, str], 
                               original_prompt: str) -> str:
        try:
            ultra_prompt = self._create_ultra_prompt(meta_responses, original_prompt)
            
            if self.ultra_engine == 'llama':
                return await self.get_llama_response(ultra_prompt)
            elif self.ultra_engine == 'chatgpt':
                return await self.get_chatgpt_response(ultra_prompt)
            elif self.ultra_engine == 'gemini':
                return await self.get_gemini_response(ultra_prompt)
            else:
                raise ValueError(f"Invalid ultra engine: {self.ultra_engine}")
                
        except Exception as e:
            self.logger.error(f"Error getting ultra response: {str(e)}")
            raise

    async def get_hyper_response(self, ultra_response: str, meta_responses: Dict[str, str], 
                                initial_responses: Dict[str, str], original_prompt: str) -> str:
        """Generate a hyper-level analysis of all previous responses"""
        try:
            hyper_prompt = f"""Perform a hyper-level analysis of the following AI orchestration results. 
            This is a meta-meta analysis that should synthesize and elevate the insights from all previous levels.

Original Prompt:
{original_prompt}

Initial Responses Summary:
{json.dumps(initial_responses, indent=2)}

Meta Responses Summary:
{json.dumps(meta_responses, indent=2)}

Ultra Response:
{ultra_response}

Please provide:
1. Cross-analysis of how ideas evolved through each layer
2. Identification of emergent patterns and insights
3. Novel perspectives that only become visible at this hyper level
4. Synthesis of the most valuable elements from all previous analyses
5. Recommendations for further refinement

Your analysis should represent the highest level of synthetic thinking possible."""

            # Use all three models for hyper analysis
            hyper_responses = await asyncio.gather(
                self.get_llama_response(hyper_prompt),
                self.get_chatgpt_response(hyper_prompt),
                self.get_gemini_response(hyper_prompt)
            )
            
            # Save individual hyper responses
            for model, response in zip(['llama', 'chatgpt', 'gemini'], hyper_responses):
                self._save_response(response, f'hyper_{model}')
            
            # Create final hyper synthesis
            hyper_synthesis_prompt = f"""Create the final hyper synthesis from these three hyper-level analyses:

Llama Hyper Analysis:
{hyper_responses[0]}

ChatGPT Hyper Analysis:
{hyper_responses[1]}

Gemini Hyper Analysis:
{hyper_responses[2]}

Synthesize these into the ultimate hyper-level analysis."""

            # Use the chosen ultra engine for final hyper synthesis
            if self.ultra_engine == 'llama':
                final_hyper = await self.get_llama_response(hyper_synthesis_prompt)
            elif self.ultra_engine == 'chatgpt':
                final_hyper = await self.get_chatgpt_response(hyper_synthesis_prompt)
            else:
                final_hyper = await self.get_gemini_response(hyper_synthesis_prompt)
                
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

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        start_time = datetime.now()
        self.prompt = prompt
        self.keyword = self._get_keyword_from_prompt(prompt)
        
        # Create timestamped directory with keyword
        self.run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = os.path.join(self.base_dir, f"{self.keyword}_{self.run_timestamp}")
        self._setup_directory()
        
        # Start patent analysis in parallel
        patent_task = asyncio.create_task(self._analyze_self_for_patent())
        
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
            
            # Get and save ultra response
            ultra_response = await self.get_ultra_response(meta_responses, prompt)
            self._save_response(ultra_response, 'ultra')
            
            # Get and save hyper response
            hyper_response = await self.get_hyper_response(
                ultra_response, 
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
            
            return {
                "original_prompt": prompt,
                "initial_responses": initial_responses,
                "meta_responses": meta_responses,
                "ultra_response": ultra_response,
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

async def main():
    # Test environment variables first
    env_ok = await test_env()
    if not env_ok:
        return
        
    # Test APIs
    await test_apis()
    
    # Get user choice for ultra/hyper engine
    print("\nWhich engine should create the ultra/hyper responses?")
    print("1. Llama")
    print("2. ChatGPT")
    print("3. Gemini")
    while True:
        choice = input("Enter your choice (1-3): ")
        if choice in ['1', '2', '3']:
            engine = {
                '1': 'llama',
                '2': 'chatgpt',
                '3': 'gemini'
            }[choice]
            break
        print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Initialize the orchestrator with chosen engine
    orchestrator = TriLLMOrchestrator(
        api_keys={
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY")
        },
        ultra_engine=engine  # Use the chosen engine
    )
    
    # Get user input for prompt
    print("\nEnter your prompt (press Enter twice when finished):")
    prompt_lines = []
    while True:
        line = input()
        if line == "":
            break
        prompt_lines.append(line)
    user_prompt = "\n".join(prompt_lines)
    
    print(f"\nProcessing with {engine.upper()} as the ultra/hyper engine...")
    results = await orchestrator.orchestrate_full_process(user_prompt)
    
    print("\nAll responses have been saved to:", orchestrator.run_dir)

if __name__ == "__main__":
    asyncio.run(main())
