import asyncio
from typing import Dict, Any, Optional, List
import json
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from string import Template
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import os
from dotenv import load_dotenv

# Updated imports for new Anthropic client
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
import google.generativeai as genai
from google.generativeai import GenerativeModel
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PromptTemplate:
    meta_round: str = """Original prompt: $original_prompt

Here are responses from three different LLMs to this prompt:

Claude's response:
$claude_response

ChatGPT's response:
$chatgpt_response

Gemini's response:
$gemini_response

Please provide an improved response that:
1. $meta_instruction_1
2. $meta_instruction_2
3. $meta_instruction_3
4. $meta_instruction_4
5. $meta_instruction_5"""

    ultra_round: str = """Original prompt: $original_prompt

Here are the meta-responses where each LLM improved upon the initial responses:

Claude's meta-response:
$claude_meta

ChatGPT's meta-response:
$chatgpt_meta

Gemini's meta-response:
$gemini_meta

Please synthesize these meta-responses into a single optimal response that:
1. $ultra_instruction_1
2. $ultra_instruction_2
3. $ultra_instruction_3
4. $ultra_instruction_4"""

    meta_instructions: List[str] = None
    ultra_instructions: List[str] = None

    def __post_init__(self):
        if self.meta_instructions is None:
            self.meta_instructions = [
                "Incorporates the unique insights from each response",
                "Addresses any limitations or gaps in the individual responses",
                "Resolves any contradictions between the responses",
                "Maintains accuracy while being more comprehensive",
                "Is clearly structured and well-organized"
            ]
        if self.ultra_instructions is None:
            self.ultra_instructions = [
                "Captures the most valuable insights from all meta-responses",
                "Eliminates redundancy and reconciles any remaining contradictions",
                "Presents the information in the most effective and coherent way",
                "Represents the best possible answer to the original prompt"
            ]

@dataclass
class RateLimits:
    claude_rpm: int = 50
    chatgpt_rpm: int = 200
    gemini_rpm: int = 60

class ResponseFormatter:
    @staticmethod
    def format_markdown(response: str) -> str:
        return f"```markdown\n{response}\n```"
    
    @staticmethod
    def format_json(response: str) -> str:
        return json.dumps({"response": response}, indent=2)
    
    @staticmethod
    def format_plain(response: str) -> str:
        return response

