import logging
import os

import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("production-test")


def test_health_endpoint():
    """Test health endpoint in production environment"""
    # Get API host and port from environment variables
    api_host = os.environ.get("API_HOST", "127.0.0.1")
    api_port = os.environ.get("API_PORT", "8085")

    # Construct URL
    url = f"http://{api_host}:{api_port}/api/health"

    # Make request
    logger.info(f"Testing health endpoint at {url}")

    try:
        # Make request with special test header
        response = requests.get(url, headers={"X-Test-Mode": "true"})

        # Log response
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text[:100]}...")

        # Check response
        assert (
            response.status_code == 200
        ), f"Expected 200 OK, got {response.status_code}"
        data = response.json()

        # Check required fields
        assert "status" in data, "Response missing 'status' field"
        assert "version" in data, "Response missing 'version' field"

        return True
    except Exception as e:
        logger.error(f"Error testing health endpoint: {e}")
        return False


if __name__ == "__main__":
    success = test_health_endpoint()
    exit(0 if success else 1)
