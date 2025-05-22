# Fallback Mechanisms Implementation

This document details the fallback mechanisms implemented as part of the SystemResilienceImplementation action.

## Overview

Fallback mechanisms allow the system to continue functioning when primary services or components fail. The Ultra system implements various fallback strategies to ensure continuity of service during component failures.

## Types of Fallback Mechanisms

### 1. LLM Provider Fallbacks

When a primary LLM provider (e.g., OpenAI) is unavailable, the system automatically falls back to alternative providers.

#### Implementation Details

```python
class LLMProviderFallback:
    """Manages fallbacks between LLM providers."""

    def __init__(self, primary_provider, fallback_providers=None):
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or []
        self.model_mapping = ModelCapabilityMapper()
        self.metrics = FallbackMetrics("llm_provider")

    async def execute_with_fallback(self, prompt, model, **kwargs):
        """Execute request with fallback support."""
        # Try primary provider first
        try:
            return await self._execute_provider(
                self.primary_provider, prompt, model, **kwargs
            )
        except (ServiceUnavailableException, TimeoutException, CircuitOpenException) as e:
            logger.warning(f"Primary provider {self.primary_provider.name} failed: {e}")
            self.metrics.record_primary_failure(self.primary_provider.name, type(e).__name__)

            # Try fallback providers in order
            for provider in self.fallback_providers:
                try:
                    # Map model to equivalent in fallback provider
                    fallback_model = self.model_mapping.map_model(
                        self.primary_provider.name, model, provider.name
                    )

                    if not fallback_model:
                        logger.warning(
                            f"No equivalent model found in {provider.name} "
                            f"for {self.primary_provider.name}/{model}"
                        )
                        continue

                    logger.info(
                        f"Trying fallback provider {provider.name} "
                        f"with model {fallback_model}"
                    )

                    # Execute with fallback provider
                    result = await self._execute_provider(
                        provider, prompt, fallback_model, **kwargs
                    )

                    # Record successful fallback
                    self.metrics.record_fallback_success(
                        self.primary_provider.name, provider.name
                    )

                    # Add fallback metadata
                    if isinstance(result, dict):
                        result["fallback_provider"] = provider.name
                        result["fallback_model"] = fallback_model
                        result["original_provider"] = self.primary_provider.name
                        result["original_model"] = model

                    return result
                except Exception as e:
                    logger.warning(f"Fallback provider {provider.name} failed: {e}")
                    self.metrics.record_fallback_failure(
                        self.primary_provider.name, provider.name, type(e).__name__
                    )

            # If all fallbacks fail, raise the original exception
            raise AllFallbacksFailedException(
                f"All providers failed for request. Original error: {e}"
            )

    async def _execute_provider(self, provider, prompt, model, **kwargs):
        """Execute request with a specific provider."""
        start_time = time.time()
        try:
            result = await provider.generate(prompt, model, **kwargs)
            execution_time = time.time() - start_time
            self.metrics.record_execution_time(provider.name, execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_execution_time(provider.name, execution_time)
            self.metrics.record_provider_error(provider.name, type(e).__name__)
            raise
```

#### Model Capability Mapping

For effective fallbacks, the system maps models between providers based on capabilities:

