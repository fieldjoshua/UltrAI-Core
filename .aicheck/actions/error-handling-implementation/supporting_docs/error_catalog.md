# Error Catalog

## Error Code Structure

Format: `CATEGORY_NUMBER`

Categories:

- AUTH: Authentication
- AUTHZ: Authorization
- VAL: Validation
- LLM: LLM Provider
- SYS: System
- NET: Network

## Error Definitions

### Authentication Errors (AUTH)

| Code     | Message             | HTTP Status | Recovery             |
| -------- | ------------------- | ----------- | -------------------- |
| AUTH_001 | Invalid credentials | 401         | Re-enter credentials |
| AUTH_002 | Token expired       | 401         | Refresh token        |
| AUTH_003 | Token invalid       | 401         | Re-authenticate      |
| AUTH_004 | Account locked      | 423         | Contact support      |

### Authorization Errors (AUTHZ)

| Code      | Message                  | HTTP Status | Recovery               |
| --------- | ------------------------ | ----------- | ---------------------- |
| AUTHZ_001 | Insufficient permissions | 403         | Request access         |
| AUTHZ_002 | Resource access denied   | 403         | Check permissions      |
| AUTHZ_003 | Action not allowed       | 403         | Review allowed actions |

### Validation Errors (VAL)

| Code    | Message                 | HTTP Status | Recovery                  |
| ------- | ----------------------- | ----------- | ------------------------- |
| VAL_001 | Required field missing  | 400         | Provide required field    |
| VAL_002 | Invalid format          | 400         | Check format requirements |
| VAL_003 | Value out of range      | 400         | Use valid range           |
| VAL_004 | File type not supported | 400         | Use supported format      |

### LLM Provider Errors (LLM)

| Code    | Message                 | HTTP Status | Recovery            |
| ------- | ----------------------- | ----------- | ------------------- |
| LLM_001 | Provider unavailable    | 503         | Retry with fallback |
| LLM_002 | Rate limit exceeded     | 429         | Wait and retry      |
| LLM_003 | Token limit exceeded    | 400         | Reduce prompt size  |
| LLM_004 | Invalid model specified | 400         | Use available model |
| LLM_005 | Response timeout        | 504         | Retry request       |

### System Errors (SYS)

| Code    | Message               | HTTP Status | Recovery           |
| ------- | --------------------- | ----------- | ------------------ |
| SYS_001 | Internal server error | 500         | Retry later        |
| SYS_002 | Database unavailable  | 503         | Contact support    |
| SYS_003 | Service overloaded    | 503         | Retry with backoff |
| SYS_004 | Configuration error   | 500         | Contact support    |

### Network Errors (NET)

| Code    | Message               | HTTP Status | Recovery           |
| ------- | --------------------- | ----------- | ------------------ |
| NET_001 | Connection timeout    | 504         | Check connection   |
| NET_002 | DNS resolution failed | 502         | Check network      |
| NET_003 | SSL certificate error | 495         | Verify certificate |
