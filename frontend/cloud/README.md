# UltraAI Cloud Frontend

This directory contains the frontend application for the UltraAI Cloud service. The cloud frontend provides a web interface for accessing UltraAI features through a cloud-based deployment.

## Files

- `app.js` - Main application logic
- `index.html` - HTML entry point
- `vercel.json` - Vercel deployment configuration
- `run_local.sh` - Script to run the frontend locally

## Development

To run the cloud frontend locally:

```bash
cd frontend/cloud
./run_local.sh
```

## Deployment

The cloud frontend is configured for deployment with Vercel. The `vercel.json` file contains the deployment configuration.

## Related Components

The cloud frontend works with the [cloud backend](../../backend/cloud) to provide a complete cloud-based UltraAI experience.

---

*Note: This cloud frontend has been migrated as part of the Codebase Reorganization Plan. The original location was in `/cloud_frontend/`.*
