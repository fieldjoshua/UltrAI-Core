# Vercel serverless function wrapper
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

# Export the FastAPI app for Vercel
app = app