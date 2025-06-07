# Dependency Index

This document tracks all dependencies in the PROJECT. All dependencies must be registered here.

## External Dependencies

| Dependency | Version | Added By | Date Added | Justification | Actions Using |
|------------|---------|----------|------------|---------------|---------------|
| email-validator | >=2.2.0,<3.0.0 | | 2025-06-06 | Required by Pydantic network validators | system-wide-cleanup-and-audit |
| prometheus-client | >=0.20.0,<1.0.0 | | 2025-06-06 | Prometheus metrics collection in metrics module | system-wide-cleanup-and-audit |
| requests | >=2.26.0,<3.0.0 | | 2025-06-06 | HTTP client in services (e.g., pricing_updater) | system-wide-cleanup-and-audit |
| psutil | >=5.9.0,<6.0.0 | | 2025-06-06 | System metrics fallback stub in HealthService and metrics collection | system-wide-cleanup-and-audit |
| google-generativeai | >=0.3.0 | | 2025-06-04 | Required for Google Gemini API integration in debug orchestrator | orchestration-deep-audit |
| openai | >=1.0.0 | | 2025-06-04 | Required for OpenAI API integration in debug orchestrator | orchestration-deep-audit |
| anthropic | >=0.18.0 | | 2025-06-04 | Required for Claude API integration in debug orchestrator | orchestration-deep-audit |
| *None yet* | | | | | |

## Internal Dependencies

| Dependency Action | Dependent Action | Type | Date Added | Description |
|-------------------|------------------|------|------------|-------------|
| *None yet* | | | | |

---
*Last Updated: 2025-06-06*
