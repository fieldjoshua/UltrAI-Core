import asyncio
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from string import Template
from typing import Any, Dict, List, Optional

import google.generativeai as genai
import openai
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

print("Testing API clients individually...")

# Test Llama
try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama2", "prompt": "test", "stream": False},
    )
    print("Llama client initialized successfully")
except Exception as e:
    print(f"Llama Error: {str(e)}")

# Test OpenAI
try:
    oai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"OpenAI Error: {str(e)}")

# Test Google
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini = genai.GenerativeModel("gemini-pro")
    print("Gemini client initialized successfully")
except Exception as e:
    print(f"Gemini Error: {str(e)}")

# Continue with rest of your code...

# Debug environment variables immediately
print("Checking environment variables...")
api_keys = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY"),
}

for name, key in api_keys.items():
    if key:
        print(f"{name}: {key[:4]}...{key[-4:]}")
    else:
        print(f"{name}: NOT FOUND")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    meta_round: str = """Original prompt: $original_prompt

Here are responses from three different LLMs to this prompt:

Llama's response:
$llama_response

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

Llama's meta-response:
$llama_meta

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
                "Is clearly structured and well-organized",
            ]
        if self.ultra_instructions is None:
            self.ultra_instructions = [
                "Captures the most valuable insights from all meta-responses",
                "Eliminates redundancy and reconciles any remaining contradictions",
                "Presents the information in the most effective and coherent way",
                "Represents the best possible answer to the original prompt",
            ]


@dataclass
class RateLimits:
    llama_rpm: int = 100
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
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        ultra_engine: str = "llama",
    ):
        print("Initializing TriLLMOrchestrator...")

        self.logger = logging.getLogger(__name__)
        self.templates = prompt_templates or PromptTemplate()
        self.rate_limits = rate_limits or RateLimits()
        self.ultra_engine = ultra_engine

        # Store API keys and print first/last 4 chars
        print("\nChecking API keys...")
        self.openai_key = api_keys["openai"]
        self.google_key = api_keys["google"]

        for name, key in [("OpenAI", self.openai_key), ("Google", self.google_key)]:
            if key:
                print(f"{name}: {key[:4]}...{key[-4:]}")
            else:
                print(f"{name}: NOT FOUND")

        # Set up formatter
        print("\nSetting up formatter...")
        if output_format == "markdown":
            self.formatter = ResponseFormatter.format_markdown
        elif output_format == "json":
            self.formatter = ResponseFormatter.format_json
        else:
            self.formatter = ResponseFormatter.format_plain

        # Initialize clients with error handling
        print("\nInitializing API clients...")
        try:
            print("Initializing Llama...")
            # Test the connection
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": "test", "stream": False},
            )
            if response.status_code == 200:
                print("Llama initialized successfully")
            else:
                print(f"Llama initialization failed with status {response.status_code}")
        except Exception as e:
            print(f"Error initializing Llama: {str(e)}")

        try:
            print("Initializing OpenAI...")
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            print("OpenAI initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI: {str(e)}")

        try:
            print("Initializing Gemini...")
            genai.configure(api_key=self.google_key)
            self.gemini_model = genai.GenerativeModel("gemini-pro")
            print("Gemini initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini: {str(e)}")

        self.base_dir = os.path.join(os.getcwd(), "responses")
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(self.base_dir, self.run_timestamp)
        self._setup_directory()

    def _setup_directory(self):
        """Create directory for this run"""
        os.makedirs(self.run_dir, exist_ok=True)

    def _save_response(self, response: str, filename: str):
        """Save a response to a file in the run directory"""
        filepath = os.path.join(self.run_dir, f"{filename}.txt")
        with open(filepath, "w") as f:
            f.write(response)

    async def _respect_rate_limit(self, client_name: str):
        """Rate limiting logic"""
        await asyncio.sleep(1)  # Simple rate limiting for now

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_llama_response(self, prompt: str) -> str:
        await self._respect_rate_limit("llama")
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama2", "prompt": prompt, "stream": False},
            )

            if response.status_code == 200:
                result = response.json()
                return self.formatter(result["response"])
            else:
                raise Exception(f"Llama HTTP error: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Error with Llama API: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_gemini_response(self, prompt: str) -> str:
        await self._respect_rate_limit("gemini")
        try:
            # Generate content synchronously
            response = self.gemini_model.generate_content(prompt)
            # Extract text directly
            if hasattr(response, "text"):
                return self.formatter(response.text)
            elif hasattr(response, "parts"):
                return self.formatter(response.parts[0].text)
            else:
                raise Exception("Unexpected Gemini response format")
        except Exception as e:
            self.logger.error(f"Error with Gemini API: {str(e)}")
            raise

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

            # Handle responses individually
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

    def _create_meta_prompt(
        self, responses: Dict[str, str], original_prompt: str
    ) -> str:
        template_vars = {
            "original_prompt": original_prompt,
            "llama_response": responses["llama"],
            "chatgpt_response": responses["chatgpt"],
            "gemini_response": responses["gemini"],
        }

        for i, instruction in enumerate(self.templates.meta_instructions, 1):
            template_vars[f"meta_instruction_{i}"] = instruction

        return Template(self.templates.meta_round).safe_substitute(template_vars)

    def _create_ultra_prompt(
        self, meta_responses: Dict[str, str], original_prompt: str
    ) -> str:
        template_vars = {
            "original_prompt": original_prompt,
            "llama_meta": meta_responses["llama"],
            "chatgpt_meta": meta_responses["chatgpt"],
            "gemini_meta": meta_responses["gemini"],
        }

        for i, instruction in enumerate(self.templates.ultra_instructions, 1):
            template_vars[f"ultra_instruction_{i}"] = instruction

        return Template(self.templates.ultra_round).safe_substitute(template_vars)

    async def get_meta_responses(
        self, initial_responses: Dict[str, str], original_prompt: str
    ) -> Dict[str, str]:
        try:
            meta_prompt = self._create_meta_prompt(initial_responses, original_prompt)

            responses = await asyncio.gather(
                self.get_llama_response(meta_prompt),
                self.get_chatgpt_response(meta_prompt),
                self.get_gemini_response(meta_prompt),
            )
            return {
                "llama": responses[0],
                "chatgpt": responses[1],
                "gemini": responses[2],
            }
        except Exception as e:
            self.logger.error(f"Error getting meta responses: {str(e)}")
            raise

    async def get_ultra_response(
        self, meta_responses: Dict[str, str], original_prompt: str
    ) -> str:
        try:
            ultra_prompt = self._create_ultra_prompt(meta_responses, original_prompt)

            # Use the chosen engine for the ultra response
            if self.ultra_engine == "llama":
                return await self.get_llama_response(ultra_prompt)
            elif self.ultra_engine == "chatgpt":
                return await self.get_chatgpt_response(ultra_prompt)
            elif self.ultra_engine == "gemini":
                return await self.get_gemini_response(ultra_prompt)
            else:
                raise ValueError(f"Invalid ultra engine: {self.ultra_engine}")

        except Exception as e:
            self.logger.error(f"Error getting ultra response: {str(e)}")
            raise

    def _get_keyword_from_prompt(self, prompt: str) -> str:
        """Extract a meaningful keyword from the prompt"""
        # Remove common words and get the first significant word
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "please",
            "edit",
            "following",
        }

        # Get the first meaningful word from the prompt
        words = prompt.lower().split()
        keyword = next(
            (word for word in words if word not in common_words and len(word) > 2),
            "task",
        )

        # Clean the keyword
        keyword = "".join(c for c in keyword if c.isalnum())
        return keyword[:15]  # Limit length

    def _save_response(self, response: str, filename: str):
        """Save a response to a file in the run directory"""
        # Use the keyword instead of generic names
        filepath = os.path.join(self.run_dir, f"{self.keyword}_{filename}.txt")
        with open(filepath, "w") as f:
            f.write(response)

    async def _analyze_self_for_patent(self):
        """Analyze Ultra's code for patent application purposes"""
        try:
            # Get Ultra's own code
            with open(__file__, "r") as f:
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
                self.get_gemini_response(patent_analysis_prompt),
            )

            # Save patent analyses
            for model, response in zip(["llama", "chatgpt", "gemini"], responses):
                self._save_response(response, f"patent_analysis_{model}")

        except Exception as e:
            self.logger.error(f"Patent analysis error (non-critical): {str(e)}")

    async def orchestrate_full_process(self, prompt: str) -> Dict[str, Any]:
        # Start patent analysis in parallel
        patent_task = asyncio.create_task(self._analyze_self_for_patent())

        # Regular process continues as normal
        start_time = datetime.now()
        self.prompt = prompt
        self.keyword = self._get_keyword_from_prompt(prompt)

        # Create timestamped directory with keyword
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(
            self.base_dir, f"{self.keyword}_{self.run_timestamp}"
        )
        self._setup_directory()

        try:
            # Save the original prompt
            self._save_response(prompt, "prompt")

            # Get and save initial responses
            initial_responses = await self.get_initial_responses(prompt)
            for model, response in initial_responses.items():
                self._save_response(response, f"initial_{model}")

            # Get and save meta responses
            meta_responses = await self.get_meta_responses(initial_responses, prompt)
            for model, response in meta_responses.items():
                self._save_response(response, f"meta_{model}")

            # Get and save ultra response
            ultra_response = await self.get_ultra_response(meta_responses, prompt)
            self._save_response(ultra_response, "ultra")

            # Save metadata
            metadata = {
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "prompt": prompt,
                "keyword": self.keyword,
                "success": True,
            }
            self._save_response(json.dumps(metadata, indent=2), "metadata")

            # Wait for patent analysis but don't let it block the main process
            try:
                await asyncio.wait_for(patent_task, timeout=60)  # 60 second timeout
            except asyncio.TimeoutError:
                pass  # Continue even if analysis isn't done

            return {
                "original_prompt": prompt,
                "initial_responses": initial_responses,
                "meta_responses": meta_responses,
                "ultra_response": ultra_response,
                "metadata": metadata,
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
                "error": str(e),
            }
            self._save_response(json.dumps(metadata, indent=2), "metadata")
            raise

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_chatgpt_response(self, prompt: str) -> str:
        await self._respect_rate_limit("chatgpt")
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
            )
            return self.formatter(response.choices[0].message.content)
        except Exception as e:
            self.logger.error(f"Error with ChatGPT API: {str(e)}")
            raise


