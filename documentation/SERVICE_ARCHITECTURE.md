# UltraAI Service Architecture

## Overview
UltraAI is deployed as a monolithic application with logical service separations. All services run within a single Render web service.

## Core Services (Essential)

### 1. **Orchestration Service** (`orchestration_service.py`)
- **Purpose**: Coordinates multi-model LLM analysis
- **Dependencies**: LLM Adapters, Health Service, Cache Service
- **Critical**: YES - This is the heart of UltraAI

### 2. **LLM Adapters** (`llm_adapters.py`)
- **Purpose**: Unified interface for OpenAI, Anthropic, Google, HuggingFace
- **Dependencies**: API keys, HTTP client
- **Critical**: YES - Required for model communication

### 3. **Health Service** (`health_service.py`)
- **Purpose**: Monitors model availability and system health
- **Dependencies**: Provider Health Manager, Model Health Cache
- **Critical**: YES - Ensures system reliability

### 4. **Cache Service** (`cache_service.py`)
- **Purpose**: Redis caching with local memory fallback
- **Dependencies**: Redis (optional), Memory cache
- **Critical**: YES - Improves performance

### 5. **Auth Service** (`auth_service.py`)
- **Purpose**: JWT authentication and user management
- **Dependencies**: Database, JWT utils
- **Critical**: YES - Secures the application

## Supporting Services (Important)

### 6. **Model Registry** (`model_registry.py`)
- **Purpose**: Tracks available models and capabilities
- **Dependencies**: Provider configurations
- **Important**: Enables dynamic model discovery

### 7. **Output Formatter** (`output_formatter.py`)
- **Purpose**: Formats orchestration results
- **Dependencies**: None
- **Important**: Standardizes responses

### 8. **Recovery Service** (`recovery_service.py`)
- **Purpose**: Handles failures and retries
- **Dependencies**: Recovery strategies
- **Important**: Improves reliability

### 9. **Rate Limiter** (`rate_limiter.py`)
- **Purpose**: Prevents API abuse
- **Dependencies**: Redis/Memory cache
- **Important**: Protects resources

## Services to Disable (Financial Layer)

### ❌ Transaction Service (`transaction_service.py`, `transaction_service_db.py`)
- **Status**: DISABLE - Not needed for core functionality
- **Impact**: Remove billing/payment features

### ❌ Pricing Services (`pricing_service.py`, `pricing_integration.py`, etc.)
- **Status**: DISABLE - Not needed for core functionality
- **Impact**: Remove cost calculations

### ❌ Billing/Budget Interfaces (`interfaces/billing_service_interface.py`, etc.)
- **Status**: DISABLE - Not needed for core functionality
- **Impact**: Remove financial tracking

## Deployment Structure

```
Render Services:
├── ultrai-core (web)
│   ├── Backend (FastAPI)
│   │   ├── Core Services
│   │   ├── API Routes
│   │   └── Middleware
│   └── Frontend (Static files)
├── ultrai-db (PostgreSQL)
└── ultrai-redis (Redis cache)
```

## Service Dependencies

```
orchestration_service
├── llm_adapters
│   └── provider_health_manager
├── health_service
│   └── model_health_cache
├── cache_service
├── output_formatter
└── recovery_service
    └── recovery_strategies
```

## Simplification Plan

1. **Remove Financial Services**
   - Comment out transaction routes
   - Disable pricing calculations
   - Remove billing middleware

2. **Focus on Core Flow**
   - User → Auth → Orchestration → LLMs → Response
   - No cost tracking or billing

3. **Minimal Database Usage**
   - Users table (auth only)
   - Remove transaction tables
   - Keep analysis history (optional)

## Environment Variables (Simplified)

### Required:
- `JWT_SECRET` - Authentication
- `OPENAI_API_KEY` - At least 2 LLM keys
- `ANTHROPIC_API_KEY` - For multi-model

### Optional:
- `REDIS_URL` - Caching
- `DATABASE_URL` - User management
- `ENABLE_PRICING=false` - Disable pricing
- `ENABLE_BILLING=false` - Disable billing