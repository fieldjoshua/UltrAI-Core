"""
Staging smoke tests for Big 3 provider readiness.

These tests hit the staging API directly to verify:
- At least one healthy model per Big 3 (openai, anthropic, google)
- Providers summary shows the Big 3 configured

Note: These tests are intended for staging/CI synthetic checks, not unit tests.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List


STAGING_BASE_URL: str = os.environ.get(
    "STAGING_API_BASE", "https://ultrai-staging-api.onrender.com/api"
).rstrip("/")

BIG3_PROVIDERS = {"openai", "anthropic", "google"}


def _http_get_json(url: str, timeout_seconds: float = 12.0) -> Dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # nosec B310
        data = response.read().decode("utf-8")
    return json.loads(data)


def test_providers_summary_all_big3_configured() -> None:
    summary_url = f"{STAGING_BASE_URL}/models/providers-summary"
    payload = _http_get_json(summary_url)

    assert "providers" in payload, f"Missing 'providers' in response: {payload}"
    providers = payload["providers"]

    configured = {
        name for name, info in providers.items() if info and info.get("configured") is True
    }

    missing = BIG3_PROVIDERS - configured
    assert not missing, (
        f"Big 3 providers not configured: {sorted(missing)} | configured={sorted(configured)}"
    )


def test_at_least_one_healthy_model_per_big3() -> None:
    # Allow a brief wait to reduce flakiness during rolling deploys
    time.sleep(0.5)
    healthy_url = f"{STAGING_BASE_URL}/available-models?healthy_only=true"
    payload = _http_get_json(healthy_url)

    assert "models" in payload, f"Missing 'models' in response: {payload}"
    models: List[Dict[str, Any]] = payload["models"]

    providers_with_healthy = {m.get("provider") for m in models if m.get("status") == "available"}
    providers_with_healthy.discard(None)

    missing = BIG3_PROVIDERS - providers_with_healthy
    assert not missing, (
        "Missing healthy models for providers: "
        f"{sorted(missing)} | providers_with_healthy={sorted(providers_with_healthy)} | "
        f"models={[(m.get('name'), m.get('provider'), m.get('status')) for m in models]}"
    )


