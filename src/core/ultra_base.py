import asyncio
import json
import logging
import os
import platform
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import torch
from dotenv import load_dotenv

load_dotenv()


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


class UltraBase:
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None,
    ):
        print("Initializing UltraBase...")

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Store configuration
        self.api_keys = api_keys
        self.prompt_templates = prompt_templates or PromptTemplate()
        self.rate_limits = rate_limits or RateLimits()
        self.output_format = output_format
        self.enabled_features = enabled_features or []

        # Initialize hardware configuration
        self._initialize_hardware()

        # Initialize base directory
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.run_dir = os.path.join(
            self.base_dir, datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        os.makedirs(self.run_dir, exist_ok=True)

        # Initialize rate limiting
        self.last_request_time = {"llama": 0, "chatgpt": 0, "gemini": 0}

        # Initialize clients
        self._initialize_clients()

    def _initialize_hardware(self):
        """Initialize hardware-specific configurations."""
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.max_threads = psutil.cpu_count(logical=False)
        self.executor = ThreadPoolExecutor(max_workers=self.max_threads)

        if self.device == "mps":
            torch.backends.mps.enable_fallback_to_cpu = True

        print("\nHardware Configuration:")
        print(f"Device: {self.device}")
        print(f"Processor: {platform.processor()}")
        print(f"Physical Cores: {self.max_threads}")
        print(
            f"Memory Available: {psutil.virtual_memory().available / (1024 * 1024 * 1024):.2f} GB"
        )
        if self.device == "mps":
            print("Apple Silicon GPU acceleration enabled")
            print("GPU Cores: 30")
            print("Metal backend: Active")

    def _initialize_clients(self):
        """Initialize API clients based on enabled features."""
        # This method should be implemented by child classes
        pass

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        return feature in self.enabled_features

    async def save_response(self, response: str, prefix: str):
        """Save a response to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.txt"
        filepath = os.path.join(self.run_dir, filename)

        with open(filepath, "w") as f:
            f.write(response)

        self.logger.info(f"Saved response to {filepath}")
        return filepath
