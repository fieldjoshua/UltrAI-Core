import asyncio
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import os
from dotenv import load_dotenv
from string import Template

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
import google.generativeai as genai
from google.generativeai import GenerativeModel

from ultra_analysis_patterns import AnalysisPatterns, AnalysisPattern

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatternOrchestrator:
    def __init__(self, 
                 api_keys: Dict[str, str],
                 pattern: str = "gut",
                 output_format: str = "plain"):
        """Initialize the pattern orchestrator"""
        self.pattern = AnalysisPatterns.get_pattern(pattern)
        if not self.pattern:
            raise ValueError(f"Unknown pattern: {pattern}")
            
        # Initialize API clients
        self.anthropic_key = api_keys["anthropic"]
        self.openai = AsyncOpenAI(api_key=api_keys["openai"])
        genai.configure(api_key=api_keys["google"])
        self.gemini = GenerativeModel('gemini-pro')
        
        # Setup output formatting
        self.formatter = getattr(ResponseFormatter, f"format_{output_format}")
        
        # Rate limiting state
        self._last_call = {"claude": 0, "chatgpt": 0, "gemini": 0}
        
        self.logger = logging.getLogger(__name__)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_claude_response(self, prompt: str) -> str:
        """Get response from Claude"""
        await self._respect_rate_limit("claude")
        try:
            async with AsyncAnthropic(api_key=self.anthropic_key) as client:
                message = await client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                return self.formatter(message.content[0].text)
        except Exception as e:
            self.logger.error(f"Error with Claude API: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_chatgpt_response(self, prompt: str) -> str:
        """Get response from ChatGPT"""
        await self._respect_rate_limit("chatgpt")
        try:
            response = await self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            return self.formatter(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"Error with ChatGPT API: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini"""
        await self._respect_rate_limit("gemini")
        try:
            response = await self.gemini.generate_content(prompt)
            return self.formatter(response.text)
        except Exception as e:
            self.logger.error(f"Error with Gemini API: {str(e)}")
            raise

    async def _respect_rate_limit(self, model: str):
        """Respect rate limits between API calls"""
        current_time = time.time()
        last_call = self._last_call.get(model, 0)
        wait_time = max(0, 1 - (current_time - last_call))
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self._last_call[model] = time.time()

    def _create_stage_prompt(self, stage: str, context: Dict[str, Any]) -> str:
        """Create a prompt for a specific analysis stage"""
        template = self.pattern.templates.get(stage)
        if not template:
            raise ValueError(f"Unknown stage: {stage}")
            
        return Template(template).safe_substitute(context)

    async def get_initial_responses(self, prompt: str) -> Dict[str, str]:
        """Get initial responses from all models"""
        responses = await asyncio.gather(
            self.get_claude_response(prompt),
            self.get_chatgpt_response(prompt),
            self.get_gemini_response(prompt)
        )
        return {
            "claude": responses[0],
            "chatgpt": responses[1],
            "gemini": responses[2]
        }

    async def get_meta_responses(self, initial_responses: Dict[str, str], 
                               original_prompt: str) -> Dict[str, str]:
        """Get meta-level responses from all models"""
        meta_responses = {}
        
        for model, response in initial_responses.items():
            # Create context for this model's meta analysis
            other_responses = {k: v for k, v in initial_responses.items() if k != model}
            context = {
                "original_prompt": original_prompt,
                "own_response": response,
                "other_responses": "\n\n".join(f"{k.upper()}:\n{v}" for k, v in other_responses.items())
            }
            
            # Get meta response using appropriate model
            if model == "claude":
                meta_responses[model] = await self.get_claude_response(
                    self._create_stage_prompt("meta", context)
                )
            elif model == "chatgpt":
                meta_responses[model] = await self.get_chatgpt_response(
                    self._create_stage_prompt("meta", context)
                )
            else:  # gemini
                meta_responses[model] = await self.get_gemini_response(
                    self._create_stage_prompt("meta", context)
                )
                
        return meta_responses

    async def get_hyper_responses(self, meta_responses: Dict[str, str],
                                initial_responses: Dict[str, str],
                                original_prompt: str) -> Dict[str, str]:
        """Get hyper-level responses from all models"""
        hyper_responses = {}
        
        for model, meta_response in meta_responses.items():
            # Create context for this model's hyper analysis
            context = {
                "original_prompt": original_prompt,
                "own_meta": meta_response,
                "other_meta_responses": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in meta_responses.items() if k != model
                ),
                "own_response": initial_responses[model],
                "critiques": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in meta_responses.items() if k != model
                ),
                "fact_checks": "\n\n".join(
                    f"{k.upper()}:\n{v}" for k, v in meta_responses.items() if k != model
                )
            }
            
            # Get hyper response using appropriate model
            if model == "claude":
                hyper_responses[model] = await self.get_claude_response(
                    self._create_stage_prompt("hyper", context)
                )
            elif model == "chatgpt":
                hyper_responses[model] = await self.get_chatgpt_response(
                    self._create_stage_prompt("hyper", context)
                )
            else:  # gemini
                hyper_responses[model] = await self.get_gemini_response(
                    self._create_stage_prompt("hyper", context)
                )
                
        return hyper_responses

    async def get_ultra_response(self, hyper_responses: Dict[str, str],
                               original_prompt: str) -> str:
        """Get final ultra-level synthesis"""
        context = {
            "original_prompt": original_prompt,
            "hyper_responses": "\n\n".join(
                f"{k.upper()}:\n{v}" for k, v in hyper_responses.items()
            )
        }
        
        # Use Claude for the final synthesis
        return await self.get_claude_response(
            self._create_stage_prompt("ultra", context)
        )

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        """Run the complete analysis process"""
        start_time = datetime.now()
        results = {}
        
        try:
            # 1. Get initial responses
            self.logger.info("Getting initial responses...")
            initial_responses = await self.get_initial_responses(prompt)
            results["initial_responses"] = initial_responses
            
            # 2. Get meta responses
            self.logger.info("Getting meta responses...")
            meta_responses = await self.get_meta_responses(initial_responses, prompt)
            results["meta_responses"] = meta_responses
            
            # 3. Get hyper responses
            self.logger.info("Getting hyper responses...")
            hyper_responses = await self.get_hyper_responses(
                meta_responses, initial_responses, prompt
            )
            results["hyper_responses"] = hyper_responses
            
            # 4. Get ultra synthesis
            self.logger.info("Getting ultra synthesis...")
            ultra_response = await self.get_ultra_response(hyper_responses, prompt)
            results["ultra_response"] = ultra_response
            
            # Add metadata
            results["metadata"] = {
                "pattern": self.pattern.name,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "prompt": prompt
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in orchestration process: {str(e)}")
            raise

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
        print("\nError: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease set these variables in your .env file")
        return False
    
    print("\nAll required environment variables are set")
    return True

async def main():
    # Test environment variables first
    env_ok = await test_env()
    if not env_ok:
        return
    
    print("\nInitializing Pattern Orchestrator...")
    
    # Get API keys from environment
    api_keys = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY")
    }
    
    # Get pattern choice from user
    print("\nAvailable analysis patterns:")
    print("1. Gut Analysis")
    print("2. Confidence Analysis")
    print("3. Critique Analysis")
    print("4. Fact Check Analysis")
    print("5. Perspective Analysis")
    print("6. Scenario Analysis")
    
    while True:
        choice = input("\nEnter your choice (1-6): ")
        if choice in ['1', '2', '3', '4', '5', '6']:
            pattern = {
                '1': 'gut',
                '2': 'confidence',
                '3': 'critique',
                '4': 'fact_check',
                '5': 'perspective',
                '6': 'scenario'
            }[choice]
            break
        print("Invalid choice. Please enter a number between 1 and 6.")
    
    # Initialize orchestrator
    orchestrator = PatternOrchestrator(
        api_keys=api_keys,
        pattern=pattern,
        output_format="markdown"
    )
    
    # Get prompt from user
    prompt = input("\nEnter your prompt (press Enter to use default): ").strip()
    if not prompt:
        prompt = "What are the most effective strategies for learning a new programming language?"
        print(f"\nUsing default prompt: {prompt}")
    
    print(f"\nStarting {orchestrator.pattern.name} process...")
    results = await orchestrator.orchestrate_full_process(prompt)
    
    # Save results
    filename = f"pattern_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main()) 