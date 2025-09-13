"""Utility for estimating request cost based on token usage.

The estimator uses a simple provider → USD per 1K token mapping.  Values can be
updated at runtime via environment variables, e.g.:

    export PRICE_OPENAI=0.01

If a provider's price is unknown we fall back to the default price defined in
CONFIG.
"""

from __future__ import annotations

import os
from typing import Dict

# Default price per 1K tokens if provider is unknown
DEFAULT_PRICE_PER_1K = float(os.getenv("DEFAULT_PRICE_PER_1K", "0.005"))

# ---------------------------------------------------------------------------
# Pricing table (USD per 1K tokens)
# ---------------------------------------------------------------------------

_DEFAULT_PRICING = {
    "openai": float(os.getenv("PRICE_OPENAI", "0.01")),  # GPT-4o 128k prompt tier
    "anthropic": float(os.getenv("PRICE_ANTHROPIC", "0.008")),  # Claude 3 Sonnet
    "google": float(os.getenv("PRICE_GOOGLE", "0.005")),  # Gemini 1.5 Pro
}


def estimate_cost(token_counts: Dict[str, int], provider: str | None = None) -> float:
    """Estimate the USD cost for the given token counts.

    Args:
        token_counts: mapping of stage → token_count.  We sum them.
        provider: 'openai' | 'anthropic' | 'google' etc.  If None, use default.
    Returns:
        Cost in USD (rounded to 4 decimal places).
    """
    total_tokens = sum(token_counts.values())
    price_per_1k = _DEFAULT_PRICING.get(provider or "", DEFAULT_PRICE_PER_1K)
    cost = (total_tokens / 1000.0) * price_per_1k
    return round(cost, 4)
