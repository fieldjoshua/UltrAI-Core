# UltraAI Cloud Backend

This directory contains the backend services for the UltraAI Cloud service. The cloud backend provides API endpoints and services that power the cloud-based deployment of the UltraAI platform.

## Files

- `main.py` - Main application entry point with FastAPI implementation
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel deployment configuration
- `run_local.sh` - Script to run the backend locally

## Development

To run the cloud backend locally:

```bash
cd backend/cloud
pip install -r requirements.txt
./run_local.sh
```

The server will be available at <http://localhost:8000>

## API Endpoints

The cloud backend provides the following key endpoints:

- `GET /api/health` - Health check endpoint
- `GET /api/models` - List available models
- `GET /api/analysis-types` - List available analysis types
- `GET /api/alacarte-options` - List available a la carte options
- `GET /api/output-formats` - List available output formats
- `POST /api/analyze` - Perform analysis with selected models

## Deployment

The cloud backend is configured for deployment with Vercel. The `vercel.json` file contains the deployment configuration.

## Related Components

The cloud backend works with the [cloud frontend](../../frontend/cloud) to provide a complete cloud-based UltraAI experience.

---

*Note: This cloud backend has been migrated as part of the Codebase Reorganization Plan. The original location was in `/cloud_backend/`.*
