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

### Orchestrator Service Status

```http
GET /api/orchestrator/status
```

Get the current status of the orchestration service, including provider availability and system readiness.

**Response (Service Ready):**

```json
{
  "ready": true,
  "models_available": 3,
  "models_required": 3,
  "providers_present": ["openai", "anthropic", "google"],
  "required_providers": ["openai", "anthropic", "google"],
  "service_status": "ready",
  "message": "Service is ready for orchestration",
  "degradation_message": null,
  "healthy_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"]
}
```

**Response (Service Unavailable - 503):**

```json
{
  "error": "SERVICE_UNAVAILABLE",
  "message": "UltraAI requires at least 3 models from the required providers to be functional",
  "details": {
    "models_required": 3,
    "models_available": 1,
    "required_providers": ["openai", "anthropic", "google"],
    "providers_present": ["openai"],
    "service_status": "degraded"
  }
}
```

### Analyze Query

```http
POST /api/orchestrator/analyze
```

Analyze a query using the UltraAI 3-stage orchestration pipeline with multiple LLMs.

**Request Body:**

```json
{
  "query": "Explain the benefits of microservices architecture",
  "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"],
  "modules": ["confidence", "traceability"],
  "stream": false
}
```

**Response (Success):**

```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "request_id": "correlation-id",
  "results": {
    "initial_responses": {
      "gpt-4o": {
        "content": "Microservices architecture offers...",
        "model": "gpt-4o",
        "provider": "openai",
        "latency_ms": 1250
      }
    },
    "peer_reviews": {
      "claude-3-5-sonnet-20241022": {
        "content": "Building on the previous response...",
        "confidence_score": 0.9
      }
    },
    "ultra_synthesis": {
      "content": "Comprehensive analysis of microservices...",
      "consensus_score": 0.85,
      "key_insights": ["scalability", "maintainability", "fault_tolerance"]
    },
    "performance": {
      "total_time_ms": 4500,
      "stage_times": {
        "initial": 1250,
        "peer_review": 1100,
        "synthesis": 2150
      }
    }
  }
}
```

**Response (Service Unavailable - 503):**

```json
{
  "error": "SERVICE_UNAVAILABLE",
  "message": "UltraAI requires at least 3 models from the required providers to be functional",
  "details": {
    "models_required": 3,
    "models_available": 1,
    "required_providers": ["openai", "anthropic", "google"],
    "providers_present": ["openai"],
    "service_status": "degraded"
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
