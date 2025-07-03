import sys
import os
import asyncio
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

# ---------------------------------------------------------------------------
# Fix for async event loop conflicts
# ---------------------------------------------------------------------------

# Check if we're in a Jupyter-like environment
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

# Force pytest-asyncio to use function-scoped event loops
import pytest_asyncio
pytest_asyncio.fixture(scope="function")

# Configure asyncio for tests
import pytest
pytest_plugins = ('pytest_asyncio',)

# No mocking - tests will use real network calls

# (OpenAIAdapter stub removed – real adapter will be used with individual tests patching requests)

# ---------------------------------------------------------------------------
# Playwright configuration to use system-installed Chrome instead of bundled browser
# ---------------------------------------------------------------------------

# Fixture recognised by pytest-playwright across versions

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Launch Playwright using the local Chrome executable in headless mode."""

    chrome_path = os.getenv(
        "CHROME_EXECUTABLE",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )
    return {"executable_path": chrome_path, "headless": True}


# ---------------------------------------------------------------------------
# Provide proper async event loop fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    # Ensure all tasks are complete
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    # Run until all tasks are cancelled
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    loop.close()


# No stubbing - all tests will use real implementations or explicit mocks