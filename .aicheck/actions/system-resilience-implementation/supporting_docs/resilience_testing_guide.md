# Resilience Testing Guide

This guide outlines approaches for testing the resilience features of the Ultra system.

## Testing Objectives

The primary objectives of resilience testing are:

1. **Verify Functionality**: Ensure resilience mechanisms work as expected
2. **Identify Weaknesses**: Find potential failure points before production
3. **Measure Recovery**: Evaluate recovery time and effectiveness
4. **Test Degradation**: Verify graceful degradation under stress
5. **Validate User Experience**: Ensure users receive appropriate feedback

## Testing Approaches

### 1. Chaos Testing

Chaos testing deliberately introduces failures to verify the system's resilience:

#### Simulated Provider Failures

```python
class MockFailingLLMProvider:
    """Mock LLM provider that fails in specific ways for testing."""

    def __init__(self, failure_pattern="none"):
        self.failure_pattern = failure_pattern
        self.call_count = 0

    async def generate(self, prompt, model, **kwargs):
        """Generate text with simulated failures."""
        self.call_count += 1

        if self.failure_pattern == "always":
            raise ServiceUnavailableException("Provider unavailable")
        elif self.failure_pattern == "intermittent" and self.call_count % 3 == 0:
            raise ServiceUnavailableException("Provider unavailable")
        elif self.failure_pattern == "timeout":
            await asyncio.sleep(10)  # Force timeout
            return "This should never be reached"
        elif self.failure_pattern == "rate_limit" and self.call_count > 5:
            raise RateLimitException("Rate limit exceeded")

        return f"Response for: {prompt[:30]}..."
```

#### Network Failure Injection

```python
class NetworkFailureProxy:
    """Proxy that injects network failures for testing."""

    def __init__(self, target_service, failure_rate=0.2):
        self.target_service = target_service
        self.failure_rate = failure_rate

    async def call(self, method_name, *args, **kwargs):
        """Call target service with simulated network failures."""
        # Randomly fail based on failure rate
        if random.random() < self.failure_rate:
            failure_type = random.choice([
                "timeout", "connection_reset", "dns_failure", "partial_response"
            ])

            if failure_type == "timeout":
                await asyncio.sleep(5)
                raise TimeoutException("Request timed out")
            elif failure_type == "connection_reset":
                raise ConnectionResetException("Connection reset by peer")
            elif failure_type == "dns_failure":
                raise DNSResolutionException("Could not resolve hostname")
            elif failure_type == "partial_response":
                raise IncompleteResponseException("Received incomplete response")

        # Call actual service
        method = getattr(self.target_service, method_name)
        return await method(*args, **kwargs)
```

#### Database Failure Simulation

```python
class DatabaseFailureSimulator:
    """Simulates database failures for resilience testing."""

    def __init__(self, database_service):
        self.database_service = database_service
        self.original_methods = {}
        self.failure_modes = {}

    def enable_failure_mode(self, method_name, failure_type, duration_seconds=60):
        """Enable a specific failure mode for a database method."""
        self.failure_modes[method_name] = {
            "type": failure_type,
            "until": time.time() + duration_seconds,
        }

    def patch_method(self, method_name):
        """Patch a database method to inject failures."""
        original_method = getattr(self.database_service, method_name)
        self.original_methods[method_name] = original_method

        async def patched_method(*args, **kwargs):
            # Check if failure mode is active
            failure_mode = self.failure_modes.get(method_name)
            if failure_mode and time.time() < failure_mode["until"]:
                failure_type = failure_mode["type"]

                if failure_type == "timeout":
                    await asyncio.sleep(5)
                    raise TimeoutException("Database operation timed out")
                elif failure_type == "connection_lost":
                    raise ConnectionException("Database connection lost")
                elif failure_type == "constraint_violation":
                    raise ConstraintViolationException("Database constraint violation")
                elif failure_type == "deadlock":
                    raise DeadlockException("Database deadlock detected")

            # Call original method
            return await original_method(*args, **kwargs)

        setattr(self.database_service, method_name, patched_method)

    def restore_methods(self):
        """Restore original database methods."""
        for method_name, original_method in self.original_methods.items():
            setattr(self.database_service, method_name, original_method)
```

### 2. Load Testing

Load testing applies stress to identify resilience under heavy load:

#### Gradual Load Increase

