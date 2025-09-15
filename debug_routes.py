#!/usr/bin/env python3
"""Debug script to understand route configuration in the app."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment to prevent any production checks
os.environ["ENVIRONMENT"] = "development"
os.environ["TESTING"] = "true"

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
    
    # Test production app
    try:
        print("\n" + "="*60)
        print("PRODUCTION APP CONFIGURATION")
        print("="*60)
        
        from app_production import app as prod_app
        print_routes_for_app("Production App", prod_app)
        
        # Check orchestration service
        if hasattr(prod_app.state, 'orchestration_service'):
            print("\n✓ Orchestration service is initialized in app.state")
        else:
            print("\n✗ Orchestration service NOT found in app.state")
            
    except Exception as e:
        print(f"\nError loading production app: {e}")
        import traceback
        traceback.print_exc()
    
    # Test development app
    try:
        print("\n" + "="*60)
        print("DEVELOPMENT APP CONFIGURATION")
        print("="*60)
        
        from app_development import app as dev_app
        print_routes_for_app("Development App", dev_app)
        
    except Exception as e:
        print(f"\nError loading development app: {e}")
    
    # Test base app
    try:
        print("\n" + "="*60)
        print("BASE APP CONFIGURATION (from app.app)")
        print("="*60)
        
        from app.app import create_app
        base_app = create_app()
        print_routes_for_app("Base App", base_app)
        
    except Exception as e:
        print(f"\nError loading base app: {e}")
    
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
        from app_production import app as prod_app
        prod_routes = {(method, route.path) for route in prod_app.routes 
                      if hasattr(route, 'path') and hasattr(route, 'methods')
                      for method in route.methods}
        
        for endpoint in endpoints_to_check:
            found = any(path == endpoint for _, path in prod_routes)
            print(f"  {endpoint:30} {'✓ Found' if found else '✗ Not Found'}")
    except:
        print("  Could not analyze production routes")

if __name__ == "__main__":
    main()