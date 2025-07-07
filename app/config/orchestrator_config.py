"""Central configuration for the MinimalOrchestrator and related services.

Values can be overridden via environment variables so that deployments can tune
behaviour without code changes.
"""

from __future__ import annotations

import os
from typing import Any


class _Config:
    """Reads environment variables once at import time and exposes attributes."""

    # Parallelism / timeouts
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("ORCH_MAX_CONCURRENT", 3))
    TIMEOUT_SECONDS: int = int(os.getenv("ORCH_TIMEOUT_SECONDS", 30))

    # Prompt context management
    MAX_CONTEXT_TOKENS: int = int(os.getenv("ORCH_MAX_CONTEXT_TOKENS", 6000))
    TRUNCATION_FACTOR: float = float(os.getenv("ORCH_TRUNCATION_FACTOR", 0.8))

    # Pricing defaults (USD per 1K tokens) – can be overridden per provider
    DEFAULT_PRICE_PER_1K: float = float(os.getenv("ORCH_DEFAULT_PRICE_PER_1K", 0.03))

    # Encryption defaults
    ENCRYPTION_KEY: str | None = os.getenv("ORCH_ENCRYPTION_KEY")

    def as_dict(self) -> dict[str, Any]:
        return {
            k: v for k, v in self.__class__.__dict__.items() if not k.startswith("__")
        }


CONFIG = _Config()
