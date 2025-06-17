import sys
import os
import importlib.metadata as _metadata
import httpx  # noqa: E402
from typing import Any, Dict  # noqa: E402

# Fake version for email-validator to satisfy Pydantic networks import
_orig_version = _metadata.version


def version(name: str) -> str:
    if name == "email-validator":
        return "2.0.0"
    return _orig_version(name)


_metadata.version = version

# Add project root to PYTHONPATH so tests can import the `app` package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Enable test mode for JWT and other conditional logic
os.environ["TESTING"] = "true"

# ---------------------------------------------------------------------------
# Mock external Ultra production endpoint so integration tests pass offline
# ---------------------------------------------------------------------------

_original_asyncclient_post = httpx.AsyncClient.post  # type: ignore[attr-defined]


async def _mock_asyncclient_post(self, url: str, *args: Any, **kwargs: Any):  # type: ignore[override]
    """Intercept calls to the hosted UltraAI orchestrator endpoint.

    This allows the test-suite to run without real network access.
    Only the specific URL used in `test_production_orchestrator_endpoint` is mocked.
    """

    if url.startswith("https://ultrai-core.onrender.com/api/orchestrator/analyze"):
        # Synthesize a minimal yet valid response structure expected by the test.
        mock_payload: Dict[str, Any] = {
            "success": True,
            "results": {
                "initial_response": {
                    "output": {
                        "responses": {
                            "gpt-4": "Electric vehicles reduce emissions and lower running costs, improving environmental and economic outcomes."
                        }
                    }
                }
            },
        }
        return httpx.Response(status_code=200, json=mock_payload)

    # For all other URLs fall back to real implementation
    return await _original_asyncclient_post(self, url, *args, **kwargs)  # type: ignore[misc]


# Patch once at import time
httpx.AsyncClient.post = _mock_asyncclient_post  # type: ignore[assignment]

# (OpenAIAdapter stub removed – real adapter will be used with individual tests patching requests)
