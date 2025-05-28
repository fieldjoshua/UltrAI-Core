"""
Production app entry point for Render deployment
This file imports the sophisticated backend app with all orchestrator routes
"""

# Import the actual app from backend
from backend.app import app

# Export for uvicorn
__all__ = ["app"]

# Add a startup message to confirm correct app is loaded
@app.on_event("startup")
async def startup_message():
    print("🚀 Production app loaded from backend.app with sophisticated orchestrator routes!")
    print("✅ Available orchestrator endpoints:")
    print("  - /api/orchestrator/models")
    print("  - /api/orchestrator/patterns") 
    print("  - /api/orchestrator/feather")
    print("  - /api/orchestrator/process")