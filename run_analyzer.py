#!/usr/bin/env python3
"""
Runner script for the analyzer CLI.

This script provides a simple way to launch the analyzer CLI
with common configurations.
"""

import sys
import os


if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Import the CLI module
    from src.cli.analyzer import main
    
    # Set default environment variables if not set
    if 'USE_MOCK' not in os.environ:
        os.environ['USE_MOCK'] = 'true'
    
    # Run the CLI
    main()