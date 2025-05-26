#!/usr/bin/env python3
"""
Test script to run the backend with the correct Python path.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

# Now we can import backend modules
from backend.app import run_server

if __name__ == "__main__":
    run_server()
