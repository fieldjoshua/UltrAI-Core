#!/usr/bin/env python3
"""Test that frontend is properly served from the backend"""

import os
import sys

# Check if frontend dist exists
frontend_dist = "frontend/dist"
if not os.path.exists(frontend_dist):
    print(f"ERROR: {frontend_dist} does not exist!")
    print("Run 'cd frontend && npm install && npm run build' first")
    sys.exit(1)

# Check for index.html
index_html = os.path.join(frontend_dist, "index.html")
if not os.path.exists(index_html):
    print(f"ERROR: {index_html} does not exist!")
    sys.exit(1)

print("✓ Frontend dist directory exists")
print("✓ index.html found")

# Quick test to ensure the app can import
try:
    from app_production import app
    print("✓ app_production imports successfully")
    
    # Check that root route is removed
    routes = [route.path for route in app.routes]
    if "/" in routes:
        for route in app.routes:
            if route.path == "/" and hasattr(route, 'endpoint'):
                print("WARNING: Root API route still exists!")
                print(f"  Endpoint: {route.endpoint}")
    else:
        print("✓ Root route removed (good for static serving)")
        
    print("\nFrontend should now be accessible at: http://localhost:8000/")
    print("API docs available at: http://localhost:8000/docs")
    
except Exception as e:
    print(f"ERROR importing app: {e}")
    sys.exit(1)