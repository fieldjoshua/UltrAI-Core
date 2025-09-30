"""
E2E tests for production frontend deployment.
Verifies the deployed frontend is functional and correctly configured.
"""
import os
import pytest
import requests

# These are smoke tests that verify production deployment
# Run with: pytest tests/e2e/test_production_frontend.py

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://ultrai-prod-ui.onrender.com")
API_URL = os.getenv("API_URL", "https://ultrai-prod-api.onrender.com")


@pytest.mark.e2e
@pytest.mark.production
def test_frontend_loads():
    """Verify frontend loads and returns HTML (not black screen)."""
    response = requests.get(FRONTEND_URL, timeout=30)
    assert response.status_code == 200, f"Frontend returned {response.status_code}"
    
    html = response.text
    assert len(html) > 1000, "Frontend HTML suspiciously short"
    assert "<html" in html.lower(), "Response is not HTML"
    assert "Ultra AI" in html, "Frontend missing app title"


@pytest.mark.e2e
@pytest.mark.production
def test_frontend_has_correct_api_url():
    """Verify frontend bundle contains correct production API URL."""
    response = requests.get(FRONTEND_URL, timeout=30)
    assert response.status_code == 200
    
    html = response.text
    # The correct API URL should be in the preconnect or will be in the JS bundle
    # Check that it's NOT pointing to wrong endpoints
    assert "ultrai-core.onrender.com" not in html or "ultrai-prod-api.onrender.com" in html, \
        "Frontend may be pointing to wrong API endpoint"
    
    # Verify it's not using localhost
    assert "localhost:8000" not in html, "Frontend pointing to localhost instead of production API"


@pytest.mark.e2e
@pytest.mark.production
def test_frontend_has_javascript():
    """Verify frontend includes JavaScript bundles (prevents black screen)."""
    response = requests.get(FRONTEND_URL, timeout=30)
    assert response.status_code == 200
    
    html = response.text
    assert '<script' in html.lower(), "Frontend missing JavaScript"
    assert 'type="module"' in html, "Frontend missing Vite module script"
    assert '/assets/index-' in html, "Frontend missing main bundle"


@pytest.mark.e2e
@pytest.mark.production
def test_api_is_reachable_from_frontend():
    """Verify the API endpoint the frontend will call is actually reachable."""
    health_url = f"{API_URL}/api/health"
    response = requests.get(health_url, timeout=30)
    assert response.status_code == 200, f"API health check failed: {response.status_code}"
    
    data = response.json()
    assert data.get("status") == "ok", f"API unhealthy: {data}"


@pytest.mark.e2e
@pytest.mark.production
def test_frontend_assets_load():
    """Verify frontend static assets (CSS, JS) are accessible."""
    # First get the HTML to find asset paths
    response = requests.get(FRONTEND_URL, timeout=30)
    assert response.status_code == 200
    
    html = response.text
    
    # Extract a CSS file path
    import re
    css_match = re.search(r'href="(/assets/[^"]+\.css)"', html)
    if css_match:
        css_path = css_match.group(1)
        css_url = f"{FRONTEND_URL}{css_path}"
        css_response = requests.get(css_url, timeout=30)
        assert css_response.status_code == 200, f"CSS asset failed to load: {css_path}"
        assert len(css_response.text) > 100, "CSS file suspiciously small"
    
    # Extract a JS file path
    js_match = re.search(r'src="(/assets/[^"]+\.js)"', html)
    if js_match:
        js_path = js_match.group(1)
        js_url = f"{FRONTEND_URL}{js_path}"
        js_response = requests.get(js_url, timeout=30)
        assert js_response.status_code == 200, f"JS asset failed to load: {js_path}"
        assert len(js_response.text) > 1000, "JS file suspiciously small"


@pytest.mark.e2e
@pytest.mark.production
def test_api_models_available():
    """Verify API has models available for frontend to use."""
    models_url = f"{API_URL}/api/available-models"
    response = requests.get(models_url, timeout=30)
    assert response.status_code == 200, f"Available models endpoint failed: {response.status_code}"
    
    models = response.json()
    assert len(models) > 0, "No models available"
    assert len(models) >= 15, f"Expected 15+ models, got {len(models)}"
    
    # Verify we have models from multiple providers
    providers = set(model.get("provider") for model in models.values())
    assert len(providers) >= 3, f"Expected 3+ providers, got {len(providers)}: {providers}"


@pytest.mark.e2e
@pytest.mark.production
def test_cors_headers_present():
    """Verify API has CORS headers so frontend can call it."""
    health_url = f"{API_URL}/api/health"
    response = requests.options(health_url, timeout=30, headers={
        "Origin": FRONTEND_URL,
        "Access-Control-Request-Method": "GET"
    })
    
    # CORS preflight should work
    assert response.status_code in [200, 204], f"CORS preflight failed: {response.status_code}"
    
    # Check for CORS headers in regular request
    response = requests.get(health_url, timeout=30, headers={
        "Origin": FRONTEND_URL
    })
    
    # At minimum, should have CORS origin header
    cors_header = response.headers.get("Access-Control-Allow-Origin")
    assert cors_header is not None, "API missing CORS headers"