class TriLLMOrchestrator:
    def __init__(self, 
                 api_keys: Dict[str, str],
                 prompt_templates: Optional[PromptTemplate] = None,
                 rate_limits: Optional[RateLimits] = None,
                 output_format: str = "plain"):
        
        # Initialize API clients - note the change here
        self.anthropic_key = api_keys["anthropic"]  # Store key for async client
        self.openai = AsyncOpenAI(api_key=api_keys["openai"])
        genai.configure(api_key=api_keys["google"])
        self.gemini = GenerativeModel('gemini-pro')
        
        # Configuration
        self.templates = prompt_templates or PromptTemplate()
        self.rate_limits = rate_limits or RateLimits()
        self.formatter = getattr(ResponseFormatter, f"format_{output_format}")
        
        # Rate limiting state
        self._last_call = {"claude": 0, "chatgpt": 0, "gemini": 0}
        
        self.logger = logging.getLogger(__name__)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_claude_response(self, prompt: str) -> str:
        """New version using AsyncAnthropic client"""
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
        await self._respect_rate_limit("chatgpt")
        try:
            response = await self.openai.chat.completions.create(
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
            response = await self.gemini.generate_content_async(prompt)
            return self.formatter(response.text)
        except Exception as e:
            self.logger.error(f"Error with Gemini API: {str(e)}")
            raise

    async def get_initial_responses(self, prompt: str) -> Dict[str, str]:
        try:
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
        except Exception as e:
            self.logger.error(f"Error getting initial responses: {str(e)}")
            raise

    def _create_meta_prompt(self, responses: Dict[str, str], original_prompt: str) -> str:
        template_vars = {
            "original_prompt": original_prompt,
            "claude_response": responses["claude"],
            "chatgpt_response": responses["chatgpt"],
            "gemini_response": responses["gemini"]
        }
        
        for i, instruction in enumerate(self.templates.meta_instructions, 1):
            template_vars[f"meta_instruction_{i}"] = instruction
            
        return Template(self.templates.meta_round).safe_substitute(template_vars)

    def _create_ultra_prompt(self, meta_responses: Dict[str, str], original_prompt: str) -> str:
        template_vars = {
            "original_prompt": original_prompt,
            "claude_meta": meta_responses["claude"],
            "chatgpt_meta": meta_responses["chatgpt"],
            "gemini_meta": meta_responses["gemini"]
        }
        
        for i, instruction in enumerate(self.templates.ultra_instructions, 1):
            template_vars[f"ultra_instruction_{i}"] = instruction
            
        return Template(self.templates.ultra_round).safe_substitute(template_vars)

    async def get_meta_responses(self, initial_responses: Dict[str, str], 
                               original_prompt: str) -> Dict[str, str]:
        try:
            meta_prompt = self._create_meta_prompt(initial_responses, original_prompt)
            
            responses = await asyncio.gather(
                self.get_claude_response(meta_prompt),
                self.get_chatgpt_response(meta_prompt),
                self.get_gemini_response(meta_prompt)
            )
            return {
                "claude": responses[0],
                "chatgpt": responses[1],
                "gemini": responses[2]
            }
        except Exception as e:
            self.logger.error(f"Error getting meta responses: {str(e)}")
            raise

    async def get_ultra_response(self, meta_responses: Dict[str, str], 
                               original_prompt: str) -> str:
        try:
            ultra_prompt = self._create_ultra_prompt(meta_responses, original_prompt)
            return await self.get_claude_response(ultra_prompt)
        except Exception as e:
            self.logger.error(f"Error getting ultra response: {str(e)}")
            raise

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        start_time = datetime.now()
        results = {
            "original_prompt": prompt,
            "initial_responses": None,
            "meta_responses": None,
            "ultra_response": None,
            "metadata": {
                "start_time": start_time.isoformat(),
                "end_time": None,
                "success": False,
                "errors": []
            }
        }
        
        try:
            print("\nGetting initial responses...")
            results["initial_responses"] = await self.get_initial_responses(prompt)
            
            print("Getting meta responses...")
            results["meta_responses"] = await self.get_meta_responses(
                results["initial_responses"],
                prompt
            )
            
            print("Getting ultra response...")
            results["ultra_response"] = await self.get_ultra_response(
                results["meta_responses"],
                prompt
            )
            
            results["metadata"]["success"] = True
            
        except Exception as e:
            error_msg = f"Error during orchestration: {str(e)}"
            self.logger.error(error_msg)
            results["metadata"]["errors"].append(error_msg)
            
        finally:
            results["metadata"]["end_time"] = datetime.now().isoformat()
            results["metadata"]["duration_seconds"] = (
                datetime.fromisoformat(results["metadata"]["end_time"]) - 
                datetime.fromisoformat(results["metadata"]["start_time"])
            ).total_seconds()
            
        return results

async def test_env():
    print("\nTesting environment variables...")
    
    # Load the .env file
    load_dotenv()
    
    # Debug: Print the .env file location and contents
    env_path = os.path.join(os.getcwd(), '.env')
    print(f"\nLooking for .env file at: {env_path}")
    try:
        with open('.env', 'r') as f:
            print("\nActual .env contents:")
            for line in f:
                key, value = line.strip().split('=')
                print(f"{key}={value[:4]}...{value[-4:]}")
    except Exception as e:
        print(f"Error reading .env file: {e}")
    
    # Check each API key
    keys = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
    }
    
    all_good = True
    for name, value in keys.items():
        if value:
            print(f"✓ {name}: {value[:4]}...{value[-4:]} (Length: {len(value)})")
        else:
            print(f"✗ {name}: NOT FOUND")
            all_good = False
    
    if all_good:
        print("\nAll environment variables are set! ✓")
    else:
        print("\nSome environment variables are missing! ✗")
        print("Please check your .env file and ensure all keys are set.")
    
    return all_good

async def main():
    # Test environment variables first
    env_ok = await test_env()
    if not env_ok:
        return
    
    print("\nInitializing LLM Orchestrator...")
    
    # Get API keys from environment
    api_keys = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY")
    }
    
    # Initialize orchestrator
    orchestrator = TriLLMOrchestrator(
        api_keys=api_keys,
        output_format="markdown"
    )
    
    # Get prompt from user
    prompt = input("\nEnter your prompt (press Enter to use default): ").strip()
    if not prompt:
        prompt = "What are the most effective strategies for learning a new programming language?"
        print(f"\nUsing default prompt: {prompt}")
    
    print("\nStarting orchestration process...")
    results = await orchestrator.orchestrate_full_process(prompt)
    
    # Save results
    filename = f"llm_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    asyncio.run(main())