```python
async def test_gradual_load_increase(client, max_concurrent=100, duration_seconds=60):
    """Test system behavior under gradually increasing load."""
    start_time = time.time()
    end_time = start_time + duration_seconds

    # Metrics
    requests_sent = 0
    successful_responses = 0
    failed_responses = 0
    response_times = []

    async def send_request():
        nonlocal requests_sent, successful_responses, failed_responses

        requests_sent += 1
        start = time.time()

        try:
            response = await client.analyze_document(
                document_id="test_document",
                analysis_type="summary",
                timeout=5.0
            )

            successful_responses += 1
            response_times.append(time.time() - start)
            return response
        except Exception as e:
            failed_responses += 1
            logger.error(f"Request failed: {e}")
            return None

    # Run test
    current_time = time.time()
    while current_time < end_time:
        # Calculate current concurrency based on elapsed time percentage
        elapsed_percent = (current_time - start_time) / duration_seconds
        current_concurrency = int(max_concurrent * elapsed_percent) + 1

        # Send batch of requests
        tasks = [send_request() for _ in range(current_concurrency)]
        await asyncio.gather(*tasks)

        # Brief pause to avoid overwhelming
        await asyncio.sleep(0.5)
        current_time = time.time()

    # Calculate metrics
    success_rate = successful_responses / requests_sent if requests_sent > 0 else 0
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    return {
        "requests_sent": requests_sent,
        "successful_responses": successful_responses,
        "failed_responses": failed_responses,
        "success_rate": success_rate,
        "avg_response_time": avg_response_time,
        "min_response_time": min(response_times) if response_times else None,
        "max_response_time": max(response_times) if response_times else None,
    }
```

#### Circuit Breaker Verification

```python
async def test_circuit_breaker_trip_under_load(client):
    """Test that circuit breakers trip appropriately under load."""
    # Create a failing service that will eventually trip the circuit breaker
    service = MockFailingLLMProvider(failure_pattern="intermittent")

    # Replace the real service with our mock
    original_service = client.llm_client
    client.llm_client = service

    try:
        # Send many requests to trigger circuit breaker
        results = {
            "success": 0,
            "failure": 0,
            "circuit_open": 0,
        }

        for _ in range(20):
            try:
                await client.generate_text("Test prompt")
                results["success"] += 1
            except CircuitOpenException:
                results["circuit_open"] += 1
            except Exception:
                results["failure"] += 1

        # Verify circuit breaker eventually opened
        assert results["circuit_open"] > 0, "Circuit breaker did not open"

        # Wait for reset timeout
        await asyncio.sleep(client.llm_client.circuit_breaker.reset_timeout + 0.1)

        # Verify circuit allows one request in half-open state
        try:
            await client.generate_text("Test after reset")
            has_reset = True
        except:
            has_reset = False

        assert has_reset, "Circuit did not reset after timeout"
    finally:
        # Restore original service
        client.llm_client = original_service
```

### 3. Degradation Testing

Degradation testing verifies the system's ability to function with limited resources:

#### Simulated Resource Constraints

```python
class ResourceConstrainer:
    """Constrains system resources for degradation testing."""

    def __init__(self):
        self.original_limits = {}

    def limit_memory(self, max_mb):
        """Limit available memory for testing."""
        import resource

        # Store original limit
        self.original_limits["memory"] = resource.getrlimit(resource.RLIMIT_AS)

        # Set new limit (convert MB to bytes)
        new_limit = max_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (new_limit, new_limit))

    def limit_cpu(self, max_cpu_seconds):
        """Limit available CPU time for testing."""
        import resource

        # Store original limit
        self.original_limits["cpu"] = resource.getrlimit(resource.RLIMIT_CPU)

        # Set new limit
        resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_seconds, max_cpu_seconds))

    def limit_file_descriptors(self, max_fds):
        """Limit available file descriptors for testing."""
        import resource

        # Store original limit
        self.original_limits["fds"] = resource.getrlimit(resource.RLIMIT_NOFILE)

        # Set new limit
        resource.setrlimit(resource.RLIMIT_NOFILE, (max_fds, max_fds))

    def restore_limits(self):
        """Restore original resource limits."""
        import resource

        if "memory" in self.original_limits:
            resource.setrlimit(resource.RLIMIT_AS, self.original_limits["memory"])

        if "cpu" in self.original_limits:
            resource.setrlimit(resource.RLIMIT_CPU, self.original_limits["cpu"])

        if "fds" in self.original_limits:
            resource.setrlimit(resource.RLIMIT_NOFILE, self.original_limits["fds"])
```

#### Degraded Mode Testing

```python
async def test_degraded_mode_operation(client):
    """Test that the system operates correctly in degraded mode."""
    # Put system in degraded mode
    await system_operation_mode.set_mode(
        SystemOperationMode.DEGRADED,
        "Testing degraded mode operation"
    )

    try:
        # Test core functionality still works
        response = await client.analyze_document(
            document_id="test_document",
            analysis_type="summary"
        )

        # Verify response is valid even in degraded mode
        assert response is not None
        assert "summary" in response

        # Verify advanced features are disabled
        advanced_response = await client.analyze_document(
            document_id="test_document",
            analysis_type="deep_analysis"
        )

        # Expect simplified response or specific error
        assert "degraded_mode" in advanced_response
        assert advanced_response.get("degraded_mode") is True
    finally:
        # Restore normal mode
        await system_operation_mode.set_mode(SystemOperationMode.NORMAL)
```

