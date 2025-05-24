# Dependency Index

This document tracks all dependencies in the PROJECT. All dependencies must be registered here.

## External Dependencies

| Dependency | Version | Added By | Date Added | Justification | Actions Using |
|------------|---------|----------|------------|---------------|---------------|
| fastapi | 0.115.12 | | 2025-05-24 | SECURITY UPDATE: Core framework for sophisticated orchestration backend - updated from 0.109.0 to resolve PYSEC-2024-38 vulnerability | security-vulnerability-fix |
| python-jose | 3.4.0 | | 2025-05-24 | SECURITY UPDATE: JWT authentication library - updated from 3.3.0 to resolve PYSEC-2024-232, PYSEC-2024-233 vulnerabilities | security-vulnerability-fix |
| aiohttp | 3.10.11 | | 2025-05-24 | SECURITY UPDATE: Async HTTP client - updated from 3.9.1 to resolve multiple vulnerabilities (PYSEC-2024-24, PYSEC-2024-26, GHSA-7gpw-8wmc-pm8g, GHSA-5m98-qgg9-wh84, GHSA-8495-4g3g-x7pr) | security-vulnerability-fix |
| sse-starlette | 2.1.0 | | 2025-05-24 | SECURITY UPDATE: Server-Sent Events for real-time streaming - updated from 1.6.5 to resolve starlette dependency conflicts and enhance security | security-vulnerability-fix |
| vite | 6.3.5 | | 2025-05-24 | SECURITY UPDATE: Frontend build tool - updated from 5.1.0 to resolve esbuild moderate vulnerabilities (GHSA-67mh-4wv8-2f99) | security-vulnerability-fix |
| API_KEY_ENCRYPTION_KEY | env-var | | 2025-05-23 | Required for encrypting and securing API keys in sophisticated backend production environment | production-config-fix |
| SECRET_KEY | env-var | | 2025-05-23 | Required security environment variable for sophisticated backend authentication and session management | production-config-fix |
| bleach | 6.1.0 | | 2025-05-23 | Security layer for document processing and input sanitization in sophisticated Feather analysis workflows | ultrai-system-assessment |
| prometheus_client | 0.19.0 | | 2025-05-23 | Performance monitoring for sophisticated orchestration system quality evaluation and patent claim validation | ultrai-system-assessment |
| python-docx | 1.1.0 | | 2025-05-23 | Document processing for sophisticated analysis workflows supporting patent-protected document context integration | ultrai-system-assessment |
| PyPDF2 | 3.0.1 | | 2025-05-23 | Document processing capability for Feather analysis patterns with context integration | ultrai-system-assessment |
| backoff | 2.2.1 | | 2025-05-23 | Circuit breaker and retry logic for resilient multi-LLM orchestration patterns | ultrai-system-assessment |
| cachetools | 5.3.2 | | 2025-05-23 | Caching layer for enhanced orchestrator performance and quality evaluation optimization | ultrai-system-assessment |
| beautifulsoup4 | 4.12.2 | | 2025-05-23 | Required for document processing and HTML parsing in sophisticated orchestration workflows | ultrai-system-assessment |
| *None yet* | | | | | |

## Internal Dependencies

| Dependency Action | Dependent Action | Type | Date Added | Description |
|-------------------|------------------|------|------------|-------------|
| *None yet* | | | | |

---
*Last Updated: 2025-05-24*
