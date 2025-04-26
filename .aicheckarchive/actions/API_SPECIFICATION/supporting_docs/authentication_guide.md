# API Authentication Guide

## Overview

This document details the authentication mechanisms used in the UltraAI API, including OAuth2 implementation, API key management, and security best practices.

## Authentication Methods

### 1. OAuth2 Authentication

The API supports OAuth2 authentication for secure access to protected resources.

#### OAuth2 Flow

1. **Authorization Request**

   ```
   GET /oauth/authorize
   ?client_id=YOUR_CLIENT_ID
   &redirect_uri=YOUR_REDIRECT_URI
   &response_type=code
   &scope=analysis documents
   ```

2. **Token Request**

   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code
   &code=AUTHORIZATION_CODE
   &redirect_uri=YOUR_REDIRECT_URI
   &client_id=YOUR_CLIENT_ID
   &client_secret=YOUR_CLIENT_SECRET
   ```

3. **Token Response**

   ```json
   {
     "access_token": "ACCESS_TOKEN",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "REFRESH_TOKEN",
     "scope": "analysis documents"
   }
   ```

### 2. API Key Authentication

For simpler integrations, the API supports API key authentication.

#### API Key Usage

```http
Authorization: Bearer YOUR_API_KEY
```

#### Obtaining an API Key

1. Register through the web interface
2. Navigate to API Settings
3. Generate a new API key
4. Store the key securely

## Token Lifecycle

### Access Tokens

- Valid for 1 hour
- Used for API requests
- Must be refreshed using refresh token

### Refresh Tokens

- Valid for 30 days
- Used to obtain new access tokens
- Should be stored securely

### API Keys

- Valid until revoked
- Can be regenerated at any time
- Should be rotated periodically

## Security Best Practices

1. **Token Storage**
   - Never store tokens in client-side code
   - Use secure storage mechanisms
   - Implement token rotation

2. **API Key Management**
   - Rotate keys periodically
   - Use different keys for different environments
   - Implement key revocation

3. **Request Security**
   - Always use HTTPS
   - Validate all input
   - Implement rate limiting

4. **Error Handling**
   - Don't expose sensitive information in errors
   - Log authentication failures
   - Implement proper error responses

## Error Responses

### Invalid Token

```json
{
  "error": "invalid_token",
  "error_description": "The access token is invalid or expired"
}
```

### Invalid API Key

```json
{
  "error": "invalid_api_key",
  "error_description": "The API key is invalid or has been revoked"
}
```

### Rate Limit Exceeded

```json
{
  "error": "rate_limit_exceeded",
  "error_description": "Too many requests",
  "retry_after": 60
}
```

## Implementation Examples

### Python

```python
import requests

def get_access_token(client_id, client_secret, code):
    response = requests.post(
        'https://api.ultra.ai/oauth/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    return response.json()

def make_api_request(access_token):
    response = requests.get(
        'https://api.ultra.ai/analyze',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    return response.json()
```

### JavaScript

```javascript
async function getAccessToken(clientId, clientSecret, code) {
    const response = await fetch('https://api.ultra.ai/oauth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            grant_type: 'authorization_code',
            code: code,
            client_id: clientId,
            client_secret: clientSecret
        })
    });
    return response.json();
}

async function makeApiRequest(accessToken) {
    const response = await fetch('https://api.ultra.ai/analyze', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    return response.json();
}
```

## Related Documentation

- [API Specification Plan](../API_SPECIFICATION-PLAN.md)
- [Rate Limiting Guide](./rate_limiting_guide.md)
- [Deployment Guide](./deployment_guide.md)

## Last Updated

2024-03-26
