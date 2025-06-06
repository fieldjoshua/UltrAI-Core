"""
Production app entry point for deployment.
This file is used by Render to start the production server.
"""

from app.main import create_production_app

# Create the production app instance
app = create_production_app()
