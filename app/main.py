"""
Production app entry point for Render deployment
"""

import os
import sys
from app.app import app
from app.services.model_registry import ModelRegistry
from app.services.analysis_pipeline import AnalysisPipeline
from app.services.prompt_templates import PromptTemplateManager

# Set the project root path to allow for correct module resolution
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Instantiate core services
model_registry = ModelRegistry()
prompt_template_manager = PromptTemplateManager()
analysis_pipeline = AnalysisPipeline(model_registry)

# Attach services to app state for dependency injection
app.state.model_registry = model_registry
app.state.prompt_template_manager = prompt_template_manager
app.state.analysis_pipeline = analysis_pipeline

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
    print(
        "  - ModelRegistry, PromptTemplateManager, and AnalysisPipeline are initialized and available via app.state."
    )
