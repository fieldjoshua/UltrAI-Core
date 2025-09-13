"""
Production app entry point for deployment.
This file is used by Render to start the production server.
"""
import os
from dotenv import load_dotenv

<<<<<<< HEAD
# Load environment variables before any other imports
load_dotenv()

# Now import the app creation function
=======
# Load environment variables FIRST before any other imports
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Now import the app after environment is loaded
>>>>>>> origin/main
from app.main import create_production_app

# Create the production app instance
app = create_production_app()
