"""
Streaming Handler for the EnhancedOrchestrator

This module implements efficient streaming response interfaces with backpressure handling,
throttling, and adaptive chunking capabilities to optimize real-time data delivery.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class StreamingMode(Enum):
    """Defines the mode for streaming responses."""

    TOKENS = "tokens"  # Stream individual tokens
    CHUNKS = "chunks"  # Stream fixed-size chunks
    SENTENCES = "sentences"  # Stream complete sentences
    ADAPTIVE = "adaptive"  # Dynamically adjust chunk size based on client capacity


class BackpressureStrategy(Enum):
    """Defines strategies for handling backpressure in streaming."""

    BUFFER = "buffer"  # Buffer tokens when client processing is slow
    THROTTLE = "throttle"  # Slow down token generation rate
    DROP = "drop"  # Drop tokens if buffer is full (lossy streaming)
    ADAPTIVE = "adaptive"  # Dynamically adjust between buffering and throttling


@dataclass
class StreamingMetrics:
    """Tracks metrics for streaming performance."""

    total_tokens: int = 0
    streaming_duration_ms: int = 0
    tokens_per_second: float = 0
    max_buffer_size: int = 0
    throttle_events: int = 0
    client_latency_ms: float = 0
    average_chunk_size: float = 0
    chunks_sent: int = 0


@dataclass
class StreamingConfig:
    """Configuration for streaming behavior."""

    mode: StreamingMode = StreamingMode.ADAPTIVE
    backpressure_strategy: BackpressureStrategy = BackpressureStrategy.ADAPTIVE
    max_buffer_size: int = 1000
    chunk_size: int = 20
    throttle_threshold_ms: int = 50
    adaptive_factor: float = 0.8
    sentence_delimiters: List[str] = field(
        default_factory=lambda: [".", "!", "?", "\n"]
    )
    client_timeout_ms: int = 5000
    enable_metrics: bool = True


class StreamingHandler:
    """
    Handles streaming responses from LLM models with advanced flow control.

    This class provides efficient streaming interfaces with backpressure handling,
    adaptive chunking, and performance monitoring for real-time data delivery.
    """

    def __init__(self, config: Optional[StreamingConfig] = None):
        """Initialize the streaming handler with the given configuration."""
        self.config = config or StreamingConfig()
        self.buffer: List[str] = []
        self.metrics = StreamingMetrics()
        self.start_time = 0
        self._last_client_process_time = 0
        self._last_chunk_time = 0
        self._current_sentence_buffer = ""

    async def process_stream(
        self,
        token_stream: AsyncGenerator[str, None],
        on_chunk_callback: Optional[Callable[[str], Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Process a stream of tokens and yield chunks according to the configured mode.

        Args:
            token_stream: Async generator producing tokens
            on_chunk_callback: Optional callback function when chunks are produced

        Yields:
            Processed chunks based on the configured streaming mode
        """
        self.start_time = time.time()
        self.metrics = StreamingMetrics()

        try:
            async for token in token_stream:
                self.metrics.total_tokens += 1

                # Apply backpressure control if needed
                await self._handle_backpressure()

                # Process the token based on the streaming mode
                chunk = await self._process_token(token)

                if chunk:
                    self.metrics.chunks_sent += 1
                    self.metrics.average_chunk_size = (
                        self.metrics.average_chunk_size * (self.metrics.chunks_sent - 1)
                        + len(chunk)
                    ) / self.metrics.chunks_sent

                    self._last_chunk_time = time.time()

                    if on_chunk_callback:
                        on_chunk_callback(chunk)

                    yield chunk

                    # Track client processing time
                    client_process_time = time.time()
                    if self._last_client_process_time > 0:
                        latency = (
                            client_process_time - self._last_client_process_time
                        ) * 1000
                        self.metrics.client_latency_ms = (
                            self.metrics.client_latency_ms
                            * (self.metrics.chunks_sent - 1)
                            + latency
                        ) / self.metrics.chunks_sent
                    self._last_client_process_time = client_process_time

            # Flush any remaining tokens in the buffer
            final_chunk = self._flush_buffer()
            if final_chunk:
                self.metrics.chunks_sent += 1
                if on_chunk_callback:
                    on_chunk_callback(final_chunk)
                yield final_chunk

        finally:
            # Calculate final metrics
            end_time = time.time()
            duration_sec = end_time - self.start_time
            self.metrics.streaming_duration_ms = int(duration_sec * 1000)

            if duration_sec > 0:
                self.metrics.tokens_per_second = (
                    self.metrics.total_tokens / duration_sec
                )

            logger.debug(
                "Streaming completed: %d tokens in %dms (%.2f tokens/sec), %d chunks, avg chunk size: %.1f",
                self.metrics.total_tokens,
                self.metrics.streaming_duration_ms,
                self.metrics.tokens_per_second,
                self.metrics.chunks_sent,
                self.metrics.average_chunk_size,
            )

    async def _handle_backpressure(self) -> None:
        """Handle backpressure based on the configured strategy."""
        buffer_size = len(self.buffer)
        self.metrics.max_buffer_size = max(self.metrics.max_buffer_size, buffer_size)

        # Check if backpressure handling is needed
        if buffer_size >= self.config.max_buffer_size * 0.8:
            strategy = self.config.backpressure_strategy

            if strategy == BackpressureStrategy.BUFFER:
                # Continue with buffer but limit size
                if buffer_size > self.config.max_buffer_size:
                    self.buffer = self.buffer[-self.config.max_buffer_size :]

            elif strategy == BackpressureStrategy.THROTTLE:
                # Introduce delay based on buffer fullness
                fullness_ratio = buffer_size / self.config.max_buffer_size
                delay = fullness_ratio * self.config.throttle_threshold_ms / 1000
                self.metrics.throttle_events += 1
                await asyncio.sleep(delay)

            elif strategy == BackpressureStrategy.DROP:
                # Drop oldest tokens if buffer is full
                if buffer_size >= self.config.max_buffer_size:
                    excess = buffer_size - int(self.config.max_buffer_size * 0.7)
                    self.buffer = self.buffer[excess:]

            elif strategy == BackpressureStrategy.ADAPTIVE:
                # Dynamically choose between throttling and buffering
                fullness_ratio = buffer_size / self.config.max_buffer_size

                if fullness_ratio > 0.95:
                    # Buffer is critical, drop some tokens
                    excess = buffer_size - int(self.config.max_buffer_size * 0.8)
                    if excess > 0:
                        self.buffer = self.buffer[excess:]
                elif fullness_ratio > 0.8:
                    # Apply throttling with adaptive delay
                    delay = (
                        (fullness_ratio - 0.8)
                        * self.config.throttle_threshold_ms
                        / 1000
                    )
                    self.metrics.throttle_events += 1
                    await asyncio.sleep(delay)

    async def _process_token(self, token: str) -> Optional[str]:
        """
        Process a token according to the streaming mode and return a chunk if ready.

        Args:
            token: The token to process

        Returns:
            A chunk if ready to send, None otherwise
        """
        self.buffer.append(token)

        if self.config.mode == StreamingMode.TOKENS:
            # Stream each token individually
            return self._flush_buffer()

        elif self.config.mode == StreamingMode.CHUNKS:
            # Stream fixed-size chunks
            if len(self.buffer) >= self.config.chunk_size:
                return self._flush_buffer()

        elif self.config.mode == StreamingMode.SENTENCES:
            # Accumulate tokens into the sentence buffer
            self._current_sentence_buffer += token

            # Check if we have a complete sentence
            for delimiter in self.config.sentence_delimiters:
                if delimiter in self._current_sentence_buffer:
                    # Get the position after the delimiter
                    pos = self._current_sentence_buffer.find(delimiter) + len(delimiter)
                    complete_sentence = self._current_sentence_buffer[:pos]
                    self._current_sentence_buffer = self._current_sentence_buffer[pos:]

                    # Clear the token buffer as we're using the sentence buffer
                    self.buffer = []
                    return complete_sentence

        elif self.config.mode == StreamingMode.ADAPTIVE:
            # Dynamically adjust chunk size based on client processing time
            if self.metrics.client_latency_ms > 0:
                # If client is slow, increase chunk size to reduce overhead
                if self.metrics.client_latency_ms > self.config.throttle_threshold_ms:
                    adaptive_size = int(
                        self.config.chunk_size * (1 + self.config.adaptive_factor)
                    )
                    if len(self.buffer) >= adaptive_size:
                        return self._flush_buffer()
                else:
                    # If client is fast, use smaller chunks for lower latency
                    adaptive_size = max(
                        1, int(self.config.chunk_size * self.config.adaptive_factor)
                    )
                    if len(self.buffer) >= adaptive_size:
                        return self._flush_buffer()
            elif len(self.buffer) >= self.config.chunk_size:
                # Use default chunk size if we don't have client metrics yet
                return self._flush_buffer()

        return None

    def _flush_buffer(self) -> Optional[str]:
        """Flush the current buffer and return it as a string."""
        if not self.buffer:
            return None

        chunk = "".join(self.buffer)
        self.buffer = []
        return chunk

    def get_metrics(self) -> Dict[str, Any]:
        """Get the current streaming metrics."""
        return {
            "total_tokens": self.metrics.total_tokens,
            "streaming_duration_ms": self.metrics.streaming_duration_ms,
            "tokens_per_second": self.metrics.tokens_per_second,
            "max_buffer_size": self.metrics.max_buffer_size,
            "throttle_events": self.metrics.throttle_events,
            "client_latency_ms": self.metrics.client_latency_ms,
            "average_chunk_size": self.metrics.average_chunk_size,
            "chunks_sent": self.metrics.chunks_sent,
        }

    def reset(self) -> None:
        """Reset the handler state."""
        self.buffer = []
        self.metrics = StreamingMetrics()
        self.start_time = 0
        self._last_client_process_time = 0
        self._last_chunk_time = 0
        self._current_sentence_buffer = ""


