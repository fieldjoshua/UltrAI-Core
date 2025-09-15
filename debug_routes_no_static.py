#!/usr/bin/env python3
"""Debug script to understand route configuration without static files."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment to prevent any production checks and skip static mounting
os.environ["ENVIRONMENT"] = "development"
os.environ["TESTING"] = "true"
os.environ["SKIP_STATIC_MOUNT"] = "true"

def print_routes_for_app(app_name, app):
    """Print all routes for a FastAPI app."""
    print(f"\n{'='*60}")
    print(f"Routes for {app_name}:")
    print('='*60)
    
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            for method in route.methods:
                routes.append((method, route.path, route.name))
    
    # Sort by path for easier reading
    routes.sort(key=lambda x: (x[1], x[0]))
    
    for method, path, name in routes:
        print(f"{method:6} {path:40} -> {name}")
    
    print(f"\nTotal routes: {len(routes)}")

def main():
    """Main debug function."""
    
    # Temporarily mock StaticFiles to prevent errors
    import sys
    from unittest.mock import Mock
    sys.modules['fastapi.staticfiles'] = Mock()
    sys.modules['fastapi.staticfiles'].StaticFiles = Mock(return_value=Mock())
    
    # Test base app by modifying create_app
    try:
        print("\n" + "="*60)
        print("BASE APP ROUTES (without static files)")
        print("="*60)
        
        # Patch the create_app function to skip static file mounting
        import app.app
        original_create_app = app.app.create_app
        
        def patched_create_app():
            # Save original path check
            original_exists = os.path.exists
            
            # Mock os.path.exists to return False for frontend/dist
            def mock_exists(path):
                if 'frontend/dist' in path:
                    return False
                return original_exists(path)
            
            os.path.exists = mock_exists
            try:
                app = original_create_app()
                return app
            finally:
                os.path.exists = original_exists
        
        app.app.create_app = patched_create_app
        base_app = app.app.create_app()
        print_routes_for_app("Base App", base_app)
        
    except Exception as e:
        print(f"\nError loading base app: {e}")
        import traceback
        traceback.print_exc()
    
    # Check for specific routes
    print("\n" + "="*60)
    print("ROUTE ANALYSIS")
    print("="*60)
    
    print("\nLooking for key endpoints:")
    endpoints_to_check = [
        "/api/orchestrate",
        "/api/orchestrator/analyze", 
        "/api/models",
        "/api/available-models",
        "/api/model-health",
        "/health",
        "/api/health"
    ]
    
    try:
        if 'base_app' in locals():
            routes = {(method, route.path) for route in base_app.routes 
                     if hasattr(route, 'path') and hasattr(route, 'methods')
                     for method in route.methods}
            
            for endpoint in endpoints_to_check:
                found = any(path == endpoint for _, path in routes)
                print(f"  {endpoint:30} {'✓ Found' if found else '✗ Not Found'}")
                
            # Also look for partial matches
            print("\nPartial matches for 'orchestrat':")
            orchestrator_routes = [(method, path) for method, path in routes if 'orchestrat' in path]
            for method, path in sorted(orchestrator_routes):
                print(f"  {method:6} {path}")
                
            print("\nPartial matches for 'model':")
            model_routes = [(method, path) for method, path in routes if 'model' in path]
            for method, path in sorted(model_routes):
                print(f"  {method:6} {path}")
    except:
        print("  Could not analyze routes")

if __name__ == "__main__":
    main()