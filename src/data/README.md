# Ultra Data Directory

This directory contains persistent data storage for the Ultra AI Framework.

## Directory Structure

- **embeddings/**: Vector embeddings for documents and queries
  - Used by the document processing system for semantic search
  - Generated using text-embedding models

- **cache/**: Cached responses and API results
  - Reduces duplicate API calls
  - Improves performance for repeated queries

- **results/**: Analysis results and outputs
  - Stored in structured format
  - Used for benchmarking and improvement

## Data Management

Data in this directory is organized by date and session ID to allow for easy tracking of analysis over time. This structure supports both debugging and performance benchmarking.

### Data Retention

By default, data is retained for 30 days. To change this behavior, modify the `DATA_RETENTION_DAYS` setting in the configuration file.

### Large Files

Large embedding files and result sets are stored with versioning to track changes over time. This directory is excluded from Git through the `.gitignore` file.

## Backups

Automated backups of this directory are configured in the `deployment/` scripts. To manually backup this data:

```bash
scripts/backup_data.sh [destination]
```

# Data Pipeline

This directory contains the enhanced data processing and caching system for Ultra.

## Components

### Unified Cache

The `UnifiedCache` class in `cache/unified_cache.py` provides a comprehensive caching solution with:

- **Memory and disk caching** - Cache items in memory for fast access and on disk for persistence
- **TTL-based expiration** - Automatically expire cache items after a configurable time
- **Configurable eviction policies** - LRU, LFU, and FIFO policies for memory cache
- **Namespace support** - Organize cache items by namespace
- **Metrics collection** - Track performance metrics like hit ratios and access times
- **Thread-safety** - Thread-safe operations for concurrent access

### Cache Adapters

The adapter classes in `core/cache_adapter.py` allow the unified cache to be integrated with existing systems:

- **CacheManagerAdapter** - Drop-in replacement for the legacy CacheManager
- **ResponseCacheAdapter** - Drop-in replacement for the legacy ResponseCache
- **UnifiedCacheFactory** - Factory for creating and managing cache instances

### Data Pipeline Processor

The `DataPipelineProcessor` class in `pipeline.py` provides a high-performance data processing system with:

- **Parallel processing** - Process large datasets in parallel for better performance
- **Efficient caching** - Cache processing results to avoid redundant work
- **Advanced metrics** - Track performance metrics for monitoring and optimization
- **Circuit breaker pattern** - Prevent cascading failures by breaking circuits after errors
- **Standardized operations** - Common data operations like filtering, transformation, and aggregation

## Usage

### Unified Cache

```python
from src.data.cache.unified_cache import CacheConfig, CacheLevel, UnifiedCache

# Create a cache instance
config = CacheConfig(
    memory_cache_size_mb=512,
    disk_cache_enabled=True,
    default_ttl_seconds=3600,
    collect_metrics=True
)
cache = UnifiedCache(config)

# Store and retrieve items
cache.set("my_key", {"data": "value"}, namespace="my_namespace")
result = cache.get("my_key", namespace="my_namespace")

# Get metrics
metrics = cache.get_metrics()
```

### Data Pipeline Processor

```python
import pandas as pd
from src.data.pipeline import DataPipelineProcessor, PipelineConfig

# Create a pipeline processor
config = PipelineConfig(
    cache_enabled=True,
    parallel_processing=True,
    collect_metrics=True
)
processor = DataPipelineProcessor(config)

# Process data with operations
df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})

# Built-in operations
filtered_df = processor.process(
    df,
    "filter",
    {"conditions": ["value > 2"]}
)

# Custom operations
def double_values(data, **kwargs):
    result = data.copy()
    result["value"] = result["value"] * 2
    return result

doubled_df = processor.process(df, double_values)

# Get pipeline metrics
metrics = processor.get_metrics()
```

## Design Principles

The refactored data pipeline follows these design principles:

1. **Performance** - Optimized for high throughput and low latency
2. **Reliability** - Robust error handling and circuit breakers
3. **Modularity** - Clean interfaces and separation of concerns
4. **Observability** - Comprehensive metrics and logging
5. **Compatibility** - Smooth integration with existing systems

## Future Improvements

Potential future enhancements:

- **Async/await support** - For non-blocking operations
- **Distributed caching** - Integration with Redis or other distributed cache systems
- **More eviction policies** - Additional cache eviction strategies
- **Schema validation** - Data validation for pipeline operations
- **Pipeline composition** - Chaining multiple operations with optimized execution
