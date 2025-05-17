#!/usr/bin/env python3
"""Simple startup script for Replit"""

import os
import sys
import subprocess

def main():
    # Set environment variables
    os.environ.setdefault('ENVIRONMENT', 'production')
    os.environ.setdefault('USE_MOCK', 'false')
    os.environ.setdefault('DEBUG', 'false')
    os.environ.setdefault('API_HOST', '0.0.0.0')
    os.environ.setdefault('API_PORT', '8080')
    
    # Install requirements
    print("Installing requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-replit.txt"])
    
    # Run the app
    print("Starting Ultra API...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "backend.app:app", 
        "--host", "0.0.0.0", 
        "--port", "8080",
        "--reload"
    ])

if __name__ == "__main__":
    main()