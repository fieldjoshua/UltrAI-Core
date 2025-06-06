"""
Production app entry point for Render deployment
"""

import os
import sys

# Set the project root path to allow for correct module resolution
# This is the definitive fix for all import errors.
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Import the actual app from our new, clean 'app' directory
from app.app import app

# Export for uvicorn
__all__ = ["app"]


# Add a startup message to confirm correct app is loaded
@app.on_event("startup")
async def startup_message():
    print(
        "🚀 Production app loaded from backend.app with sophisticated orchestrator routes!"
    )
    print("✅ Available orchestrator endpoints:")
    print("  - /api/orchestrator/models")
    print("  - /api/orchestrator/patterns")
    print("  - /api/orchestrator/feather")
    print("  - /api/orchestrator/process")
