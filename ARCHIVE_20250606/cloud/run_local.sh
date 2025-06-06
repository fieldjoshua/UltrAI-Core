#!/bin/bash
# Run the FastAPI backend locally for development

echo "Starting UltraAI Cloud Backend on port 8000..."
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