```python
class ModelCapabilityMapper:
    """Maps models between providers based on capabilities."""

    def __init__(self):
        self.model_capabilities = {
            "openai": {
                "gpt-4o": ["summarization", "code_generation", "complex_reasoning"],
                "gpt-4": ["summarization", "code_generation", "complex_reasoning"],
                "gpt-3.5-turbo": ["summarization", "simple_reasoning"],
            },
            "anthropic": {
                "claude-3-opus": ["summarization", "code_generation", "complex_reasoning"],
                "claude-3-sonnet": ["summarization", "code_generation", "complex_reasoning"],
                "claude-3-haiku": ["summarization", "simple_reasoning"],
            },
            "google": {
                "gemini-1.5-pro": ["summarization", "code_generation", "complex_reasoning"],
                "gemini-1.5-flash": ["summarization", "simple_reasoning"],
            },
        }

        # Direct model mappings for known equivalents
        self.direct_mappings = {
            "openai": {
                "gpt-4o": {"anthropic": "claude-3-opus", "google": "gemini-1.5-pro"},
                "gpt-4": {"anthropic": "claude-3-opus", "google": "gemini-1.5-pro"},
                "gpt-3.5-turbo": {"anthropic": "claude-3-haiku", "google": "gemini-1.5-flash"},
            },
            "anthropic": {
                "claude-3-opus": {"openai": "gpt-4o", "google": "gemini-1.5-pro"},
                "claude-3-sonnet": {"openai": "gpt-4", "google": "gemini-1.5-pro"},
                "claude-3-haiku": {"openai": "gpt-3.5-turbo", "google": "gemini-1.5-flash"},
            },
            "google": {
                "gemini-1.5-pro": {"openai": "gpt-4", "anthropic": "claude-3-opus"},
                "gemini-1.5-flash": {"openai": "gpt-3.5-turbo", "anthropic": "claude-3-haiku"},
            },
        }

    def map_model(self, source_provider, source_model, target_provider):
        """Map a model from source provider to target provider."""
        # Check direct mappings first
        if (source_provider in self.direct_mappings and
            source_model in self.direct_mappings[source_provider] and
            target_provider in self.direct_mappings[source_provider][source_model]):
            return self.direct_mappings[source_provider][source_model][target_provider]

        # If no direct mapping, try capability-based mapping
        if (source_provider in self.model_capabilities and
            source_model in self.model_capabilities[source_provider] and
            target_provider in self.model_capabilities):
            source_capabilities = self.model_capabilities[source_provider][source_model]

            # Find the model in target provider with most matching capabilities
            best_match = None
            best_match_score = 0

            for target_model, target_capabilities in self.model_capabilities[target_provider].items():
                match_score = sum(1 for cap in source_capabilities if cap in target_capabilities)
                if match_score > best_match_score:
                    best_match = target_model
                    best_match_score = match_score

            return best_match

        # No mapping found
        return None
```

#### Usage Example

```python
# Create LLM clients
openai_client = OpenAIAdapter(api_key=OPENAI_API_KEY)
anthropic_client = AnthropicAdapter(api_key=ANTHROPIC_API_KEY)
google_client = GoogleAdapter(api_key=GOOGLE_API_KEY)

# Create fallback handler
llm_fallback = LLMProviderFallback(
    primary_provider=openai_client,
    fallback_providers=[anthropic_client, google_client]
)

# Use fallback mechanism
try:
    result = await llm_fallback.execute_with_fallback(
        prompt="Explain quantum computing in simple terms",
        model="gpt-4o"
    )

    # Check if fallback was used
    if "fallback_provider" in result:
        logger.info(
            f"Used fallback provider {result['fallback_provider']} "
            f"with model {result['fallback_model']}"
        )
except AllFallbacksFailedException as e:
    logger.error(f"All LLM providers failed: {e}")
    # Implement graceful degradation for user
```

### 2. Database Fallbacks

The system implements database fallbacks to handle database connection issues.

#### Replica Fallback

