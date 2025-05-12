"""
Docker Model Runner CLI Adapter for Ultra.

This adapter uses the Docker Model CLI commands to run local LLMs.
"""

import os
import sys
import json
import asyncio
import tempfile
from typing import Dict, List, Optional, Any, AsyncGenerator

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Import the base adapter class
from src.models.llm_adapter import LLMAdapter


class DockerModelRunnerCLIAdapter(LLMAdapter):
    """Adapter for Docker Model Runner using CLI commands."""
    
    def __init__(self, model: str):
        """Initialize the Docker Model Runner CLI adapter.
        
        Args:
            model: The model identifier (e.g., "ai/smollm2")
        """
        self.model = model
    
    @staticmethod
    async def get_available_models() -> List[str]:
        """Get list of available models from Docker Model Runner.
        
        Returns:
            List of available model identifiers
        """
        try:
            # Run docker model list command
            process = await asyncio.create_subprocess_exec(
                "docker", "model", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"Error getting models: {stderr.decode()}")
                return []
            
            # Parse the text output
            output = stdout.decode().strip()
            if not output:
                return []
            
            # Parse the table format output
            # Skip header line
            lines = output.split('\n')
            if len(lines) <= 1:
                return []
            
            # Extract model names from first column
            models = []
            for line in lines[1:]:  # Skip header
                parts = line.split()
                if parts:
                    models.append(parts[0])
            
            return models
            
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters for the model
        
        Returns:
            The generated text response
        """
        try:
            # Run docker model run command with the prompt as an argument
            # Wrap the prompt in quotes to handle special characters
            process = await asyncio.create_subprocess_exec(
                "docker", "model", "run", self.model, prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_message = stderr.decode().strip()
                print(f"Error generating response: {error_message}")
                return f"Error: {error_message}"
            
            # Return the generated output
            return stdout.decode().strip()
                    
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"
    
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream a response from the model.
        
        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters for the model
        
        Yields:
            Chunks of the generated text response
        """
        try:
            # Start the process
            process = await asyncio.create_subprocess_exec(
                "docker", "model", "run", self.model, prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Buffer for incomplete lines
            buffer = ""
            
            # Read from stdout as it becomes available
            while True:
                # Read a chunk of output
                chunk = await process.stdout.read(128)
                if not chunk:
                    break
                
                # Decode and add to buffer
                text = chunk.decode()
                buffer += text
                
                # Yield complete buffer
                if buffer:
                    yield buffer
                    buffer = ""
            
            # Check if there was an error
            if await process.wait() != 0:
                stderr_data = await process.stderr.read()
                error_message = stderr_data.decode().strip()
                print(f"Error in streaming: {error_message}")
                yield f"\nError: {error_message}"
                
        except Exception as e:
            print(f"Error in streaming: {str(e)}")
            yield f"\nError: {str(e)}"
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this adapter.
        
        Returns:
            A dictionary of capabilities
        """
        return {
            "streaming": True,
            "max_tokens": 2048,
            "provider": "docker-model-runner",
            "model": self.model
        }


async def create_modelrunner_cli_adapter(model: str) -> DockerModelRunnerCLIAdapter:
    """Create a Docker Model Runner CLI adapter.
    
    Args:
        model: The model identifier (e.g., "ai/smollm2")
    
    Returns:
        A DockerModelRunnerCLIAdapter instance
    """
    return DockerModelRunnerCLIAdapter(model=model)


async def main():
    """Test the Docker Model Runner CLI adapter."""
    print("Testing Docker Model Runner CLI adapter...")
    
    # Get available models
    print("\nAvailable models:")
    models = await DockerModelRunnerCLIAdapter.get_available_models()
    for model in models:
        print(f"- {model}")
    
    if not models:
        print("No models available")
        return
    
    # Create an adapter for the first model
    model = models[0]
    print(f"\nCreating adapter for model: {model}")
    adapter = await create_modelrunner_cli_adapter(model)
    
    # Test generation
    prompt = "What is Docker Model Runner in one sentence?"
    print(f"\nGenerating response for prompt: '{prompt}'")
    response = await adapter.generate(prompt)
    print(f"\nResponse: {response}")
    
    # Test streaming
    prompt = "Explain the concept of containerization."
    print(f"\nStreaming response for prompt: '{prompt}'")
    print("\nResponse: ", end="", flush=True)
    async for chunk in adapter.stream_generate(prompt):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())