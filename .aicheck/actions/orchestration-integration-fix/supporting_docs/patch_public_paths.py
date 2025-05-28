#!/usr/bin/env python3
"""
Temporary patch to add orchestrator endpoints to public paths for testing
"""

import fileinput
import sys

# Path to the app.py file
app_file = "/Users/joshuafield/Documents/Ultra/backend/app.py"

# Find and replace the setup_api_key_middleware call
search_line = "    setup_api_key_middleware(app)"
replace_line = '''    setup_api_key_middleware(
        app,
        public_paths=[
            "/api/auth/",
            "/health",
            "/metrics", 
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/favicon.ico",
            "/api/orchestrator/",  # Temporarily add orchestrator endpoints
        ]
    )'''

def patch_file():
    """Add orchestrator endpoints to public paths"""
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        if search_line in content:
            new_content = content.replace(search_line, replace_line)
            with open(app_file, 'w') as f:
                f.write(new_content)
            print("✅ Successfully patched app.py to add orchestrator endpoints to public paths")
            print("🔄 Please restart the server for changes to take effect")
        else:
            print("❌ Could not find the line to patch in app.py")
            print("   Looking for:", search_line)
            
    except Exception as e:
        print(f"❌ Error patching file: {e}")

if __name__ == "__main__":
    patch_file()