```python
class DatabaseReplicaFallback:
    """Fallback to read replicas for database operations."""

    def __init__(self, primary_connection, read_replicas=None):
        self.primary_connection = primary_connection
        self.read_replicas = read_replicas or []
        self.metrics = FallbackMetrics("database")

    async def execute_query(self, query, params=None, read_only=False):
        """Execute a database query with fallback support."""
        if read_only and self.read_replicas:
            # For read-only queries, try replicas if primary fails
            try:
                return await self._execute_on_primary(query, params)
            except DatabaseConnectionException as e:
                logger.warning(f"Primary database connection failed: {e}")
                self.metrics.record_primary_failure("primary_db", type(e).__name__)

                # Try read replicas in order
                for i, replica in enumerate(self.read_replicas):
                    try:
                        logger.info(f"Trying read replica {i+1}")
                        result = await self._execute_on_replica(replica, query, params)
                        self.metrics.record_fallback_success("primary_db", f"replica_{i+1}")
                        return result
                    except Exception as e:
                        logger.warning(f"Read replica {i+1} failed: {e}")
                        self.metrics.record_fallback_failure(
                            "primary_db", f"replica_{i+1}", type(e).__name__
                        )

                # If all replicas fail, raise the original exception
                raise AllFallbacksFailedException(
                    f"All database connections failed for read query. Original error: {e}"
                )
        else:
            # For write queries, only use primary
            return await self._execute_on_primary(query, params)

    async def _execute_on_primary(self, query, params=None):
        """Execute query on primary database."""
        start_time = time.time()
        try:
            result = await self.primary_connection.execute(query, params)
            execution_time = time.time() - start_time
            self.metrics.record_execution_time("primary_db", execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_execution_time("primary_db", execution_time)
            self.metrics.record_provider_error("primary_db", type(e).__name__)
            raise

    async def _execute_on_replica(self, replica, query, params=None):
        """Execute query on a read replica."""
        start_time = time.time()
        try:
            result = await replica.execute(query, params)
            execution_time = time.time() - start_time
            self.metrics.record_execution_time(f"replica_{id(replica)}", execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_execution_time(f"replica_{id(replica)}", execution_time)
            self.metrics.record_provider_error(f"replica_{id(replica)}", type(e).__name__)
            raise
```

#### In-Memory Cache Fallback

```python
class DatabaseCacheFallback:
    """Fallback to cached data when database is unavailable."""

    def __init__(self, database_service, cache_service):
        self.database_service = database_service
        self.cache_service = cache_service
        self.metrics = FallbackMetrics("db_cache")

    async def get_entity(self, entity_type, entity_id):
        """Get an entity with cache fallback."""
        cache_key = f"{entity_type}:{entity_id}"

        try:
            # Try database first
            entity = await self.database_service.get_entity(entity_type, entity_id)

            # Update cache for future fallbacks
            await self.cache_service.put(cache_key, entity, "db_entities", ttl_seconds=3600)

            return entity
        except DatabaseException as e:
            logger.warning(f"Database error when fetching {entity_type}/{entity_id}: {e}")
            self.metrics.record_primary_failure("database", type(e).__name__)

            # Try to get from cache
            try:
                cached_entity = await self.cache_service.get(cache_key, "db_entities")
                if cached_entity:
                    logger.info(f"Retrieved {entity_type}/{entity_id} from cache")
                    self.metrics.record_fallback_success("database", "cache")

                    # Add fallback metadata
                    if isinstance(cached_entity, dict):
                        cached_entity["from_cache"] = True
                        cached_entity["cache_time"] = time.time()

                    return cached_entity
            except CacheException as cache_error:
                logger.warning(f"Cache also failed: {cache_error}")
                self.metrics.record_fallback_failure("database", "cache", type(cache_error).__name__)

            # Rethrow original error if cache fallback also fails
            raise DatabaseFallbackException(
                f"Could not retrieve {entity_type}/{entity_id} from database or cache"
            ) from e
```

### 3. Function-Level Fallbacks

Generic function-level fallbacks for any operation:

```python
class FunctionFallback:
    """Generic fallback mechanism for any function."""

    def __init__(self, fallback_function, should_fallback_on=None):
        self.fallback_function = fallback_function
        self.should_fallback_on = should_fallback_on or [Exception]
        self.metrics = FallbackMetrics("function")

    def __call__(self, func):
        """Decorator for adding fallback behavior to a function."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Try primary function
                result = await func(*args, **kwargs)
                self.metrics.record_primary_success(func.__name__)
                return result
            except Exception as e:
                # Check if we should fallback on this exception
                should_fallback = any(
                    isinstance(e, exc_type) for exc_type in self.should_fallback_on
                )

                if not should_fallback:
                    # Not a fallback-eligible exception
                    raise

                logger.warning(f"Function {func.__name__} failed, trying fallback: {e}")
                self.metrics.record_primary_failure(func.__name__, type(e).__name__)

                try:
                    # Try fallback function
                    result = await self.fallback_function(*args, **kwargs)
                    self.metrics.record_fallback_success(
                        func.__name__, self.fallback_function.__name__
                    )

                    # Add fallback metadata if possible
                    if isinstance(result, dict):
                        result["fallback_used"] = True
                        result["fallback_function"] = self.fallback_function.__name__
                        result["original_function"] = func.__name__
                        result["original_error"] = str(e)

                    return result
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback function {self.fallback_function.__name__} also failed: {fallback_error}"
                    )
                    self.metrics.record_fallback_failure(
                        func.__name__,
                        self.fallback_function.__name__,
                        type(fallback_error).__name__
                    )

                    # Raise a combined exception
                    raise FallbackFailedException(
                        f"Both primary function {func.__name__} and fallback function "
                        f"{self.fallback_function.__name__} failed. Original error: {e}. "
                        f"Fallback error: {fallback_error}"
                    )

        return wrapper
```

