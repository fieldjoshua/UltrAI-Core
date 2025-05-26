#!/usr/bin/env python3
"""
Fix for PatternOrchestrator Import Issue
This script demonstrates the fix needed for production deployment
"""

import os
import sys

def fix_orchestrator_imports():
    """
    Fix the import issues in orchestrator_routes.py
    """
    
    print("🔧 Fixing PatternOrchestrator import issues...")
    
    # Read the current orchestrator_routes.py
    routes_file = "/Users/joshuafield/Documents/Ultra/backend/routes/orchestrator_routes.py"
    
    with open(routes_file, 'r') as f:
        content = f.read()
    
    # Fix 1: Remove the complex sys.path manipulation
    old_import_block = """# Add project root to Python path to ensure we can import our sophisticated orchestrator
# even when FastAPI is run from elsewhere
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Import our sophisticated orchestrator
try:
    # Import the sophisticated PatternOrchestrator from src/core
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator
    from src.patterns.ultra_analysis_patterns import get_pattern_mapping"""
    
    # New import that works better in production
    new_import_block = """# Import our sophisticated orchestrator with proper path handling
try:
    # Try direct import first (works in development)
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator
    from src.patterns.ultra_analysis_patterns import get_pattern_mapping
except ImportError:
    try:
        # Try backend-relative import (works when backend is the main module)
        from ..integrations.pattern_orchestrator import PatternOrchestrator
        from ..models.enhanced_orchestrator import get_pattern_mapping
    except ImportError:
        # Final fallback - use the orchestrator from backend directory
        try:
            import sys
            import os
            # Add parent directory to path for production environments
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            root_dir = os.path.dirname(parent_dir)
            if root_dir not in sys.path:
                sys.path.append(root_dir)
            
            from src.core.ultra_pattern_orchestrator import PatternOrchestrator
            from src.patterns.ultra_analysis_patterns import get_pattern_mapping
        except ImportError as e:
            print(f"⚠️ Could not import PatternOrchestrator: {e}")
            raise"""
    
    # Replace the import block
    content = content.replace(old_import_block, new_import_block)
    
    # Save the fixed file
    fixed_file = "/Users/joshuafield/Documents/Ultra/.aicheck/actions/comprehensive-system-validation/supporting_docs/orchestrator_routes_fixed.py"
    with open(fixed_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed import saved to: {fixed_file}")
    
    # Create a requirements file with all needed dependencies
    requirements_content = """# Core Dependencies for UltraAI Orchestrator
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6

# LLM Provider SDKs
openai>=1.12.0
anthropic>=0.18.1
google-generativeai>=0.3.2
mistralai>=0.0.8
cohere>=4.39
perplexity>=0.1.0

# Async Support
aiohttp>=3.9.0
httpx>=0.25.0

# Utilities
python-dotenv>=1.0.0
tenacity>=8.2.3
"""
    
    requirements_file = "/Users/joshuafield/Documents/Ultra/.aicheck/actions/comprehensive-system-validation/supporting_docs/requirements-orchestrator.txt"
    with open(requirements_file, 'w') as f:
        f.write(requirements_content)
    
    print(f"✅ Requirements file created: {requirements_file}")
    
    # Create a simpler orchestrator integration for backend
    integration_content = '''"""
Pattern Orchestrator Integration for Backend
This provides a cleaner integration point for the sophisticated orchestrator
"""

import os
import sys

# Ensure src directory is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
src_dir = os.path.join(root_dir, "src")

for directory in [root_dir, src_dir]:
    if directory not in sys.path and os.path.exists(directory):
        sys.path.insert(0, directory)

# Now import the orchestrator
try:
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator
    from src.patterns.ultra_analysis_patterns import get_pattern_mapping
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import PatternOrchestrator: {e}")
    # Provide fallback implementations
    class PatternOrchestrator:
        """Fallback PatternOrchestrator for when imports fail"""
        def __init__(self, api_keys, pattern="gut", output_format="plain"):
            self.api_keys = api_keys
            self.pattern = pattern
            self.output_format = output_format
            self.available_models = list(api_keys.keys()) if api_keys else []
        
        async def orchestrate_full_process(self, prompt):
            return {
                "initial_responses": {"mock": "PatternOrchestrator not available"},
                "meta_responses": {"mock": "Import failed in production"},
                "hyper_responses": {"mock": "Check logs for import errors"},
                "ultra_response": "PatternOrchestrator import failed. Check deployment configuration.",
                "processing_time": 0.0
            }
    
    def get_pattern_mapping():
        return {
            "gut": None,
            "confidence": None,
            "critique": None,
            "fact_check": None,
            "perspective": None,
            "scenario": None
        }
    
    ORCHESTRATOR_AVAILABLE = False

# Export the orchestrator components
__all__ = ["PatternOrchestrator", "get_pattern_mapping", "ORCHESTRATOR_AVAILABLE"]
'''
    
    integration_file = "/Users/joshuafield/Documents/Ultra/.aicheck/actions/comprehensive-system-validation/supporting_docs/pattern_orchestrator_integration.py"
    with open(integration_file, 'w') as f:
        f.write(integration_content)
    
    print(f"✅ Integration module created: {integration_file}")
    
    print("\n📋 Next Steps:")
    print("1. Copy pattern_orchestrator_integration.py to backend/integrations/")
    print("2. Update orchestrator_routes.py with the fixed import")
    print("3. Ensure requirements-orchestrator.txt dependencies are included")
    print("4. Redeploy to Render")
    
    return True

if __name__ == "__main__":
    fix_orchestrator_imports()