# Resilience Integration Examples

This document provides examples of how to integrate and use the resilience components in your application code. These components were implemented as part of the SystemResilienceImplementation action to improve the overall reliability, stability, and fault tolerance of the Ultra system.

## Table of Contents

1. [LLM Client Integration](#llm-client-integration)
2. [Distributed Cache Integration](#distributed-cache-integration)
3. [Persistent Request Queue Integration](#persistent-request-queue-integration)
4. [System Operation Mode Integration](#system-operation-mode-integration)
5. [Complete Integration Example](#complete-integration-example)

## LLM Client Integration

The `ResilientLLMClient` provides built-in resilience features for interacting with LLM providers. Here's how to integrate it into your service:

```python
from backend.resilience.llm_client import ResilientLLMClient
from backend.utils.domain_exceptions import LLMException

class AnthropicService:
    """Service for interacting with Anthropic Claude models."""

    def __init__(self, api_key: str):
        # Create a resilient client with custom configuration
        self.client = ResilientLLMClient(
            provider="anthropic",
            api_key=api_key,
            timeout=30,  # 30 seconds timeout
            retry_attempts=3,
            backoff_factor=1.5,
            jitter=0.2,
            circuit_breaker_threshold=5,
            circuit_breaker_recovery_time=60,
            rate_limit=100  # requests per minute
        )

    async def generate_text(self, prompt: str, max_tokens: int = 1000):
        """Generate text using Claude with built-in resilience."""
        try:
            response = await self.client.completion(
                prompt=prompt,
                max_tokens=max_tokens,
                model="claude-3-opus-20240229"
            )
            return response.text
        except LLMException as e:
            # The client already handled retries, circuit breaking, etc.
            # This catch is for truly unrecoverable errors
            logger.error(f"Failed to generate text: {e}")
            return None
```

## Distributed Cache Integration

The `DistributedCache` provides multi-level caching capabilities. Here's how to integrate it:

```python
from backend.resilience.cache import DistributedCache
import hashlib

class DocumentService:
    """Service for handling document operations with caching."""

    def __init__(self):
        # Create a multi-level cache
        self.cache = DistributedCache(
            memory_cache_size=1000,  # Items to store in memory
            disk_cache_dir="/tmp/ultra_cache",  # Local disk cache
            redis_url="redis://localhost:6379/0",  # Redis for distributed caching
            redis_prefix="docs:"  # Prefix for Redis keys
        )

    async def get_document(self, document_id: str):
        """Get a document with caching support."""
        # Create a cache key
        cache_key = f"document:{document_id}"

        # Try to get from cache first
        cached_doc = await self.cache.get(cache_key)
        if cached_doc:
            return cached_doc

        # If not in cache, fetch from database
        document = await self.database.fetch_document(document_id)
        if document:
            # Store in cache for future requests
            await self.cache.set(
                key=cache_key,
                value=document,
                ttl=3600  # Cache for 1 hour
            )

        return document

    async def invalidate_document_cache(self, document_id: str):
        """Invalidate the cache when a document is updated."""
        cache_key = f"document:{document_id}"
        await self.cache.delete(cache_key)
```

## Persistent Request Queue Integration

The `PersistentRequestQueue` ensures that requests are processed even after system restarts. Here's how to integrate it:

```python
from backend.resilience.queue import PersistentRequestQueue
import json
import uuid

class DocumentProcessingService:
    """Service for handling document processing with persistent queue."""

    def __init__(self):
        # Create a persistent queue
        self.queue = PersistentRequestQueue(
            queue_name="document_processing",
            storage_path="/var/ultra/queues",
            max_workers=5,  # Number of worker processes
            max_retries=3,  # Retries per job
            backoff_factor=2  # Exponential backoff
        )

        # Register handlers for different job types
        self.queue.register_handler("analyze_document", self._handle_document_analysis)
        self.queue.register_handler("index_document", self._handle_document_indexing)

        # Start the queue workers
        self.queue.start()

    async def submit_document_for_analysis(self, document_id: str, options: dict):
        """Queue a document for analysis."""
        job_id = str(uuid.uuid4())

        # Create a job with the necessary data
        job_data = {
            "document_id": document_id,
            "options": options,
            "user_id": get_current_user_id()
        }

        # Submit to the persistent queue
        await self.queue.enqueue(
            job_type="analyze_document",
            job_id=job_id,
            job_data=job_data,
            priority=1  # Higher priority
        )

        return job_id

    async def _handle_document_analysis(self, job_data: dict):
        """Handler for document analysis jobs."""
        document_id = job_data["document_id"]
        options = job_data["options"]

        # Perform the actual analysis
        try:
            result = await self.analyzer.analyze_document(document_id, options)
            await self.database.store_analysis_result(document_id, result)
            return True
        except Exception as e:
            logger.error(f"Failed to analyze document {document_id}: {e}")
            # Return False to indicate job failure, queue will retry based on configuration
            return False
```

## System Operation Mode Integration

The `SystemOperationMode` manager tracks the system's health and enables graceful degradation. Here's how to integrate it:

```python
from backend.resilience.operation_mode import (
    SystemOperationMode,
    OperationModeType,
    DegradationReason,
    FeatureFlag
)

# Create a global operation mode manager
operation_mode = SystemOperationMode()

# Define feature flags
ENABLE_DOCUMENT_ANALYSIS = FeatureFlag(
    name="enable_document_analysis",
    description="Enable document analysis features",
    default_value=True,
    mode_values={
        OperationModeType.EMERGENCY: False,  # Disable in emergency mode
        OperationModeType.MAINTENANCE: False  # Disable during maintenance
    }
)

ENABLE_ADVANCED_LLM_MODELS = FeatureFlag(
    name="enable_advanced_llm_models",
    description="Enable GPU-intensive advanced LLM models",
    default_value=True,
    mode_values={
        OperationModeType.DEGRADED: False,  # Use simpler models in degraded mode
        OperationModeType.EMERGENCY: False,  # Disable in emergency mode
        OperationModeType.MAINTENANCE: False  # Disable during maintenance
    }
)

# Register the feature flags
operation_mode.register_feature_flag(ENABLE_DOCUMENT_ANALYSIS)
operation_mode.register_feature_flag(ENABLE_ADVANCED_LLM_MODELS)

# API endpoint with feature flag check
@app.post("/api/analyze")
async def analyze_document(request: AnalysisRequest):
    # Check if the feature is enabled
    if not operation_mode.is_feature_enabled(ENABLE_DOCUMENT_ANALYSIS):
        raise ServiceUnavailableException(
            "Document analysis is currently unavailable due to system maintenance."
        )

    # Determine which models to use based on feature flags
    if operation_mode.is_feature_enabled(ENABLE_ADVANCED_LLM_MODELS):
        llm_model = "claude-3-opus-20240229"
    else:
        llm_model = "claude-3-haiku-20240307"  # Fallback to a lighter model

    # Continue with the regular flow
    analysis_result = await document_service.analyze(
        request.document_id,
        model=llm_model
    )

    return {"status": "success", "result": analysis_result}

# Health check integration
@app.get("/api/health")
async def health_check():
    health_status = await health_service.check_all_systems()

    # Update operation mode based on health check
    if health_status.all_healthy:
        operation_mode.set_mode(OperationModeType.NORMAL)
    elif health_status.critical_errors:
        operation_mode.set_mode(
            OperationModeType.EMERGENCY,
            DegradationReason(
                component="health_check",
                description="Critical system components are failing",
                severity=3
            )
        )
    elif health_status.warnings:
        operation_mode.set_mode(
            OperationModeType.DEGRADED,
            DegradationReason(
                component="health_check",
                description="Some system components are degraded",
                severity=2
            )
        )

    return {
        "status": "ok" if health_status.all_healthy else "degraded",
        "operation_mode": operation_mode.current_mode.value,
        "components": health_status.component_status
    }
```

## Complete Integration Example

Here's a more complete example showing how to integrate all resilience components together in a service:

```python
from backend.resilience.llm_client import ResilientLLMClient
from backend.resilience.cache import DistributedCache
from backend.resilience.queue import PersistentRequestQueue
from backend.resilience.operation_mode import SystemOperationMode, OperationModeType, FeatureFlag
from backend.utils.domain_exceptions import LLMException, ServiceUnavailableException
import logging

logger = logging.getLogger(__name__)

class ResilientAnalysisService:
    """
    Analysis service with comprehensive resilience features.

    This service integrates all resilience components to provide a robust
    and fault-tolerant document analysis capability.
    """

    def __init__(
        self,
        anthropic_api_key: str,
        openai_api_key: str,
        operation_mode: SystemOperationMode
    ):
        # Initialize resilient LLM clients
        self.anthropic_client = ResilientLLMClient(
            provider="anthropic",
            api_key=anthropic_api_key,
            timeout=60,
            retry_attempts=3
        )

        self.openai_client = ResilientLLMClient(
            provider="openai",
            api_key=openai_api_key,
            timeout=30,
            retry_attempts=2
        )

        # Initialize distributed cache
        self.cache = DistributedCache(
            memory_cache_size=5000,
            disk_cache_dir="/var/ultra/cache",
            redis_url="redis://localhost:6379/0"
        )

        # Initialize persistent queue
        self.queue = PersistentRequestQueue(
            queue_name="analysis_queue",
            storage_path="/var/ultra/queues",
            max_workers=10,
            max_retries=3
        )

        # Register queue handlers
        self.queue.register_handler("analyze_document", self._handle_analysis_job)

        # Store operation mode reference
        self.operation_mode = operation_mode

        # Start queue processing
        self.queue.start()

    async def analyze_document(self, document_id: str, options: dict):
        """
        Queue a document for analysis with resilience features.

        This function demonstrates the integration of:
        - Operation mode check to determine if the feature is available
        - Caching to avoid redundant processing
        - Persistent queue for reliable processing
        """
        # Check if analysis is enabled based on operation mode
        if not self.operation_mode.is_feature_enabled("enable_document_analysis"):
            raise ServiceUnavailableException(
                "Document analysis is currently unavailable."
            )

        # Try to get from cache first
        cache_key = f"analysis:{document_id}:{hash(frozenset(options.items()))}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached analysis for document {document_id}")
            return cached_result

        # Queue the analysis job
        job_id = await self.queue.enqueue(
            job_type="analyze_document",
            job_data={
                "document_id": document_id,
                "options": options,
                "cache_key": cache_key
            }
        )

        return {"status": "queued", "job_id": job_id}

    async def get_analysis_status(self, job_id: str):
        """Get the status of a queued analysis job."""
        return await self.queue.get_job_status(job_id)

    async def _handle_analysis_job(self, job_data: dict):
        """
        Handler for document analysis jobs.

        This handler demonstrates:
        - Selection of LLM provider based on availability
        - Fallback between providers
        - Caching of results
        - Adaptive operation based on system mode
        """
        document_id = job_data["document_id"]
        options = job_data["options"]
        cache_key = job_data["cache_key"]

        # Determine which LLM to use based on operation mode
        use_advanced_models = self.operation_mode.is_feature_enabled("enable_advanced_llm_models")

        # Get document content
        document = await self.document_service.get_document(document_id)
        if not document:
            logger.error(f"Document {document_id} not found")
            return False

        # Prepare prompt
        prompt = self._prepare_analysis_prompt(document, options)

        # Try primary provider with fallback
        try:
            # First try Anthropic
            model = "claude-3-opus-20240229" if use_advanced_models else "claude-3-haiku-20240307"
            result = await self.anthropic_client.completion(
                prompt=prompt,
                max_tokens=options.get("max_tokens", 1000),
                model=model
            )
            analysis_text = result.text
        except LLMException as e:
            logger.warning(f"Anthropic request failed, falling back to OpenAI: {e}")
            try:
                # Fallback to OpenAI
                model = "gpt-4" if use_advanced_models else "gpt-3.5-turbo"
                result = await self.openai_client.completion(
                    prompt=prompt,
                    max_tokens=options.get("max_tokens", 1000),
                    model=model
                )
                analysis_text = result.text
            except LLMException as fallback_error:
                logger.error(f"Both providers failed: {fallback_error}")
                return False

        # Process the result
        analysis_result = self._process_analysis_result(analysis_text, options)

        # Store the result
        await self.document_service.store_analysis(document_id, analysis_result)

        # Cache the result
        await self.cache.set(
            key=cache_key,
            value=analysis_result,
            ttl=3600 * 24  # Cache for 24 hours
        )

        return True

    def _prepare_analysis_prompt(self, document, options):
        """Prepare the analysis prompt based on document and options."""
        # Implementation details...
        return prompt

    def _process_analysis_result(self, analysis_text, options):
        """Process the raw analysis text into a structured result."""
        # Implementation details...
        return processed_result
```

This example demonstrates how to:

1. Initialize all resilience components with appropriate configuration
2. Use operation mode to control feature availability
3. Implement caching to improve performance and reduce load
4. Use a persistent queue for reliable asynchronous processing
5. Implement provider fallback for LLM requests
6. Adapt behavior based on system health and operation mode

By integrating these resilience components, services become more robust against failures and can operate more reliably in less-than-ideal conditions.
