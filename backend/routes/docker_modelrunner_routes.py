"""
Routes for interacting with Docker Model Runner.

This module provides API endpoints for testing and using Docker Model Runner LLMs.
"""

import asyncio
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Global variables for adapters
DockerModelRunnerCLIAdapter = None
create_modelrunner_cli_adapter = None
DockerModelRunnerAdapter = None
get_available_models = None

# Try to import the CLI adapter
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    try:
        from models.docker_modelrunner_cli_adapter import (
            DockerModelRunnerCLIAdapter,
            create_modelrunner_cli_adapter,
        )
    except ImportError:
        from backend.models.docker_modelrunner_cli_adapter import (
            DockerModelRunnerCLIAdapter,
            create_modelrunner_cli_adapter,
        )
except ImportError as e:
    logging.error(f"Failed to import Docker Model Runner CLI adapter: {e}")

# Try to import the API adapter
try:
    try:
        from models.docker_modelrunner_adapter import (
            DockerModelRunnerAdapter,
            get_available_models,
        )
    except ImportError:
        from backend.models.docker_modelrunner_adapter import (
            DockerModelRunnerAdapter,
            get_available_models,
        )
except ImportError as e:
    logging.error(f"Failed to import Docker Model Runner API adapter: {e}")

# Create router
router = APIRouter(
    prefix="/api/modelrunner",
    tags=["modelrunner"],
    responses={404: {"description": "Not found"}},
)

# Logger
logger = logging.getLogger("modelrunner_routes")


class ModelRunnerRequest(BaseModel):
    """Request model for Docker Model Runner API."""

    prompt: str = Field(..., description="The prompt to send to the model")
    model: Optional[str] = Field(
        None, description="The model to use (defaults to configured default)"
    )
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Temperature for generation")
    stream: Optional[bool] = Field(False, description="Whether to stream the response")


@router.get("/models")
async def list_models():
    """List available Docker Model Runner models."""
    try:
        # Direct Docker CLI call to list models (simplest approach for testing)
        try:
            logger.info("Listing Docker models via CLI")

            # Alternative approach - use shell command to invoke Docker Model CLI on host
            # This could be python scripting if available in the container
            cmd = 'ls -la /var/run/docker.sock || echo "Docker socket not found" && docker model list || echo "Docker model command not available"'

            # For debugging - show environment
            logger.info(
                f"Environment: PATH={os.environ.get('PATH', 'N/A')}, DOCKER_HOST={os.environ.get('DOCKER_HOST', 'N/A')}"
            )

            # Execute the command
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error = stderr.decode().strip()
                logger.error(f"Docker model list command failed: {error}")
                raise HTTPException(
                    status_code=500, detail=f"Docker model list command failed: {error}"
                )

            # Parse the output to extract model names
            output = stdout.decode().strip()
            lines = output.split("\n")
            models = []

            # Skip header line
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split()
                    if parts:
                        models.append(parts[0])  # First column is model name

            return {"models": models}
        except Exception as e:
            logger.error(f"Error listing Docker models: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error listing Docker models: {str(e)}"
            )
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")


@router.post("/generate")
async def generate(request: ModelRunnerRequest):
    """Generate a response using Docker Model Runner."""
    try:
        model_runner_type = os.getenv("MODEL_RUNNER_TYPE", "cli").lower()
        default_model = os.getenv("DEFAULT_LOCAL_MODEL", "ai/smollm2")

        # Use requested model or default
        model = request.model or default_model

        # Direct Docker CLI call (simplest approach for testing)
        try:
            logger.info(f"Running Docker model command with model {model}")
            # Quote the prompt to handle special characters
            quoted_prompt = request.prompt.replace('"', '\\"')
            cmd = f'docker model run {model} "{quoted_prompt}"'

            # For debugging - show environment
            logger.info(
                f"Running with model: {model}, Environment: PATH={os.environ.get('PATH', 'N/A')}"
            )

            # Alternative approach - directly run the model
            # In a container environment, we may need to use a different approach
            cmd = f'docker model run {model} "{quoted_prompt}" || echo "Docker model command failed"'

            # Execute the command
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error = stderr.decode().strip()
                logger.error(f"Docker model command failed: {error}")
                raise HTTPException(
                    status_code=500, detail=f"Docker model command failed: {error}"
                )

            response = stdout.decode().strip()
            return {"model": model, "response": response}
        except Exception as e:
            logger.error(f"Error executing Docker model command: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error executing Docker model command: {str(e)}",
            )

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}"
        )
