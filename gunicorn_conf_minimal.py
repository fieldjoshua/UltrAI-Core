"""Minimal Gunicorn configuration for Render deployment"""

import os

# Use minimal workers for low memory environment
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120

# Bind to Render's PORT
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Basic logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Reduce memory usage
max_requests = 100
max_requests_jitter = 10
preload_app = True  # Load app before forking workers to save memory