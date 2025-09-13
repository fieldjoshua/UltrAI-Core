"""
Production app entry point for deployment.
This file is used by Render to start the production server.
"""
import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

# Now import the app creation function
from app.main import create_production_app

# Create the production app instance
app = create_production_app()