#### Usage Example

```python
# Define primary and fallback functions
async def get_user_data_from_api(user_id):
    # Get user data from API
    response = await api_client.get(f"/users/{user_id}")
    return response.json()

async def get_user_data_from_cache(user_id):
    # Get user data from cache
    cached_data = await cache.get(f"user:{user_id}")
    if cached_data:
        return cached_data
    else:
        return {"user_id": user_id, "name": "Unknown", "cached_fallback": True}

# Create fallback decorator
api_fallback = FunctionFallback(
    fallback_function=get_user_data_from_cache,
    should_fallback_on=[TimeoutException, ConnectionException]
)

# Apply fallback to primary function
@api_fallback
async def get_user_data(user_id):
    return await get_user_data_from_api(user_id)

# Use the function with fallback
try:
    user_data = await get_user_data("12345")
    if user_data.get("cached_fallback"):
        logger.info("Used cached fallback data")
except FallbackFailedException as e:
    logger.error(f"All user data retrieval methods failed: {e}")
```

### 4. Degraded Mode Fallbacks

The system implements degraded mode operation when critical services are unavailable:

```python
class DegradedModeFallback:
    """Provides fallback functionality in degraded mode."""

    def __init__(self, system_operation_mode):
        self.operation_mode = system_operation_mode
        self.fallback_functions = {}
        self.metrics = FallbackMetrics("degraded_mode")

    def register_fallback(self, feature_name, normal_function, degraded_function):
        """Register normal and degraded functions for a feature."""
        self.fallback_functions[feature_name] = {
            "normal": normal_function,
            "degraded": degraded_function,
        }

    async def execute_feature(self, feature_name, *args, **kwargs):
        """Execute a feature with degraded mode awareness."""
        if feature_name not in self.fallback_functions:
            raise ValueError(f"No functions registered for feature '{feature_name}'")

        current_mode = self.operation_mode.get_mode()

        if current_mode == SystemOperationMode.NORMAL:
            # Use normal function in normal mode
            try:
                result = await self.fallback_functions[feature_name]["normal"](*args, **kwargs)
                self.metrics.record_primary_success(feature_name)
                return result
            except Exception as e:
                logger.error(f"Normal function for {feature_name} failed: {e}")
                self.metrics.record_primary_failure(feature_name, type(e).__name__)

                # If normal function fails, try to use degraded function
                try:
                    logger.warning(f"Falling back to degraded function for {feature_name}")
                    result = await self.fallback_functions[feature_name]["degraded"](*args, **kwargs)
                    self.metrics.record_fallback_success(feature_name, f"{feature_name}_degraded")

                    # Mark system as degraded due to this feature
                    await self.operation_mode.mark_component_degraded(
                        feature_name,
                        f"Feature {feature_name} is operating in degraded mode due to error: {e}",
                        severity="medium"
                    )

                    # Add degraded metadata
                    if isinstance(result, dict):
                        result["degraded_mode"] = True
                        result["degraded_reason"] = str(e)

                    return result
                except Exception as degraded_error:
                    logger.critical(
                        f"Both normal and degraded functions for {feature_name} failed. "
                        f"Original error: {e}, Degraded error: {degraded_error}"
                    )
                    self.metrics.record_fallback_failure(
                        feature_name,
                        f"{feature_name}_degraded",
                        type(degraded_error).__name__
                    )

                    # Mark component as critically degraded
                    await self.operation_mode.mark_component_degraded(
                        feature_name,
                        f"Feature {feature_name} is critically degraded. Both normal and degraded "
                        f"functions failed. Original error: {e}, Degraded error: {degraded_error}",
                        severity="high"
                    )

                    raise FeatureUnavailableException(
                        f"Feature {feature_name} is currently unavailable"
                    )
        else:
            # In degraded or emergency mode, use degraded function directly
            try:
                logger.info(f"Using degraded function for {feature_name} in {current_mode} mode")
                result = await self.fallback_functions[feature_name]["degraded"](*args, **kwargs)

                # Add degraded metadata
                if isinstance(result, dict):
                    result["degraded_mode"] = True
                    result["system_mode"] = current_mode

                return result
            except Exception as e:
                logger.critical(f"Degraded function for {feature_name} failed in {current_mode} mode: {e}")

                raise FeatureUnavailableException(
                    f"Feature {feature_name} is currently unavailable in {current_mode} mode"
                )
```

