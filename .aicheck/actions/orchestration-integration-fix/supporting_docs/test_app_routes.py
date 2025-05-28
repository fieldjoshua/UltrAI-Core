#!/usr/bin/env python3
"""
Test to check which routes are loaded in the app
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Change to backend directory and import
os.chdir(project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

# Import the app
import backend.app
app = backend.app.app

print("=== Checking FastAPI Routes ===\n")

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, "path"):
        routes.append((route.path, route.methods))

# Sort routes
routes.sort()

# Print routes
print(f"Total routes found: {len(routes)}\n")
print("Orchestrator routes:")
for path, methods in routes:
    if "orchestrator" in path:
        print(f"  {path} - {methods}")

print("\nAll API routes:")
for path, methods in routes:
    if path.startswith("/api"):
        print(f"  {path} - {methods}")