# Ultra API

This directory contains API-related code for the Ultra AI Framework, including public API specifications, client implementations, and mock servers for development and testing.

## Directory Structure

- **public/**: Public API documentation, specifications, and SDKs
  - `.aicheck/actions/API_SPECIFICATION/supporting_docs/`: API documentation and guides
  - `spec/`: OpenAPI specifications
  - `sdks/`: Client libraries for different languages

- **mocks/**: Mock API implementations for development
  - `server.js`: Express server with mock endpoints
  - `uploads/`: Directory for file uploads in development

- **index.js**: Main API entry point
- **config.js**: API configuration settings

## Development

For development, you can use the mock API server:

```bash
cd src/api/mocks
npm install
npm start
```

The mock server will be available at <http://localhost:8000> and provides endpoints that simulate the behavior of the real API.

## Production API

The production API implementation is available in the backend directory. The specifications in `public/spec/` define the expected behavior of all API endpoints.

## Related Documentation

- [API Specification](../../.aicheck/actions/API_SPECIFICATION/API_SPECIFICATION-PLAN.md)
- [Backend Documentation](../../backend/README.md)
- [Frontend API Integration](../../frontend/api/README.md)

---

*Note: This API directory structure was created as part of the Codebase Reorganization Plan. It consolidates API-related code that was previously scattered across multiple locations.*