#### Usage Example

```python
# Create operation mode manager
operation_mode = SystemOperationMode()

# Create degraded mode fallback manager
degraded_mode = DegradedModeFallback(operation_mode)

# Define normal and degraded functions for document analysis
async def analyze_document_normal(document_id, analysis_type):
    # Full analysis with all LLM providers
    document = await document_service.get_document(document_id)
    analysis = await orchestrator.analyze(document.content, analysis_type)
    return {
        "document_id": document_id,
        "analysis_type": analysis_type,
        "analysis": analysis,
        "confidence": analysis.get("confidence", 0.9),
    }

async def analyze_document_degraded(document_id, analysis_type):
    # Simplified analysis with cached models or simplified processing
    document = await document_service.get_document(document_id)

    # Use simpler analysis or cached results
    basic_analysis = {
        "summary": "Document analysis is limited in degraded mode",
        "key_points": ["Basic analysis only", "Limited functionality"],
        "confidence": 0.6,
    }

    return {
        "document_id": document_id,
        "analysis_type": analysis_type,
        "analysis": basic_analysis,
        "degraded_mode": True,
        "full_analysis_available": False,
    }

# Register functions with degraded mode manager
degraded_mode.register_fallback(
    "document_analysis",
    analyze_document_normal,
    analyze_document_degraded
)

# Use the feature with degraded mode awareness
try:
    analysis_result = await degraded_mode.execute_feature(
        "document_analysis",
        document_id="doc123",
        analysis_type="comprehensive"
    )

    if analysis_result.get("degraded_mode"):
        logger.info("Document was analyzed in degraded mode")
        # Inform user about limited functionality
except FeatureUnavailableException as e:
    logger.error(f"Document analysis is unavailable: {e}")
    # Show appropriate error to user
```

## Fallback Metrics and Monitoring

To track fallback effectiveness and performance, the system collects detailed metrics:

