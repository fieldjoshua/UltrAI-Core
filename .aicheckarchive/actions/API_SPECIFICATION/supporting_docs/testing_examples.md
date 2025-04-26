# API Testing Examples

## Overview

This document provides comprehensive examples of testing the UltraAI API, including request/response examples, error handling, authentication, and rate limiting scenarios.

## Request/Response Examples

### 1. Basic Analysis Request

```python
import requests

def test_basic_analysis():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications of this technology?",
        "pattern": "critique",
        "models": ["gpt-4", "claude-3"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200

    result = response.json()
    assert "result" in result
    assert "analysisId" in result
    assert "pattern" in result
    assert "models" in result
```

### 2. Pattern Listing Request

```python
def test_pattern_listing():
    url = "https://api.ultra.ai/patterns"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200

    patterns = response.json()["patterns"]
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    assert all("key" in pattern for pattern in patterns)
    assert all("name" in pattern for pattern in patterns)
```

### 3. Model Listing Request

```python
def test_model_listing():
    url = "https://api.ultra.ai/models"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY"
    }

    response = requests.get(url, headers=headers)
    assert response.status_code == 200

    models = response.json()["models"]
    assert isinstance(models, list)
    assert len(models) > 0
    assert all("id" in model for model in models)
    assert all("name" in model for model in models)
```

## Error Handling Examples

### 1. Invalid Request Parameters

```python
def test_invalid_parameters():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        # Missing required 'pattern' field
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 400

    error = response.json()
    assert "error" in error
    assert "error_description" in error
    assert "missing_field" in error["error_description"]
```

### 2. Invalid Pattern

```python
def test_invalid_pattern():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "invalid_pattern",
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 404

    error = response.json()
    assert "error" in error
    assert "error_description" in error
    assert "available_patterns" in error
```

### 3. Unavailable Model

```python
def test_unavailable_model():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["unavailable-model"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 400

    error = response.json()
    assert "error" in error
    assert "error_description" in error
    assert "available_models" in error
```

## Authentication Examples

### 1. Valid API Key

```python
def test_valid_api_key():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer VALID_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200
```

### 2. Invalid API Key

```python
def test_invalid_api_key():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer INVALID_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 401

    error = response.json()
    assert "error" in error
    assert error["error"] == "invalid_api_key"
```

### 3. Missing API Key

```python
def test_missing_api_key():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 401

    error = response.json()
    assert "error" in error
    assert error["error"] == "missing_api_key"
```

## Rate Limiting Examples

### 1. Within Rate Limit

```python
def test_within_rate_limit():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 200

    rate_limit = response.headers
    assert "X-RateLimit-Limit" in rate_limit
    assert "X-RateLimit-Remaining" in rate_limit
    assert "X-RateLimit-Reset" in rate_limit
```

### 2. Exceeding Rate Limit

```python
def test_exceeding_rate_limit():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    # Make requests until rate limit is exceeded
    responses = []
    for _ in range(100):  # Assuming rate limit is less than 100
        response = requests.post(url, headers=headers, json=data)
        responses.append(response)
        if response.status_code == 429:
            break

    # Check if rate limit was exceeded
    assert any(r.status_code == 429 for r in responses)

    # Check rate limit exceeded response
    rate_limit_exceeded = next(r for r in responses if r.status_code == 429)
    error = rate_limit_exceeded.json()
    assert "error" in error
    assert error["error"] == "rate_limit_exceeded"
    assert "retry_after" in error
```

### 3. Rate Limit Headers

```python
def test_rate_limit_headers():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    response = requests.post(url, headers=headers, json=data)

    # Check rate limit headers
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers

    # Parse header values
    limit = int(response.headers["X-RateLimit-Limit"])
    remaining = int(response.headers["X-RateLimit-Remaining"])
    reset = int(response.headers["X-RateLimit-Reset"])

    # Validate header values
    assert limit > 0
    assert 0 <= remaining <= limit
    assert reset > 0
```

## Integration Testing

### 1. End-to-End Analysis Flow

```python
def test_end_to_end_analysis():
    # 1. Get available patterns
    patterns_url = "https://api.ultra.ai/patterns"
    patterns_response = requests.get(patterns_url, headers={"Authorization": "Bearer YOUR_API_KEY"})
    assert patterns_response.status_code == 200
    patterns = patterns_response.json()["patterns"]

    # 2. Get available models
    models_url = "https://api.ultra.ai/models"
    models_response = requests.get(models_url, headers={"Authorization": "Bearer YOUR_API_KEY"})
    assert models_response.status_code == 200
    models = models_response.json()["models"]

    # 3. Perform analysis
    analysis_url = "https://api.ultra.ai/analyze"
    data = {
        "prompt": "What are the implications of this technology?",
        "pattern": patterns[0]["key"],
        "models": [models[0]["id"]]
    }
    analysis_response = requests.post(analysis_url, headers={"Authorization": "Bearer YOUR_API_KEY"}, json=data)
    assert analysis_response.status_code == 200

    # 4. Verify analysis result
    result = analysis_response.json()
    assert "result" in result
    assert "analysisId" in result
    assert result["pattern"] == patterns[0]["key"]
    assert result["models"] == [models[0]["id"]]
```

### 2. Error Recovery Flow

```python
def test_error_recovery():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }

    # 1. Make invalid request
    invalid_data = {
        "prompt": "What are the implications?",
        "pattern": "invalid_pattern",
        "models": ["gpt-4"]
    }
    invalid_response = requests.post(url, headers=headers, json=invalid_data)
    assert invalid_response.status_code == 404

    # 2. Get available patterns
    patterns_url = "https://api.ultra.ai/patterns"
    patterns_response = requests.get(patterns_url, headers=headers)
    assert patterns_response.status_code == 200
    patterns = patterns_response.json()["patterns"]

    # 3. Make valid request with correct pattern
    valid_data = {
        "prompt": "What are the implications?",
        "pattern": patterns[0]["key"],
        "models": ["gpt-4"]
    }
    valid_response = requests.post(url, headers=headers, json=valid_data)
    assert valid_response.status_code == 200
```

## Performance Testing

### 1. Response Time Test

```python
import time

def test_response_time():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=data)
    end_time = time.time()

    assert response.status_code == 200
    assert end_time - start_time < 5.0  # Response should be under 5 seconds
```

### 2. Concurrent Requests Test

```python
import concurrent.futures

def test_concurrent_requests():
    url = "https://api.ultra.ai/analyze"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "What are the implications?",
        "pattern": "critique",
        "models": ["gpt-4"]
    }

    def make_request():
        return requests.post(url, headers=headers, json=data)

    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        responses = [f.result() for f in futures]

    # Check all requests were successful
    assert all(r.status_code == 200 for r in responses)
```

## Related Documentation

- [API Specification Plan](../API_SPECIFICATION-PLAN.md)
- [Authentication Guide](./authentication_guide.md)
- [Rate Limiting Guide](./rate_limiting_guide.md)
- [Deployment Guide](./deployment_guide.md)

## Last Updated

2024-03-26
