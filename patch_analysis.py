"""Patch script to apply the analysis fix."""
import sys
import os
import importlib.util

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Import our analysis fix
try:
    from src.simple_core.analysis_fix import patch_modular_orchestrator
    success = patch_modular_orchestrator()
    if success:
        print("Successfully applied analysis fix patch")
    else:
        print("Failed to apply analysis fix patch")
except Exception as e:
    print(f"Error importing analysis fix: {e}")

# Exit with success status
sys.exit(0)