async def create_sample_token_stream() -> AsyncGenerator[str, None]:
    """Create a sample token stream for testing."""
    tokens = [
        "Hello",
        " ",
        "world",
        "!",
        " ",
        "This",
        " ",
        "is",
        " ",
        "a",
        " ",
        "sample",
        " ",
        "streaming",
        " ",
        "response",
        ".",
        " ",
        "How",
        " ",
        "efficient",
        " ",
        "is",
        " ",
        "the",
        " ",
        "handler",
        "?",
    ]

    for token in tokens:
        yield token
        await asyncio.sleep(0.05)  # Simulate token generation time


async def sample_usage() -> None:
    """Demonstrate sample usage of the StreamingHandler."""
    config = StreamingConfig(
        mode=StreamingMode.ADAPTIVE,
        backpressure_strategy=BackpressureStrategy.ADAPTIVE,
        chunk_size=5,
    )

    handler = StreamingHandler(config)
    token_stream = create_sample_token_stream()

    print("Starting streaming:")
    async for chunk in handler.process_stream(token_stream):
        print(f"Received chunk: '{chunk}'")
        await asyncio.sleep(0.1)  # Simulate client processing time

    print("\nStreaming metrics:")
    for key, value in handler.get_metrics().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    # This code runs when the module is executed directly
    import sys

    if sys.version_info >= (3, 7):
        asyncio.run(sample_usage())
    else:
        # For Python 3.6
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sample_usage())
