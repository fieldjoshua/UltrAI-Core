# UltraAI Core API Reference

## Overview

UltraAI Core provides a comprehensive REST API for multi-model LLM orchestration, user management, and document analysis. All API endpoints are accessible at `https://ultrai-core.onrender.com/api`.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

## Base URL

- Production: `https://ultrai-core.onrender.com/api`
- Development: `http://localhost:8000/api`

## Response Format

All responses follow a consistent format:

```json
{
  "status": "success|error",
  "data": {}, // Response data
  "message": "Optional message",
  "request_id": "unique-request-id"
}
```

## Error Handling

Error responses include detailed information:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": [
    {
      "type": "validation_error",
      "msg": "Invalid email format",
      "loc": ["body", "email"]
    }
  ],
  "request_id": "unique-request-id"
}
```

## Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "username": "johndoe", // Optional
  "full_name": "John Doe" // Optional
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "user",
  "subscription_tier": "free",
  "account_balance": 0.0,
  "is_verified": false,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Login

Authenticate and receive an access token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email_or_username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "role": "user",
    "subscription_tier": "free",
    "account_balance": 25.50
  }
}
```

### Get Current User

Get the authenticated user's information.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "user",
  "subscription_tier": "premium",
  "account_balance": 150.75,
  "is_verified": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

---

## Orchestration Endpoints

### Analyze with Multiple Models

Run the Ultra Synthesis™ pipeline with multiple LLMs.

