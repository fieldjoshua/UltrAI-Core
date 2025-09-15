import os
import pytest
import requests


# Only run live demo tests when explicitly enabled
pytestmark = pytest.mark.skipif(
    os.getenv("ULTRA_RUN_LIVE") != "1",
    reason="Live demo tests disabled by default; set ULTRA_RUN_LIVE=1 to enable",
)


def get_base_url() -> str:
    url = os.environ.get("DEMO_BASE_URL")
    if url:
        return url.rstrip("/")
    # default to staging demo api
    return "https://ultrai-staging-api.onrender.com"


def _skip_on_502(resp: requests.Response, path: str) -> None:
    if resp.status_code == 502:
        pytest.skip(f"Endpoint {path} returned 502 (service unavailable)")


@pytest.mark.live
def test_demo_health_available_models():
    base = get_base_url()

    r = requests.get(f"{base}/health", timeout=15)
    _skip_on_502(r, "/health")
    assert r.status_code == 200

    r = requests.get(f"{base}/available-models", timeout=20)
    _skip_on_502(r, "/available-models")
    assert r.status_code == 200
    data = r.json()
    assert "total_count" in data


@pytest.mark.live
def test_demo_models_providers_summary():
    base = get_base_url()
    r = requests.get(f"{base}/models/providers-summary", timeout=20)
    _skip_on_502(r, "/models/providers-summary")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)

