# Ultra Mock API Server

This directory contains a mock API server implementation for the Ultra AI Framework. The mock server provides simulated endpoints for development and testing purposes.

## Getting Started

To run the mock API server:

```bash
cd src/api/mocks
npm install
npm start
```

The server will be available at <http://localhost:8000>

## Available Endpoints

The mock API server provides the following endpoints:

- `GET /api/documents` - List all documents
- `GET /api/documents/:id` - Get a single document
- `POST /api/upload-document` - Upload a new document
- `DELETE /api/documents/:id` - Delete a document
- `GET /api/available-models` - Get available models
- `GET /api/analysis/history` - Get analysis history
- `POST /api/analyze` - Perform analysis
- `POST /api/analyze-with-docs` - Perform analysis with documents
- `GET /api/analysis/:id` - Get specific analysis

## Mock Data

The server includes mock data for:

- Sample documents
- Available models
- Analysis history
- Generated responses

## File Uploads

File uploads are stored in the `uploads/` directory. This directory is created automatically if it doesn't exist.

## Dependencies

- Express - Web server framework
- CORS - Cross-Origin Resource Sharing support
- Multer - File upload handling

---

*Note: This mock API server has been migrated as part of the Codebase Reorganization Plan. The original location was in `/mock-api/`.*
