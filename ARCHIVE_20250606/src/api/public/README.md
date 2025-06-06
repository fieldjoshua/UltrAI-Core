# Ultra Public API

This directory contains API documentation, specifications, and SDKs for the Ultra AI Framework's public-facing API.

## Directory Structure

- **docs/**: API documentation
  - Detailed endpoint descriptions
  - Authentication guidelines
  - Usage examples
  - Rate limiting information

- **spec/**: OpenAPI specifications
  - `openapi.yaml`: OpenAPI 3.0 specification
  - JSON Schema definitions
  - Request/response examples

- **sdks/**: Software Development Kits
  - Python client library
  - JavaScript/TypeScript client library
  - Other language bindings

## API Endpoints

The Ultra API provides the following key endpoints:

- `/analyze`: Submit text for multi-level analysis
- `/documents`: Upload and manage documents
- `/models`: List available models and capabilities
- `/patterns`: Access and execute specific analysis patterns

## Authentication

The API uses Bearer token authentication. To obtain an API key, contact the development team or sign up through the web interface.

Example:

```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limits

The API has the following rate limits:

- Free tier: 10 requests per minute
- Standard tier: 60 requests per minute
- Enterprise tier: Customized limits

## Using the SDKs

### Python Example

```python
from ultra_sdk import UltraClient

client = UltraClient(api_key="YOUR_API_KEY")
result = client.analyze("What are the implications of this technology?",
                        pattern="critique")
print(result)
```

### JavaScript Example

```javascript
import { UltraClient } from '@ultra/sdk';

const client = new UltraClient({ apiKey: 'YOUR_API_KEY' });
const result = await client.analyze({
  text: 'What are the implications of this technology?',
  pattern: 'critique'
});
console.log(result);
```

## OpenAPI Specification

The API is fully documented using OpenAPI 3.0. You can view the interactive documentation by:

1. Importing the `spec/openapi.yaml` file into tools like Swagger UI, Postman, or Insomnia
2. Visiting the hosted API documentation at `https://api.ultra.ai/docs`

## Changelog

API changes are documented in [CHANGELOG.md](./CHANGELOG.md).

---

*Note: This API documentation has been migrated as part of the Codebase Reorganization Plan. The original location was in `/public_api/`.*