```python
class FallbackMetrics:
    """Metrics for fallback mechanisms."""

    def __init__(self, fallback_type="generic"):
        self.fallback_type = fallback_type
        self.primary_success_count = 0
        self.primary_failure_count = 0
        self.fallback_success_count = 0
        self.fallback_failure_count = 0
        self.execution_times = defaultdict(list)
        self.error_counts = defaultdict(lambda: defaultdict(int))
        self._lock = threading.RLock()

    def record_primary_success(self, primary_name):
        """Record successful primary execution."""
        with self._lock:
            self.primary_success_count += 1
            metrics.counter(
                f"fallback.{self.fallback_type}.primary.success",
                {"primary": primary_name}
            ).inc()

    def record_primary_failure(self, primary_name, error_type):
        """Record primary execution failure."""
        with self._lock:
            self.primary_failure_count += 1
            self.error_counts[primary_name][error_type] += 1
            metrics.counter(
                f"fallback.{self.fallback_type}.primary.failure",
                {"primary": primary_name, "error_type": error_type}
            ).inc()

    def record_fallback_success(self, primary_name, fallback_name):
        """Record successful fallback execution."""
        with self._lock:
            self.fallback_success_count += 1
            metrics.counter(
                f"fallback.{self.fallback_type}.fallback.success",
                {"primary": primary_name, "fallback": fallback_name}
            ).inc()

    def record_fallback_failure(self, primary_name, fallback_name, error_type):
        """Record fallback execution failure."""
        with self._lock:
            self.fallback_failure_count += 1
            self.error_counts[fallback_name][error_type] += 1
            metrics.counter(
                f"fallback.{self.fallback_type}.fallback.failure",
                {"primary": primary_name, "fallback": fallback_name, "error_type": error_type}
            ).inc()

    def record_execution_time(self, component_name, execution_time):
        """Record execution time for a component."""
        with self._lock:
            self.execution_times[component_name].append(execution_time)
            metrics.histogram(
                f"fallback.{self.fallback_type}.execution_time",
                {"component": component_name}
            ).observe(execution_time)

    def record_provider_error(self, provider_name, error_type):
        """Record provider-specific error."""
        with self._lock:
            self.error_counts[provider_name][error_type] += 1
            metrics.counter(
                f"fallback.{self.fallback_type}.provider.error",
                {"provider": provider_name, "error_type": error_type}
            ).inc()

    def get_metrics(self):
        """Get all metrics as a dictionary."""
        with self._lock:
            return {
                "type": self.fallback_type,
                "primary_success_count": self.primary_success_count,
                "primary_failure_count": self.primary_failure_count,
                "fallback_success_count": self.fallback_success_count,
                "fallback_failure_count": self.fallback_failure_count,
                "fallback_success_rate": (
                    self.fallback_success_count /
                    (self.fallback_success_count + self.fallback_failure_count)
                    if (self.fallback_success_count + self.fallback_failure_count) > 0
                    else 0
                ),
                "primary_failure_rate": (
                    self.primary_failure_count /
                    (self.primary_success_count + self.primary_failure_count)
                    if (self.primary_success_count + self.primary_failure_count) > 0
                    else 0
                ),
                "execution_times": {
                    component: {
                        "min": min(times) if times else None,
                        "max": max(times) if times else None,
                        "avg": sum(times) / len(times) if times else None,
                        "p50": np.percentile(times, 50) if times else None,
                        "p95": np.percentile(times, 95) if times else None,
                        "p99": np.percentile(times, 99) if times else None,
                    }
                    for component, times in self.execution_times.items()
                },
                "error_counts": dict(self.error_counts),
            }
```

## Integration with Health Checks

Fallback mechanisms integrate with the health check system to report their status:

```python
class FallbackHealthCheck(HealthCheck):
    """Health check for fallback mechanisms."""

    def __init__(self, fallback_manager, fallback_type):
        super().__init__(f"fallback_{fallback_type}", "fallback")
        self.fallback_manager = fallback_manager
        self.fallback_type = fallback_type

    async def check_health(self):
        """Check the health of the fallback mechanism."""
        try:
            metrics = self.fallback_manager.metrics.get_metrics()

            # Determine status based on metrics
            status = "ok"
            message = f"Fallback mechanism {self.fallback_type} is healthy"

            # If fallback success rate is low, mark as degraded
            fallback_success_rate = metrics.get("fallback_success_rate", 1.0)
            if fallback_success_rate < 0.5:
                status = "degraded"
                message = f"Fallback mechanism {self.fallback_type} has low success rate ({fallback_success_rate:.2f})"

            # If primary failure rate is high, mark as degraded
            primary_failure_rate = metrics.get("primary_failure_rate", 0.0)
            if primary_failure_rate > 0.8:
                status = "degraded"
                message = f"Primary components for {self.fallback_type} have high failure rate ({primary_failure_rate:.2f})"

            return HealthStatus(
                status=status,
                message=message,
                details={
                    "metrics": metrics,
                }
            )
        except Exception as e:
            return HealthStatus(
                status="critical",
                message=f"Error checking fallback health: {e}",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
```

## Conclusion

The fallback mechanisms implemented in the Ultra system provide robust resilience against component failures. By automatically switching to alternative providers, using cached data, and implementing degraded mode operation, the system can continue functioning effectively even when primary components fail. The comprehensive metrics collection and health check integration enable monitoring and continuous improvement of fallback effectiveness.
