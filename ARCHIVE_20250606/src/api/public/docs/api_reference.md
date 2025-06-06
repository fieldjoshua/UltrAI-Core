# API Documentation

## Overview

This document describes the API endpoints available in the Ultra backend for prompt analysis and LLM management.

## Authentication

All API endpoints require authentication using a Bearer token. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- 100 requests per minute per IP address
- 100 requests per minute per authenticated user
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when the limit resets

## Endpoints

### Analyze Prompt

```http
POST /api/analyze
```

Analyze a prompt using multiple LLMs and an Ultra LLM.

**Request Body:**

```json
{
  "prompt": "string",
  "selected_models": ["string"],
  "ultra_model": "string",
  "pattern": "string",
  "options": ["string"],
  "max_tokens": 0,
  "stream": false
}
```

**Response:**

```json
{
  "status": "success",
  "analysis_id": "string",
  "results": {
    "model_responses": {},
    "ultra_response": {},
    "performance": {
      "total_time_seconds": 0,
      "model_times": {},
      "token_counts": {}
    }
  }
}
```

### Get Analysis Progress

```http
GET /api/analyze/{analysis_id}/progress
```

Get the progress of a multi-stage analysis.

**Response:**

```json
{
  "status": "success",
  "analysis_id": "string",
  "progress": {
    "status": "string",
    "current_stage": "string",
    "stages": {
      "stage_name": {
        "status": "string",
        "progress": 0
      }
    }
  }
}
```

### Get Analysis Results

```http
GET /api/analyze/{analysis_id}/results
```

Get the results of a completed analysis.

**Response:**

```json
{
  "status": "success",
  "analysis_id": "string",
  "results": {
    "model_responses": {},
    "ultra_response": {},
    "performance": {
      "total_time_seconds": 0,
      "model_times": {},
      "token_counts": {}
    }
  }
}
```

### Get Available LLMs

```http
GET /api/llms
```

Get a list of available LLM models.

**Query Parameters:**

- `tags`: Filter models by tags
- `capability`: Filter models by capability

**Response:**

```json
{
  "status": "success",
  "count": 0,
  "models": [
    {
      "name": "string",
      "description": "string",
      "capabilities": ["string"],
      "tags": ["string"]
    }
  ]
}
```

### Get Analysis Patterns

```http
GET /api/patterns
```

Get a list of available analysis patterns.

**Response:**

```json
{
  "status": "success",
  "count": 0,
  "patterns": ["string"]
}
```

## Error Responses

All endpoints return standard error responses:

```json
{
  "status": "error",
  "message": "Error description"
}
```

Common HTTP status codes:

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error
