"""
Persistent request queue for Ultra.

This module provides a persistent queue for handling retryable requests, ensuring
that requests are processed even if the system is restarted.
"""

import asyncio
import inspect
import logging
import os
import pickle
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Configure logger
logger = logging.getLogger("persistent_queue")


class RequestStatus(str, Enum):
    """Status of a request in the queue."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class RequestPriority(int, Enum):
    """Priority of a request in the queue."""

    HIGH = 100
    NORMAL = 50
    LOW = 10


@dataclass
class QueuedRequest:
    """A request in the queue."""

    id: str
    operation: Callable
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: RequestPriority = RequestPriority.NORMAL
    max_retries: int = 3
    retry_delay_base: float = 2.0
    status: RequestStatus = RequestStatus.PENDING
    attempts: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    next_attempt_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        """Initialize the request."""
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary for serialization."""
        return {
            "id": self.id,
            "priority": self.priority,
            "max_retries": self.max_retries,
            "retry_delay_base": self.retry_delay_base,
            "status": self.status,
            "attempts": self.attempts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "next_attempt_at": self.next_attempt_at,
            "result": self.result,
            "error": self.error,
            # The operation, args, and kwargs are serialized separately
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        operation: Callable,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> "QueuedRequest":
        """Create a request from a dictionary."""
        return cls(
            id=data["id"],
            operation=operation,
            args=args,
            kwargs=kwargs,
            priority=data["priority"],
            max_retries=data["max_retries"],
            retry_delay_base=data["retry_delay_base"],
            status=data["status"],
            attempts=data["attempts"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            next_attempt_at=data["next_attempt_at"],
            result=data["result"],
            error=data["error"],
        )

    def get_retry_delay(self) -> float:
        """Get the delay before the next retry attempt."""
        if self.attempts <= 0:
            return 0

        # Exponential backoff with jitter
        delay = self.retry_delay_base ** (self.attempts - 1)
        jitter = delay * 0.1 * (time.time() % 1.0)
        return delay + jitter


class QueueFullException(Exception):
    """Exception raised when the queue is full."""

    def __init__(
        self,
        message: str = "Queue is full",
        max_size: Optional[int] = None,
    ):
        """Initialize the exception."""
        if max_size is not None:
            message = f"{message} (max size: {max_size})"
        super().__init__(message)
        self.max_size = max_size


class PersistentRequestQueue:
    """
    Persistent queue for request processing with resilience features.

    This queue ensures that requests are processed even if the system is restarted,
    providing resilience against system failures.
    """

    def __init__(
        self,
        name: str,
        storage_path: Optional[str] = None,
        max_size: int = 1000,
        worker_count: int = 5,
        poll_interval: float = 1.0,
    ):
        """
        Initialize the persistent queue.

        Args:
            name: Queue name
            storage_path: Path to store the queue state (None to disable persistence)
            max_size: Maximum number of requests in the queue
            worker_count: Number of worker tasks to process the queue
            poll_interval: Interval in seconds to poll for new requests
        """
        self.name = name
        self.storage_path = storage_path
        self.max_size = max_size
        self.worker_count = worker_count
        self.poll_interval = poll_interval

        self.requests: Dict[str, QueuedRequest] = {}
        self.processing = False
        self.processing_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

        logger.info(
            f"Initialized persistent queue {name} with "
            f"storage_path={storage_path}, max_size={max_size}, "
            f"worker_count={worker_count}, poll_interval={poll_interval}"
        )

        # Create storage directory if it doesn't exist
        if storage_path:
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)

            # Load existing queue if available
            if os.path.exists(storage_path):
                try:
                    self._load_state_sync()
                except Exception as e:
                    logger.error(f"Error loading queue state: {e}")

    async def start(self) -> None:
        """Start processing the queue."""
        async with self._lock:
            if self.processing:
                return

            self.processing = True
            self.processing_task = asyncio.create_task(self._process_queue())

            logger.info(f"Started processing queue {self.name}")

    async def stop(self) -> None:
        """Stop processing the queue."""
        async with self._lock:
            if not self.processing or not self.processing_task:
                return

            self.processing = False

            # Wait for the processing task to complete
            if self.processing_task:
                try:
                    await asyncio.wait_for(self.processing_task, timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout waiting for queue {self.name} to stop")
                    self.processing_task.cancel()
                except Exception as e:
                    logger.error(f"Error stopping queue {self.name}: {e}")
                finally:
                    self.processing_task = None

            logger.info(f"Stopped processing queue {self.name}")

    async def enqueue(
        self,
        operation: Callable,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        priority: RequestPriority = RequestPriority.NORMAL,
        max_retries: int = 3,
        retry_delay_base: float = 2.0,
    ) -> str:
        """
        Add a request to the queue.

        Args:
            operation: Function to call
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            priority: Request priority
            max_retries: Maximum number of retry attempts
            retry_delay_base: Base delay for exponential backoff

        Returns:
            Request ID

        Raises:
            QueueFullException: If the queue is full
        """
        async with self._lock:
            # Check queue size
            if len(self.requests) >= self.max_size:
                raise QueueFullException(
                    message=f"Queue {self.name} is full",
                    max_size=self.max_size,
                )

            # Create request
            request = QueuedRequest(
                id=str(uuid.uuid4()),
                operation=operation,
                args=args or [],
                kwargs=kwargs or {},
                priority=priority,
                max_retries=max_retries,
                retry_delay_base=retry_delay_base,
            )

            # Add request to queue
            self.requests[request.id] = request

            # Save queue state
            await self._save_state()

            logger.info(
                f"Enqueued request {request.id} with "
                f"priority={priority.name}, max_retries={max_retries}"
            )

            return request.id

    async def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a request from the queue.

        Args:
            request_id: Request ID

        Returns:
            Request data or None if not found
        """
        async with self._lock:
            request = self.requests.get(request_id)
            if not request:
                return None

            # Return a copy of the request data
            return request.to_dict()

    async def get_requests(
        self,
        status: Optional[RequestStatus] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get requests from the queue.

        Args:
            status: Filter by request status (None for all)
            limit: Maximum number of requests to return (None for all)

        Returns:
            List of request data
        """
        async with self._lock:
            # Filter requests by status
            requests = list(self.requests.values())
            if status:
                requests = [r for r in requests if r.status == status]

            # Sort requests by priority and created time
            requests.sort(key=lambda r: (-r.priority, r.created_at))

            # Limit the number of requests
            if limit is not None:
                requests = requests[:limit]

            # Return a copy of the request data
            return [r.to_dict() for r in requests]

    async def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending request.

        Args:
            request_id: Request ID

        Returns:
            True if the request was cancelled, False if not found or not pending
        """
        async with self._lock:
            request = self.requests.get(request_id)
            if not request or request.status != RequestStatus.PENDING:
                return False

            # Mark request as failed
            request.status = RequestStatus.FAILED
            request.error = "Cancelled by user"
            request.updated_at = time.time()

            # Save queue state
            await self._save_state()

            logger.info(f"Cancelled request {request_id}")

            return True

    async def clear(self) -> int:
        """
        Clear the queue.

        Returns:
            Number of requests cleared
        """
        async with self._lock:
            # Get request count
            count = len(self.requests)

            # Clear requests
            self.requests.clear()

            # Save queue state
            await self._save_state()

            logger.info(f"Cleared {count} requests from queue {self.name}")

            return count

    async def _process_queue(self) -> None:
        """Process requests in the queue."""
        while self.processing:
            try:
                # Clean up completed and failed requests
                await self._cleanup_old_requests()

                # Process requests
                await self._process_requests()

                # Wait for the next interval
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                # Task was cancelled, exit gracefully
                logger.info(f"Queue {self.name} processing task cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing queue {self.name}: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

    async def _process_requests(self) -> None:
        """Process requests in the queue."""
        # Get pending requests sorted by priority
        pending_requests = []
        retry_requests = []

        async with self._lock:
            now = time.time()

            for request in self.requests.values():
                if request.status == RequestStatus.PENDING:
                    pending_requests.append(request)
                elif request.status == RequestStatus.RETRY:
                    if (
                        request.next_attempt_at is None
                        or now >= request.next_attempt_at
                    ):
                        retry_requests.append(request)

        # Sort requests by priority and created time
        pending_requests.sort(key=lambda r: (-r.priority, r.created_at))
        retry_requests.sort(key=lambda r: (-r.priority, r.next_attempt_at or 0))

        # Process retry requests first
        tasks = []
        for request in retry_requests:
            if len(tasks) >= self.worker_count:
                break

            # Mark request as processing
            async with self._lock:
                if request.id not in self.requests:
                    continue

                request = self.requests[request.id]
                request.status = RequestStatus.PROCESSING
                request.updated_at = time.time()
                await self._save_state()

            # Create task to process the request
            tasks.append(asyncio.create_task(self._process_request(request)))

        # Process pending requests
        for request in pending_requests:
            if len(tasks) >= self.worker_count:
                break

            # Mark request as processing
            async with self._lock:
                if request.id not in self.requests:
                    continue

                request = self.requests[request.id]
                request.status = RequestStatus.PROCESSING
                request.updated_at = time.time()
                await self._save_state()

            # Create task to process the request
            tasks.append(asyncio.create_task(self._process_request(request)))

        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_request(self, request: QueuedRequest) -> None:
        """
        Process a single request.

        Args:
            request: Request to process
        """
        # Update request status
        request.attempts += 1
        request.updated_at = time.time()

        logger.info(
            f"Processing request {request.id} "
            f"(attempt {request.attempts}/{request.max_retries + 1})"
        )

        try:
            # Call the operation
            if inspect.iscoroutinefunction(request.operation):
                result = await request.operation(*request.args, **request.kwargs)
            else:
                result = request.operation(*request.args, **request.kwargs)

            # Update request status
            async with self._lock:
                if request.id not in self.requests:
                    return

                request = self.requests[request.id]
                request.status = RequestStatus.COMPLETED
                request.result = result
                request.updated_at = time.time()

                logger.info(f"Request {request.id} completed successfully")

                await self._save_state()
        except Exception as e:
            # Update request status
            async with self._lock:
                if request.id not in self.requests:
                    return

                request = self.requests[request.id]

                if request.attempts <= request.max_retries:
                    # Retry the request
                    request.status = RequestStatus.RETRY
                    request.error = str(e)
                    request.updated_at = time.time()

                    # Calculate next retry time
                    retry_delay = request.get_retry_delay()
                    request.next_attempt_at = time.time() + retry_delay

                    logger.warning(
                        f"Request {request.id} failed, "
                        f"retrying in {retry_delay:.2f}s "
                        f"(attempt {request.attempts}/{request.max_retries + 1}): {e}"
                    )
                else:
                    # Mark request as failed
                    request.status = RequestStatus.FAILED
                    request.error = str(e)
                    request.updated_at = time.time()

                    logger.error(
                        f"Request {request.id} failed after "
                        f"{request.attempts} attempts: {e}"
                    )

                await self._save_state()

    async def _cleanup_old_requests(self) -> None:
        """Clean up old completed and failed requests."""
        async with self._lock:
            now = time.time()

            # Keep track of requests to remove
            to_remove = []

            for request_id, request in self.requests.items():
                if request.status in [RequestStatus.COMPLETED, RequestStatus.FAILED]:
                    # Remove completed and failed requests after 1 hour
                    if now - request.updated_at > 3600:
                        to_remove.append(request_id)

            # Remove old requests
            for request_id in to_remove:
                del self.requests[request_id]

            if to_remove:
                await self._save_state()

                logger.info(f"Cleaned up {len(to_remove)} old requests")

    async def _save_state(self) -> None:
        """Save queue state to persistent storage."""
        if not self.storage_path:
            return

        try:
            # Serialize queue state
            state = {
                "name": self.name,
                "max_size": self.max_size,
                "requests": {},
            }

            # Process each request
            for request_id, request in self.requests.items():
                # Serialize the request
                request_data = request.to_dict()

                # We can't serialize the operation, so we'll just store its name
                operation_name = request.operation.__name__

                # Serialize args and kwargs
                try:
                    serialized_args = pickle.dumps(request.args)
                    serialized_kwargs = pickle.dumps(request.kwargs)
                except Exception as e:
                    logger.error(
                        f"Error serializing args/kwargs for request {request_id}: {e}"
                    )
                    continue

                # Store the request
                state["requests"][request_id] = {
                    "data": request_data,
                    "operation_name": operation_name,
                    "serialized_args": serialized_args,
                    "serialized_kwargs": serialized_kwargs,
                }

            # Write state to file
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, "wb") as f:
                pickle.dump(state, f)

            # Atomically replace the old file
            os.replace(temp_path, self.storage_path)

            logger.debug(
                f"Saved queue state to {self.storage_path} "
                f"({len(self.requests)} requests)"
            )
        except Exception as e:
            logger.error(f"Error saving queue state: {e}", exc_info=True)

    def _load_state_sync(self) -> None:
        """Load queue state from persistent storage (synchronous version)."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return

        try:
            # Load state from file
            with open(self.storage_path, "rb") as f:
                state = pickle.load(f)

            # Validate state
            if not isinstance(state, dict) or "requests" not in state:
                logger.error(f"Invalid queue state in {self.storage_path}")
                return

            # Handle operation registry - this is a temporary registry for loading
            # We'll need to register operations before loading the queue
            operation_registry = {}

            # Process each request
            requests = {}
            for request_id, request_state in state["requests"].items():
                # Check that all required fields are present
                if not all(
                    field in request_state
                    for field in [
                        "data",
                        "operation_name",
                        "serialized_args",
                        "serialized_kwargs",
                    ]
                ):
                    logger.error(f"Invalid request state for request {request_id}")
                    continue

                # Get request data
                request_data = request_state["data"]
                operation_name = request_state["operation_name"]

                # Get operation function
                operation = operation_registry.get(operation_name)
                if operation is None:
                    logger.warning(
                        f"Operation {operation_name} not found in registry, "
                        f"skipping request {request_id}"
                    )
                    continue

                # Deserialize args and kwargs
                try:
                    args = pickle.loads(request_state["serialized_args"])
                    kwargs = pickle.loads(request_state["serialized_kwargs"])
                except Exception as e:
                    logger.error(
                        f"Error deserializing args/kwargs for request {request_id}: {e}"
                    )
                    continue

                # Create request
                try:
                    request = QueuedRequest.from_dict(
                        request_data,
                        operation=operation,
                        args=args,
                        kwargs=kwargs,
                    )

                    # Add request to queue
                    requests[request_id] = request
                except Exception as e:
                    logger.error(f"Error creating request {request_id}: {e}")
                    continue

            # Update queue state
            self.requests = requests
            self.max_size = state.get("max_size", self.max_size)

            logger.info(
                f"Loaded queue state from {self.storage_path} "
                f"({len(self.requests)} requests)"
            )
        except Exception as e:
            logger.error(f"Error loading queue state: {e}", exc_info=True)

    async def register_operation(
        self,
        operation: Callable,
        name: Optional[str] = None,
    ) -> None:
        """
        Register an operation for deserialization.

        Args:
            operation: Operation function
            name: Operation name (defaults to function name)
        """
        # This is just a placeholder for now since we're not fully implementing
        # the operation registry in this version
        pass