async def test_env():
    print("\nTesting environment variables...")

    # Load the .env file
    load_dotenv()

    # Check each API key
    keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        # Removed ANTHROPIC_API_KEY since we're using local Llama
    }

    all_good = True
    for name, value in keys.items():
        if value:
            print(f"✓ {name}: {value[:4]}...{value[-4:]} (Length: {len(value)})")
        else:
            print(f"✗ {name}: NOT FOUND")
            all_good = False

    # Test Llama connection
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": "test", "stream": False},
        )
        print("✓ Llama: Connected successfully")
    except Exception as e:
        print(f"✗ Llama: Connection failed - {str(e)}")
        all_good = False

    if all_good:
        print("\nAll services are available! ✓")
    else:
        print("\nSome services are not available! ✗")
        print("Please check your setup and ensure all services are running.")

    return all_good


async def test_apis():
    print("\nTesting APIs individually...")

    # Test Llama
    print("\nTesting Llama...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama2", "prompt": "Hello", "stream": False},
        )
        if response.status_code == 200:
            print("Llama test successful!")
        else:
            print(f"Llama test failed with status {response.status_code}")
    except Exception as e:
        print(f"Llama test failed: {str(e)}")

    # Test OpenAI
    print("\nTesting OpenAI...")
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview", messages=[{"role": "user", "content": "Hello"}]
        )
        if response.choices[0].message.content:
            print("OpenAI test successful!")
    except Exception as e:
        print(f"OpenAI test failed: {str(e)}")

    # Test Gemini
    print("\nTesting Gemini...")
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Hello")
        print("Gemini test successful!")
    except Exception as e:
        print(f"Gemini test failed: {str(e)}")


async def main():
    # Test environment variables first
    env_ok = await test_env()
    if not env_ok:
        return

    # Test APIs
    await test_apis()

    # Get user input for prompt
    print("\nEnter your prompt (press Enter twice when finished):")
    prompt_lines = []
    while True:
        line = input()
        if line == "":
            break
        prompt_lines.append(line)
    user_prompt = "\n".join(prompt_lines)

    # Get user choice for ultra engine
    while True:
        print("\nWhich engine should create the ultra response?")
        print("1. Llama")
        print("2. ChatGPT")
        print("3. Gemini")
        choice = input("Enter your choice (1-3): ")

        if choice in ["1", "2", "3"]:
            ultra_engine = {"1": "llama", "2": "chatgpt", "3": "gemini"}[choice]
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    # Initialize the orchestrator with the chosen ultra engine
    orchestrator = TriLLMOrchestrator(
        api_keys={
            "openai": os.getenv("OPENAI_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
        },
        ultra_engine=ultra_engine,
    )

    print(f"\nProcessing with {ultra_engine.upper()} as the ultra engine...")
    results = await orchestrator.orchestrate_full_process(user_prompt)

    print("\nAll responses have been saved to:", orchestrator.run_dir)


if __name__ == "__main__":
    asyncio.run(main())
