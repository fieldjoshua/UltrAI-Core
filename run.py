#!/usr/bin/env python3
"""
Unified entry point for development and production.
Handles environment detection and appropriate server configuration.
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the application with environment-appropriate settings."""
    # Get configuration from environment
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    print(f"Starting UltraAI Core in {environment} mode on port {port}")
    
    if environment == "development":
        # Development mode with hot reload
        uvicorn.run(
            "app_production:app",
            host="0.0.0.0",
            port=port,
            reload=True,
            log_level="info"
        )
    else:
        # Production mode - no reload, optimized
        from app_production import app
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="warning"
        )

if __name__ == "__main__":
    main()