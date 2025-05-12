"""Gunicorn configuration file for Ultra API"""

import os
import multiprocessing

# Worker configuration
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))

# Bind configuration
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")

# Logging configuration
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")

# Performance tuning
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", 1000))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))

# Process naming
proc_name = "ultra_api"