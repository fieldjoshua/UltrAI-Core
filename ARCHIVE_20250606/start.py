#!/usr/bin/env python3
"""
Simple entry point script for the UltraAI Backend
This script works around import issues and properly sets up paths
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ultra_starter")

# Add the parent directory to Python path for 'backend' module
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent.absolute()
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))
logger.info(f"Path setup: Added {parent_dir} and {current_dir} to Python path")


def start_backend():
    """Start the backend API server"""
    parser = argparse.ArgumentParser(description="Run the UltraAI backend server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8085, help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--mock", action="store_true", help="Run in mock mode with simulated responses"
    )
    args = parser.parse_args()

    # Set environment variable for mock mode
    if args.mock:
        os.environ["USE_MOCK"] = "true"
        logger.info("Starting backend in MOCK MODE - using simulated responses")

    # Server runtime info
    logger.info(f"Starting UltraAI backend on http://{args.host}:{args.port}")
    logger.info("API docs will be available at /api/docs")

    # Attempt to start the server by trying different approaches
    try:
        # Try to find the API object in main.py
        logger.info("Approach 1: Trying to load FastAPI app from main.py")
        try:
            # Clear away any cached imports first
            if "main" in sys.modules:
                del sys.modules["main"]

            import main

            if hasattr(main, "app"):
                logger.info("Using FastAPI app from main.py")
                import uvicorn

                uvicorn.run(
                    "main:app",
                    host=args.host,
                    port=args.port,
                    reload=args.reload,
                    log_level="info",
                )
                return
            else:
                logger.warning("No 'app' object found in main.py")
        except ImportError as e:
            logger.warning(f"Failed to import main.py: {str(e)}")

        # Try alternative approaches with direct app import
        logger.info("Approach 2: Trying to load app in a different way")
        try:
            import uvicorn

            os.chdir(current_dir)  # Make sure we're in the backend directory
            uvicorn.run(
                "app:app",
                host=args.host,
                port=args.port,
                reload=args.reload,
                log_level="info",
            )
            return
        except ImportError as e:
            logger.warning(f"Failed to load app: {str(e)}")

        # Direct command execution
        logger.info("Approach 3: Running main.py directly")
        import subprocess

        # SECURITY NOTE: We are only running our own script with trusted arguments
        # No user input is being passed to subprocess
        cmd = [sys.executable, "main.py"]
        if args.mock:
            cmd.append("--mock")
        subprocess.run(cmd, check=True)

    except Exception as e:
        logger.error(f"All backend start approaches failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    start_backend()
