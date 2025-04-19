# Backend Modularization Plan

## Current Issues

- `main.py` is 66KB and 1,834 lines long
- Contains multiple concerns: models, routes, services, utility functions
- Difficult to maintain and extend

## Proposed Structure

```
backend/
├── api/
│   ├── __init__.py              # Makes directory a package
│   ├── routes/
│   │   ├── __init__.py          # Aggregates and exports all routes
│   │   ├── analyze.py           # Analysis-related endpoints
│   │   ├── documents.py         # Document processing endpoints
│   │   ├── health.py            # Health check endpoints
│   │   ├── metrics.py           # System metrics endpoints
│   │   ├── pricing.py           # Pricing-related endpoints
│   │   └── users.py             # User account endpoints
│   └── middleware/
│       ├── __init__.py
│       ├── error_handling.py    # Error handling middleware
│       └── cors.py              # CORS middleware
├── models/
│   ├── __init__.py
│   ├── document.py              # Document-related models
│   ├── analysis.py              # Analysis-related models
│   ├── pricing.py               # Pricing-related models
│   └── user.py                  # User-related models
├── services/
│   ├── __init__.py
│   ├── document_processor.py    # Document processing service
│   ├── llm_service.py           # LLM orchestration service
│   ├── pricing_service.py       # Pricing calculation service
│   └── metrics_service.py       # System metrics collection
├── utils/
│   ├── __init__.py
│   ├── caching.py               # Caching utilities
│   ├── file_utils.py            # File handling utilities
│   └── metrics_utils.py         # Metrics calculation utilities
└── main.py                      # Much smaller main file
```

## Extraction Plan

### 1. Models

Extract all Pydantic models into separate files:

- Move `DocumentChunk`, `ProcessedDocument`, `DocumentUploadResponse` to `models/document.py`
- Move `TokenEstimateRequest` to `models/analysis.py`
- Move `PricingToggleRequest`, `UserAccountRequest`, `AddFundsRequest` to `models/pricing.py`

### 2. Routes

Extract route handlers to their own modules:

- Move `/api/analyze` endpoints to `api/routes/analyze.py`
- Move `/api/upload-files`, `/api/documents/*` endpoints to `api/routes/documents.py`
- Move `/health`, `/api/health`, `/api/system/health` to `api/routes/health.py`
- Move `/api/metrics*` endpoints to `api/routes/metrics.py`
- Move pricing-related endpoints to `api/routes/pricing.py`
- Move user account endpoints to `api/routes/users.py`

### 3. Services

Move service classes to their respective files:

- Move `UltraDocumentsOptimized` to `services/document_processor.py`
- Move `MockLLMService` to `services/llm_service.py`
- Move `MockPricingIntegration` to `services/pricing_service.py`
- Move metrics tracking code to `services/metrics_service.py`

### 4. Utilities

Extract utility functions:

- Move caching functions to `utils/caching.py`
- Move file operations to `utils/file_utils.py`
- Move metrics calculations to `utils/metrics_utils.py`

### 5. Main App

Refactor `main.py` to:

1. Import and initialize components
2. Register routes from route modules
3. Set up middleware
4. Configure app-wide settings

## Implementation Strategy

1. **Create directory structure** first
2. **Extract models** (least dependent components)
3. **Extract utility functions** (generally self-contained)
4. **Extract services** (depend on models and utils)
5. **Extract route handlers** (depend on all the above)
6. **Refactor main.py** to use new modular components

## Testing Strategy

- After each extraction, run the app to ensure functionality
- Create simple test cases for each new module
- Do final integration test with complete refactored structure

## Timeline Estimate

- Models extraction: 1 day
- Utils extraction: 1 day
- Services extraction: 2 days
- Routes extraction: 2-3 days
- Main.py refactoring: 1 day
- Testing & bug fixes: 2 days

Total estimated time: 9-10 days