**Endpoint:** `POST /orchestrator/analyze`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Explain quantum computing applications in finance",
  "selected_models": [
    "gpt-4o",
    "claude-3-5-sonnet-20241022",
    "gemini-1.5-pro"
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "include_pipeline_details": false,
    "save_outputs": true
  }
}
```

**Response (Simplified):**
```json
{
  "ultra_synthesis": "## Ultra Synthesis™: Quantum Computing in Finance\n\n[Comprehensive analysis combining insights from all models...]",
  "metadata": {
    "models_used": ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
    "total_tokens": 4532,
    "estimated_cost": 0.145,
    "processing_time": 8.3
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (With Pipeline Details):**
```json
{
  "initial_response": {
    "gpt-4o": { "response": "...", "tokens": 1234 },
    "claude-3-5-sonnet": { "response": "...", "tokens": 1456 },
    "gemini-1.5-pro": { "response": "...", "tokens": 1342 }
  },
  "peer_review_and_revision": {
    "gpt-4o": { "revised_response": "...", "critiques": [...] },
    "claude-3-5-sonnet": { "revised_response": "...", "critiques": [...] }
  },
  "ultra_synthesis": "## Ultra Synthesis™: ...",
  "metadata": { ... }
}
```

### Get Available Models

List all available LLM models.

**Endpoint:** `GET /available-models`

**Response:**
```json
{
  "models": [
    {
      "id": "gpt-4o",
      "name": "GPT-4 Optimized",
      "provider": "openai",
      "capabilities": ["text", "code", "analysis"],
      "context_window": 128000,
      "pricing": {
        "input_per_1k": 0.005,
        "output_per_1k": 0.015
      }
    },
    {
      "id": "claude-3-5-sonnet-20241022",
      "name": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "capabilities": ["text", "code", "analysis", "vision"],
      "context_window": 200000,
      "pricing": {
        "input_per_1k": 0.003,
        "output_per_1k": 0.015
      }
    }
  ]
}
```

---

## User Balance & Transactions

### Get User Balance

Get current account balance.

**Endpoint:** `GET /user/balance`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "user_id": 1,
  "balance": 150.75,
  "currency": "USD",
  "last_updated": "2024-01-20T15:30:00Z"
}
```

### Get Transaction History

Get user's transaction history.

**Endpoint:** `GET /user/transactions`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `limit` (optional): Number of transactions to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `type` (optional): Filter by transaction type (credit/debit)

**Response:**
```json
{
  "transactions": [
    {
      "id": 123,
      "type": "debit",
      "amount": 0.145,
      "balance_after": 150.75,
      "description": "LLM usage: 3 models, 4532 tokens",
      "created_at": "2024-01-20T15:25:00Z"
    },
    {
      "id": 122,
      "type": "credit",
      "amount": 50.00,
      "balance_after": 150.895,
      "description": "Account top-up",
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total": 45,
  "limit": 50,
  "offset": 0
}
```

---

## Document Management

### Upload Document

Upload a document for analysis.

**Endpoint:** `POST /documents/upload`

**Headers:**
```
Authorization: Bearer <jwt-token>
Content-Type: multipart/form-data
```

**Request:**
```
file: <binary-file-data>
title: "Q4 Financial Report" (optional)
description: "Company financial report for Q4 2023" (optional)
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "q4_report.pdf",
  "title": "Q4 Financial Report",
  "size_bytes": 2456789,
  "mime_type": "application/pdf",
  "status": "processing",
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Get Document

Retrieve document metadata and content.

**Endpoint:** `GET /documents/{document_id}`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "q4_report.pdf",
  "title": "Q4 Financial Report",
  "description": "Company financial report for Q4 2023",
  "size_bytes": 2456789,
  "mime_type": "application/pdf",
  "status": "ready",
  "processed_at": "2024-01-20T10:05:00Z",
  "chunks": 45,
  "download_url": "/documents/doc_abc123/download"
}
```

### Analyze Document

Analyze document with specific prompts.

**Endpoint:** `POST /documents/{document_id}/analyze`

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Request Body:**
```json
{
  "query": "Summarize the key financial metrics and year-over-year growth",
  "analysis_type": "summary",
  "selected_models": ["gpt-4o", "claude-3-5-sonnet"],
  "options": {
    "include_citations": true,
    "max_chunks": 10
  }
}
```

**Response:**
```json
{
  "analysis_id": "analysis_xyz789",
  "document_id": "doc_abc123",
  "status": "completed",
  "result": {
    "summary": "Key financial metrics show...",
    "citations": [
      {
        "text": "Revenue increased by 23% YoY",
        "page": 3,
        "chunk_id": 15
      }
    ]
  },
  "metadata": {
    "models_used": ["gpt-4o", "claude-3-5-sonnet"],
    "chunks_analyzed": 10,
    "processing_time": 12.5,
    "cost": 0.234
  }
}
```

---

## Health & Monitoring

### Health Check

Check API health status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "llm_providers": {
      "openai": "available",
      "anthropic": "available",
      "google": "available"
    }
  }
}
```

### Metrics

Get Prometheus metrics.

**Endpoint:** `GET /metrics`

**Response:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 12543
http_requests_total{method="POST",status="200"} 8921

# HELP llm_requests_total Total LLM API requests
# TYPE llm_requests_total counter
llm_requests_total{provider="openai",model="gpt-4o"} 3421
llm_requests_total{provider="anthropic",model="claude-3-5-sonnet"} 2156
```

---

## Rate Limiting

API requests are rate-limited based on user tier:

| Tier | Requests/Minute | Burst |
|------|----------------|-------|
| Free | 10 | 20 |
| Basic | 60 | 100 |
| Premium | 300 | 500 |
| Enterprise | Unlimited | - |

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705750800
```

---

## Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    "https://ultrai-core.onrender.com/api/auth/login",
    json={
        "email_or_username": "user@example.com",
        "password": "your-password"
    }
)
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "https://ultrai-core.onrender.com/api/orchestrator/analyze",
    headers=headers,
    json={
        "query": "Explain quantum computing",
        "selected_models": ["gpt-4o", "claude-3-5-sonnet"]
    }
)
result = response.json()
print(result["ultra_synthesis"])
```

### JavaScript/TypeScript

```typescript
// Login
const loginResponse = await fetch('https://ultrai-core.onrender.com/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email_or_username: 'user@example.com',
    password: 'your-password'
  })
});
const { access_token } = await loginResponse.json();

// Make authenticated request
const response = await fetch('https://ultrai-core.onrender.com/api/orchestrator/analyze', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'Explain quantum computing',
    selected_models: ['gpt-4o', 'claude-3-5-sonnet']
  })
});
const result = await response.json();
console.log(result.ultra_synthesis);
```

### cURL

```bash
# Login
TOKEN=$(curl -X POST https://ultrai-core.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email_or_username":"user@example.com","password":"your-password"}' \
  | jq -r '.access_token')

# Make authenticated request
curl -X POST https://ultrai-core.onrender.com/api/orchestrator/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain quantum computing",
    "selected_models": ["gpt-4o", "claude-3-5-sonnet"]
  }'
```

---

## SDKs

Official SDKs are planned for:
- Python
- JavaScript/TypeScript
- Go
- Ruby

For now, use the REST API directly with your preferred HTTP client.

---

## Support

- GitHub Issues: https://github.com/your-org/ultrai-core/issues
- API Status: https://status.ultrai.app
- Documentation: https://docs.ultrai.app