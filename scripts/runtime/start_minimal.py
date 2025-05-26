#!/usr/bin/env python3
"""Ultra minimal startup script for Render deployment"""

import os

import uvicorn

from app_simple import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, workers=1, log_level="info")
