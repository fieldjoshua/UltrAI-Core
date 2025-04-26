# API Specification

## Base URL

```
http://localhost:8085/api
```

## Authentication

All endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Document Management

#### Upload Document

```http
POST /documents/upload
Content-Type: multipart/form-data

file: <file>
```

Response:

```json
{
    "document_id": "string",
    "filename": "string",
    "status": "string",
    "uploaded_at": "datetime"
}
```

#### Get Document Status

```http
GET /documents/{document_id}/status
```

Response:

```json
{
    "document_id": "string",
    "status": "string",
    "processing_progress": "float"
}
```

### LLM Integration

#### List Available LLMs

```http
GET /llms
```

Response:

```json
{
    "llms": [
        {
            "id": "string",
            "name": "string",
            "description": "string",
            "capabilities": ["string"]
        }
    ]
}
```

#### Process Document with LLM

```http
POST /analyze
Content-Type: application/json

{
    "document_id": "string",
    "llm_id": "string",
    "analysis_type": "string",
    "prompt": "string"
}
```

Response:

```json
{
    "analysis_id": "string",
    "status": "string",
    "result": "string",
    "created_at": "datetime"
}
```

### Analysis Types

#### List Available Analysis Types

```http
GET /analysis/types
```

Response:

```json
{
    "types": [
        {
            "id": "string",
            "name": "string",
            "description": "string",
            "supported_llms": ["string"]
        }
    ]
}
```

## Error Responses

All endpoints may return the following error responses:

```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": "object"
    }
}
```

Common error codes:

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

Rate limits are applied per endpoint:

- Document upload: 10 requests per minute
- LLM processing: 5 requests per minute
- Other endpoints: 20 requests per minute
