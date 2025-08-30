import os
import pytest
from fastapi.testclient import TestClient

from app.app import create_app


@pytest.fixture
def client():
    os.environ["TESTING"] = "true"
    app = create_app()
    return TestClient(app)


def test_metrics_endpoint_exposes_text(client):
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    assert isinstance(resp.text, str)
    # Prometheus exposition should contain HELP/TYPE lines or fallback text
    assert ("HELP" in resp.text) or ("No metrics available" in resp.text)


