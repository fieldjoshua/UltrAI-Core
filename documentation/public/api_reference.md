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

## Request Tracing

To facilitate end-to-end request tracing and debugging, all orchestration endpoints accept an optional `X-Correlation-ID` header.

-   **Header:** `X-Correlation-ID`
-   **Behavior:** If you provide a value in this header (e.g., a UUID), it will be propagated through the entire system, from the initial API request to all log messages and SSE events. This allows you to easily trace the lifecycle of a single request.
-   **Generation:** If you do not provide a `X-Correlation-ID`, a new one will be generated automatically and returned in the response headers.

## Feature Flags

### Enhanced Synthesis

The application includes a feature flag to safely manage the rollout of the Enhanced Synthesis feature.

-   **Environment Variable:** `ENHANCED_SYNTHESIS_ENABLED`
-   **Behavior:** When enabled, the orchestration service will use an improved set of prompts and a more sophisticated model selection strategy for the final synthesis stage. When disabled, it uses the original, stable synthesis logic.
-   **Defaults:**
    -   **Staging:** `true` (Enabled by default for testing)
    -   **Production:** `false` (Disabled by default for safe rollout)

## Endpoints

### Orchestrator

#### `GET /api/orchestrator/status`

Check the service status, including model availability and provider health.

**Successful Response (200 OK):**
```json
{
  "status": "healthy",
  "service_available": true,
  "message": "Service operational with 4 models",
  "environment": "development",
  "api_keys_configured": {
    "openai": true,
    "anthropic": true,
    "google": true,
    "huggingface": false
  },
  "models": {
    "available": [
      "gpt-4o",
      "claude-3-5-sonnet-20241022",
      "gemini-1.5-pro",
      "gpt-3.5-turbo"
    ],
    "count": 4,
    "required": 3,
    "single_model_fallback": false
  },
  "provider_health": {
    "available_providers": ["openai", "anthropic", "google"],
    "total_providers": 3,
    "meets_requirements": true,
    "details": {
      "openai": { "status": "healthy", "is_available": true, "average_latency_ms": 1200 },
      "anthropic": { "status": "healthy", "is_available": true, "average_latency_ms": 980 },
      "google": { "status": "healthy", "is_available": true, "average_latency_ms": 1100 }
    }
  },
  "timestamp": 1678886400.0
}
```

#### `POST /api/orchestrator/analyze`

Submit a query for multi-stage analysis.

**Request Body:**
```json
{
  "query": "Analyze the impact of climate change on global supply chains.",
  "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
}
```

**Successful Response (200 OK):**
```json
{
  "success": true,
  "results": {
    "ultra_synthesis": "Comprehensive analysis of climate change impact...",
    "status": "completed"
  },
  "processing_time": 15.7,
  "pipeline_info": {
    "stages_completed": ["initial_response", "peer_review_and_revision", "ultra_synthesis"],
    "models_used": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
  }
}
```

**Service Unavailable Response (503 Service Unavailable):**
```json
{
  "detail": "UltraAI requires at least 3 models and providers: ['anthropic', 'google', 'openai']; missing: ['google']; available_models=2",
  "error_details": {
    "providers_present": ["anthropic", "openai"],
    "required_providers": ["anthropic", "google", "openai"]
  }
}
```

#### `POST /api/orchestrator/analyze/stream`

Submit a query for analysis and stream back real-time events via Server-Sent Events (SSE).

**Request Body:**
```json
{
  "query": "Analyze the impact of climate change on global supply chains.",
  "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"],
  "stream_stages": ["stage_events", "synthesis_chunks"]
}
```

**SSE Event Stream:**

The stream provides real-time updates on the analysis pipeline.

**Existing Events:**
- `analysis_start`: The overall analysis process has begun.
- `initial_start`: The initial response generation stage has started.
- `model_selected`: A specific model has been chosen for a stage.
- `model_completed`: A specific model has finished its task for a stage.
- `pipeline_complete`: All stages of the pipeline have finished.
- `service_unavailable`: The service is not available.

**New Events for Enhanced Synthesis:**
- `peer_review_start`: The peer review stage has begun.
- `ultra_synthesis_start`: The final synthesis stage has begun.
- `synthesis_complete`: The final synthesis stage has finished.
- `synthesis_chunk` (optional): A token or chunk of the final synthesis is streamed.
- `error`: An error occurred during a stage.

**Standardized Event Payload:**

All new events will follow this schema to provide detailed context.

```json
{
  "event": "ultra_synthesis_start",
  "data": {
    "stage": "synthesis",
    "model": "claude-3-5-sonnet-20241022",
    "provider": "anthropic",
    "correlation_id": "req_abc123",
    "latency_ms": null,
    "data": {
      "synthesis_type": "enhanced",
      "prompt_set": "enhanced",
      "non_participant": true
    }
  }
}
```

**Example New Event Flow:**
```
event: peer_review_start
data: {"stage": "peer_review", "correlation_id": "req_abc123"}

event: ultra_synthesis_start
data: {"stage": "synthesis", "model": "claude-3-5-sonnet-20241022", "provider": "anthropic", "correlation_id": "req_abc123"}

event: synthesis_chunk
data: {"chunk": "The impact of AI..."}

event: synthesis_complete
data: {"stage": "synthesis", "correlation_id": "req_abc123", "latency_ms": 4500}
```

### Legacy Endpoints

#### `POST /api/analyze`
*This endpoint is deprecated. Please use `/api/orchestrator/analyze`.*

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
- 503: Service Unavailable