### 4. Recovery Testing

Recovery testing verifies the system's ability to recover from failures:

#### Database Recovery Test

```python
async def test_database_recovery(database_service):
    """Test database service recovery after connection failure."""
    # Simulate database connection failure
    db_simulator = DatabaseFailureSimulator(database_service)
    db_simulator.patch_method("execute_query")
    db_simulator.enable_failure_mode("execute_query", "connection_lost", duration_seconds=5)

    # Attempt database operations during failure
    failed_operations = 0
    successful_operations = 0

    start_time = time.time()
    end_time = start_time + 10  # Test for 10 seconds

    while time.time() < end_time:
        try:
            await database_service.execute_query("SELECT 1")
            successful_operations += 1
        except Exception:
            failed_operations += 1

        await asyncio.sleep(0.5)

    # Verify that operations eventually succeeded after failure mode ended
    assert successful_operations > 0, "No operations succeeded after recovery"

    # Restore original methods
    db_simulator.restore_methods()
```

#### Cache Recovery Test

```python
async def test_cache_recovery(cache_service):
    """Test cache service recovery after failure."""
    # Store some data in cache
    await cache_service.put("test_key", "test_value", ttl_seconds=60)

    # Verify data is retrievable
    assert await cache_service.get("test_key") == "test_value"

    # Simulate cache failure
    original_get = cache_service.get
    original_put = cache_service.put

    async def failing_get(*args, **kwargs):
        raise CacheException("Simulated cache failure")

    async def failing_put(*args, **kwargs):
        raise CacheException("Simulated cache failure")

    # Replace methods with failing versions
    cache_service.get = failing_get
    cache_service.put = failing_put

    # Verify system continues to work without cache
    try:
        user_service = UserService(cache_service=cache_service)
        user = await user_service.get_user(user_id="test_user")
        assert user is not None, "User service failed without cache"
    finally:
        # Restore original methods
        cache_service.get = original_get
        cache_service.put = original_put

    # Verify cache operation resumes after recovery
    await cache_service.put("recovery_key", "recovery_value", ttl_seconds=60)
    assert await cache_service.get("recovery_key") == "recovery_value"
```

### 5. End-to-End Resilience Testing

End-to-end testing verifies the entire system's resilience:

#### Simulated Provider Outage Scenario

```python
async def test_end_to_end_provider_outage():
    """Test end-to-end system behavior during provider outage."""
    # Start application with all providers available
    app = create_test_app()
    client = TestClient(app)

    # Verify system works normally
    response = client.post("/api/analyze", json={
        "text": "Test document for analysis",
        "analysis_type": "summary"
    })
    assert response.status_code == 200
    assert "result" in response.json()

    # Simulate OpenAI outage
    with mock.patch("src.adapters.openai_adapter.OpenAIAdapter.generate") as mock_generate:
        mock_generate.side_effect = ServiceUnavailableException("OpenAI is down")

        # Test system falls back to alternative provider
        response = client.post("/api/analyze", json={
            "text": "Test document during outage",
            "analysis_type": "summary"
        })

        # Verify request still succeeds with fallback
        assert response.status_code == 200
        assert "result" in response.json()
        assert "fallback_provider" in response.json()

        # Verify correct fallback provider was used
        assert response.json()["fallback_provider"] == "anthropic"
```

#### Full System Resilience Test

