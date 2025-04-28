"""
Enhanced data pipeline with unified caching and parallel processing.

This module provides a high-performance data processing pipeline that leverages
the UnifiedCache system for efficient caching and implements parallel processing
for improved throughput on large datasets.
"""

import concurrent.futures
import logging
import os
import time
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Union, Literal

import pandas as pd

from src.core.cache_adapter import UnifiedCacheFactory
from src.data.cache.unified_cache import CacheConfig, CacheLevel


@dataclass
class PipelineMetrics:
    """Metrics for monitoring pipeline performance."""

    processing_time_ms: List[float] = field(default_factory=list)
    records_processed: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0

    def get_avg_processing_time(self) -> float:
        """Get average processing time in milliseconds."""
        if not self.processing_time_ms:
            return 0.0
        return sum(self.processing_time_ms) / len(self.processing_time_ms)

    def get_cache_hit_ratio(self) -> float:
        """Get cache hit ratio."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    def get_throughput(self) -> float:
        """Get throughput in records per second."""
        if not self.processing_time_ms:
            return 0.0
        total_time = sum(self.processing_time_ms) / 1000  # Convert to seconds
        if total_time == 0:
            return 0.0
        return self.records_processed / total_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "avg_processing_time_ms": self.get_avg_processing_time(),
            "records_processed": self.records_processed,
            "throughput_rps": self.get_throughput(),
            "cache_hit_ratio": self.get_cache_hit_ratio(),
            "errors": self.errors,
        }


@dataclass
class PipelineConfig:
    """Configuration for the data pipeline."""

    # Caching settings
    cache_enabled: bool = True
    cache_level: CacheLevel = CacheLevel.BOTH
    cache_ttl_seconds: int = 3600  # 1 hour

    # Parallel processing settings
    parallel_processing: bool = True
    max_workers: Optional[int] = None  # None means use available CPU count
    batch_size: int = 1000  # Records per batch for parallel processing

    # Monitoring settings
    collect_metrics: bool = True
    log_level: int = logging.INFO

    # Circuit breaker settings
    max_errors: int = 10  # Max consecutive errors before circuit breaks
    circuit_break_ttl_seconds: int = 60  # Time circuit stays open


class DataPipelineProcessor:
    """
    Processes data with configurable transformations and caching.

    Features:
    - Unified caching for processed data
    - Parallel processing of large datasets
    - Metrics collection
    - Circuit breaker pattern for error handling
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline processor.

        Args:
            config: Optional pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.config.log_level)

        # Initialize caching
        cache_config = CacheConfig(
            memory_cache_size_mb=512,
            disk_cache_enabled=True,
            default_ttl_seconds=self.config.cache_ttl_seconds,
            collect_metrics=True,
        )
        self.cache = UnifiedCacheFactory.get_instance("pipeline", cache_config)

        # Initialize metrics
        self.metrics = PipelineMetrics()

        # Circuit breaker state
        self.circuit_open = False
        self.circuit_open_until = 0
        self.consecutive_errors = 0

        self.logger.info(
            f"Initialized DataPipelineProcessor with config: {self.config}"
        )

    def _check_circuit_breaker(self) -> bool:
        """
        Check if circuit breaker is open.

        Returns:
            True if circuit is closed (processing allowed), False if open
        """
        # Reset if circuit break time has passed
        if self.circuit_open and time.time() > self.circuit_open_until:
            self.logger.info("Circuit breaker reset after timeout")
            self.circuit_open = False
            self.consecutive_errors = 0
            return True

        return not self.circuit_open

    def _open_circuit_breaker(self):
        """Open circuit breaker to prevent further processing after too many errors."""
        self.circuit_open = True
        self.circuit_open_until = time.time() + self.config.circuit_break_ttl_seconds
        ttl = self.config.circuit_break_ttl_seconds
        self.logger.warning(
            f"Circuit breaker opened for {ttl} seconds "
            f"after {self.consecutive_errors} consecutive errors"
        )

    def _generate_cache_key(
        self, data: Any, operation: str, params: Dict[str, Any]
    ) -> str:
        """
        Generate a cache key for the processing operation.

        Args:
            data: Input data (or its hash/identifier)
            operation: Operation name
            params: Operation parameters

        Returns:
            Cache key string
        """
        # For DataFrames, use shape and hash of column names as part of the key
        if isinstance(data, pd.DataFrame):
            data_id = f"df_{hash(tuple(data.columns))}_{data.shape[0]}_{data.shape[1]}"
        else:
            # For other types, use string representation or hash
            data_id = str(hash(str(data)))

        # Create key from operation and sorted params
        params_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{data_id}_{operation}_{params_str}"

    def _process_batch(
        self, batch: pd.DataFrame, operation: Callable, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Process a batch of data.

        Args:
            batch: DataFrame batch to process
            operation: Processing function
            params: Processing parameters

        Returns:
            Processed DataFrame batch
        """
        try:
            return operation(batch, **params)
        except Exception as e:
            self.logger.error(f"Error processing batch: {e}")
            self.metrics.errors += 1
            raise

    def process(
        self,
        data: Union[pd.DataFrame, List[Dict[str, Any]]],
        operation: Union[str, Callable],
        params: Optional[Dict[str, Any]] = None,
        cache_override: Optional[bool] = None,
    ) -> pd.DataFrame:
        """
        Process data with caching and parallel processing.

        Args:
            data: Input data to process
            operation: Operation name or callable function
            params: Processing parameters
            cache_override: Override cache setting for this operation

        Returns:
            Processed data
        """
        start_time = time.time()
        params = params or {}

        # Check circuit breaker
        if not self._check_circuit_breaker():
            self.logger.warning("Circuit breaker open, processing skipped")
            raise ValueError("Processing circuit is open due to too many errors")

        # Convert to DataFrame if needed
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)

        # Record data size
        record_count = len(data)
        self.metrics.records_processed += record_count

        # Resolve operation function
        if isinstance(operation, str):
            op_func = self._get_operation_by_name(operation)
        else:
            op_func = operation

        # Use cache if enabled
        use_cache = self.config.cache_enabled
        if cache_override is not None:
            use_cache = cache_override

        if use_cache:
            cache_key = self._generate_cache_key(data, str(operation), params)
            cached_result = self.cache.get(cache_key)

            if cached_result is not None:
                self.metrics.cache_hits += 1
                self.logger.debug(f"Cache hit for operation: {operation}")
                return cached_result

            self.metrics.cache_misses += 1

        try:
            # Process data (with parallel processing if enabled and data is large)
            large_data = record_count > self.config.batch_size
            if (
                self.config.parallel_processing
                and large_data
                and self.config.max_workers != 1
            ):

                result = self._process_in_parallel(data, op_func, params)
            else:
                result = op_func(data, **params)

            # Cache the result
            if use_cache:
                self.cache.set(
                    cache_key,
                    result,
                    ttl_seconds=self.config.cache_ttl_seconds,
                    cache_level=self.config.cache_level,
                )

            # Reset error counter on success
            self.consecutive_errors = 0

            # Record metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.processing_time_ms.append(elapsed_ms)

            return result

        except Exception as e:
            # Update error metrics and circuit breaker
            self.metrics.errors += 1
            self.consecutive_errors += 1

            # Check if we need to open the circuit
            if self.consecutive_errors >= self.config.max_errors:
                self._open_circuit_breaker()

            self.logger.error(f"Error processing data: {e}")
            raise

    def _process_in_parallel(
        self, data: pd.DataFrame, operation: Callable, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Process data in parallel using multiple workers.

        Args:
            data: Input DataFrame
            operation: Processing function
            params: Processing parameters

        Returns:
            Processed DataFrame
        """
        # Determine number of workers
        max_workers = self.config.max_workers or min(32, (os.cpu_count() or 4))

        # Split data into batches
        batch_size = self.config.batch_size
        batches = [
            data.iloc[i : i + batch_size] for i in range(0, len(data), batch_size)
        ]

        # Create processing function with fixed params
        process_func = partial(self._process_batch, operation=operation, params=params)

        # Process in parallel
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_func, batch) for batch in batches]

            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    self.logger.error(f"Parallel processing error: {e}")
                    self.metrics.errors += 1
                    raise

        # Combine results
        if results:
            return pd.concat(results, ignore_index=True)
        return pd.DataFrame()

    def _get_operation_by_name(self, operation_name: str) -> Callable:
        """
        Get operation function by name.

        Args:
            operation_name: Name of the operation

        Returns:
            Operation function
        """
        operations = {
            "filter": self._filter_data,
            "transform": self._transform_data,
            "aggregate": self._aggregate_data,
            "join": self._join_data,
            "clean": self._clean_data,
        }

        if operation_name not in operations:
            raise ValueError(f"Unknown operation: {operation_name}")

        return operations[operation_name]

    def _filter_data(
        self, data: pd.DataFrame, conditions: Optional[List[str]] = None, **kwargs
    ) -> pd.DataFrame:
        """
        Filter data based on conditions.

        Args:
            data: Input DataFrame
            conditions: List of filter conditions as strings (e.g., "column > value")

        Returns:
            Filtered DataFrame
        """
        result = data.copy()
        if conditions:
            for condition in conditions:
                result = result.query(condition)
        return result

    def _transform_data(
        self,
        data: pd.DataFrame,
        transformations: Optional[Dict[str, Union[str, Callable]]] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Apply transformations to data.

        Args:
            data: Input DataFrame
            transformations: Dictionary mapping column names to transformation functions

        Returns:
            Transformed DataFrame
        """
        result = data.copy()
        if transformations:
            for column, transform in transformations.items():
                if callable(transform):
                    result[column] = result[column].apply(transform)
                elif isinstance(transform, str):
                    # Handle string transformations (e.g., "upper", "lower")
                    if transform == "upper":
                        result[column] = result[column].str.upper()
                    elif transform == "lower":
                        result[column] = result[column].str.lower()
                    # Add more string transformations as needed
        return result

    def _aggregate_data(
        self,
        data: pd.DataFrame,
        group_by: Optional[List[str]] = None,
        aggregations: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Aggregate data by grouping and applying aggregation functions.

        Args:
            data: Input DataFrame
            group_by: Columns to group by
            aggregations: Dictionary mapping column names to aggregation functions

        Returns:
            Aggregated DataFrame
        """
        if not group_by or not aggregations:
            return data.copy()

        return data.groupby(group_by).agg(aggregations).reset_index()

    def _join_data(
        self,
        data: pd.DataFrame,
        right: Optional[pd.DataFrame] = None,
        on: Optional[Union[str, List[str]]] = None,
        how: Literal["inner", "outer", "left", "right", "cross"] = "inner",
        **kwargs,
    ) -> pd.DataFrame:
        """
        Join data with another DataFrame.

        Args:
            data: Left DataFrame
            right: Right DataFrame
            on: Columns to join on
            how: Join type (inner, outer, left, right, cross)

        Returns:
            Joined DataFrame
        """
        if right is None or on is None:
            return data.copy()

        return data.merge(right, on=on, how=how)

    def _clean_data(
        self,
        data: pd.DataFrame,
        drop_na: bool = False,
        fillna_values: Optional[Dict[str, Any]] = None,
        drop_duplicates: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Clean data by handling missing values and duplicates.

        Args:
            data: Input DataFrame
            drop_na: Whether to drop rows with NA values
            fillna_values: Dictionary mapping column names to fill values
            drop_duplicates: Whether to drop duplicate rows

        Returns:
            Cleaned DataFrame
        """
        result = data.copy()

        # Handle missing values
        if drop_na:
            result = result.dropna()
        elif fillna_values:
            for column, value in fillna_values.items():
                if column in result.columns:
                    result[column] = result[column].fillna(value)

        # Handle duplicates
        if drop_duplicates:
            result = result.drop_duplicates()

        return result

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get pipeline metrics.

        Returns:
            Dictionary with pipeline metrics
        """
        if not self.config.collect_metrics:
            return {}

        # Combine pipeline metrics with cache metrics
        pipeline_metrics = self.metrics.to_dict()
        cache_metrics = self.cache.get_metrics()

        return {
            "pipeline": pipeline_metrics,
            "cache": cache_metrics,
        }

    def clear_cache(self, namespace: Optional[str] = None):
        """
        Clear the cache.

        Args:
            namespace: Optional namespace to clear (clears all if None)
        """
        self.cache.clear(namespace)
        message = f"Cleared cache{f' for namespace {namespace}' if namespace else ''}"
        self.logger.info(message)

    def reset_metrics(self):
        """Reset pipeline metrics."""
        self.metrics = PipelineMetrics()
        self.logger.info("Reset pipeline metrics")

    def reset_circuit_breaker(self):
        """Reset circuit breaker state."""
        self.circuit_open = False
        self.consecutive_errors = 0
        self.logger.info("Reset circuit breaker state")
