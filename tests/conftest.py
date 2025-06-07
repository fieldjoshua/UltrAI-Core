import sys
import os

# Add project root to PYTHONPATH so tests can import the `app` package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
