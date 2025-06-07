import sys
import os
import importlib.metadata as _metadata

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