```python
async def test_full_system_resilience():
    """Comprehensive test of system resilience under multiple failure conditions."""
    # Start application
    app = create_test_app()
    client = TestClient(app)

    # Phase 1: Normal operation baseline
    normal_response = client.post("/api/analyze", json={
        "text": "Baseline test document",
        "analysis_type": "summary"
    })
    assert normal_response.status_code == 200

    # Phase 2: Database degradation
    with mock.patch("src.database.connection.execute_query") as mock_query:
        # Make database slow but functional
        async def slow_query(*args, **kwargs):
            await asyncio.sleep(1)
            return [{"id": 1, "name": "Test"}]

        mock_query.side_effect = slow_query

        # Test system with slow database
        slow_db_response = client.post("/api/analyze", json={
            "text": "Test with slow database",
            "analysis_type": "summary"
        })

        # Verify system still works but may be slower
        assert slow_db_response.status_code == 200

    # Phase 3: LLM provider failures
    with mock.patch("src.adapters.openai_adapter.OpenAIAdapter.generate") as mock_openai:
        mock_openai.side_effect = ServiceUnavailableException("OpenAI is down")

        with mock.patch("src.adapters.anthropic_adapter.AnthropicAdapter.generate") as mock_anthropic:
            # First make Anthropic slow
            async def slow_anthropic(*args, **kwargs):
                await asyncio.sleep(2)
                return "Slow response from Anthropic"

            mock_anthropic.side_effect = slow_anthropic

            # Test with primary provider down and secondary slow
            partial_outage_response = client.post("/api/analyze", json={
                "text": "Test during partial outage",
                "analysis_type": "summary"
            })

            # Should still work but be slower
            assert partial_outage_response.status_code == 200

            # Now make Anthropic fail too
            mock_anthropic.side_effect = ServiceUnavailableException("Anthropic is down")

            # Test with all providers down
            full_outage_response = client.post("/api/analyze", json={
                "text": "Test during full outage",
                "analysis_type": "summary"
            })

            # System should degrade gracefully
            assert full_outage_response.status_code in (200, 503)
            if full_outage_response.status_code == 200:
                assert full_outage_response.json()["degraded_mode"] is True

    # Phase 4: Recovery
    recovery_response = client.post("/api/analyze", json={
        "text": "Test after recovery",
        "analysis_type": "summary"
    })
    assert recovery_response.status_code == 200
```

## Automated Resilience Testing

Automated resilience testing can be implemented using a test framework:

```python
class ResilienceTestSuite:
    """Comprehensive resilience test suite for the Ultra system."""

    def __init__(self, app, test_duration_seconds=60):
        self.app = app
        self.client = TestClient(app)
        self.test_duration = test_duration_seconds
        self.results = {}

    async def run_all_tests(self):
        """Run all resilience tests."""
        self.results["provider_failover"] = await self.test_provider_failover()
        self.results["circuit_breaker"] = await self.test_circuit_breaker()
        self.results["cache_resilience"] = await self.test_cache_resilience()
        self.results["load_handling"] = await self.test_load_handling()
        self.results["degraded_mode"] = await self.test_degraded_mode()
        self.results["recovery"] = await self.test_recovery()

        return self.results

    async def test_provider_failover(self):
        """Test LLM provider failover."""
        # Implementation...

    async def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        # Implementation...

    async def test_cache_resilience(self):
        """Test cache resilience."""
        # Implementation...

    async def test_load_handling(self):
        """Test system behavior under load."""
        # Implementation...

    async def test_degraded_mode(self):
        """Test degraded mode operation."""
        # Implementation...

    async def test_recovery(self):
        """Test system recovery after failures."""
        # Implementation...
```

## Continuous Resilience Testing

Resilience tests should be run regularly as part of CI/CD pipelines:

```yaml
# .github/workflows/resilience-tests.yml
name: Resilience Tests

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  workflow_dispatch: # Allow manual triggers

jobs:
  resilience-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt

      - name: Set up test environment
        run: |
          ./scripts/setup-test-env.sh

      - name: Run resilience tests
        run: |
          python -m pytest tests/resilience/ -v

      - name: Generate resilience report
        run: |
          python scripts/generate_resilience_report.py

      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: resilience-test-results
          path: reports/resilience-report.html
```

## Test Result Analysis

Resilience test results should be analyzed to identify improvements:

1. **Key Metrics to Track**:

   - Recovery time after failure
   - Success rate during degraded operation
   - Response time distribution under load
   - Cache hit rate during provider outages
   - Circuit breaker open/close cycles

2. **Report Example**:

   ```
   === Resilience Test Report ===

   Provider Failover Test:
   - Success Rate: 98.5%
   - Average Failover Time: 120ms
   - Provider Usage: OpenAI (78%), Anthropic (21%), Google (1%)

   Circuit Breaker Test:
   - Proper Tripping: PASSED
   - Proper Reset: PASSED
   - Average Time to Open: 350ms
   - False Positive Rate: 0.5%

   Degraded Mode Test:
   - Core Functionality: PASSED
   - User Notification: PASSED
   - Feature Limitations: PASSED

   Recovery Test:
   - Database Recovery: PASSED (850ms)
   - Cache Recovery: PASSED (120ms)
   - Provider Recovery: PASSED (210ms)

   Load Handling:
   - Max Sustained RPS: 240
   - Response Time p50: 180ms
   - Response Time p95: 450ms
   - Response Time p99: 820ms
   ```

## Conclusion

Thorough resilience testing is essential to ensure the Ultra system can withstand failures and continue operating effectively. The testing approaches outlined in this guide provide a comprehensive framework for validating resilience features and identifying areas for improvement. Regular resilience testing should be part of the development and operational process to maintain and enhance system reliability.
