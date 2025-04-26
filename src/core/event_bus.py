"""
Event Bus - Core component responsible for event handling and communication between components.
"""

from typing import Dict, List, Any, Optional, Callable
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priorities."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    """Event data structure."""

    name: str
    data: Any
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL
    source: str = "system"
    correlation_id: Optional[str] = None


class EventBus:
    """Manages event handling and communication between components."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._initialized = False
        self._lock = asyncio.Lock()
        self._event_queue = asyncio.Queue()
        self._processing = False

    async def initialize(self) -> None:
        """Initialize the event bus."""
        if self._initialized:
            logger.warning("Event Bus already initialized")
            return

        logger.info("Initializing Event Bus")

        try:
            # Start event processing
            self._processing = True
            asyncio.create_task(self._process_events())

            self._initialized = True
            logger.info("Event Bus initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Event Bus: {str(e)}")
            raise

    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._processing:
            try:
                event = await self._event_queue.get()
                await self._handle_event(event)
                self._event_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")

    async def _handle_event(self, event: Event) -> None:
        """Handle a single event."""
        handlers = self._handlers.get(event.name, [])

        # Sort handlers by priority
        handlers.sort(
            key=lambda h: getattr(h, "priority", EventPriority.NORMAL).value,
            reverse=True,
        )

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.name}: {str(e)}")

    async def publish(self, event: Event) -> None:
        """Publish an event."""
        if not self._initialized:
            raise RuntimeError("Event Bus not initialized")

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)

        # Add to queue
        await self._event_queue.put(event)
        logger.debug(f"Published event: {event.name}")

    async def subscribe(
        self,
        event_name: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """Subscribe to an event."""
        if not self._initialized:
            raise RuntimeError("Event Bus not initialized")

        async with self._lock:
            if event_name not in self._handlers:
                self._handlers[event_name] = []

            # Add priority to handler
            handler.priority = priority
            self._handlers[event_name].append(handler)
            logger.debug(f"Subscribed to event: {event_name}")

    async def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """Unsubscribe from an event."""
        if not self._initialized:
            raise RuntimeError("Event Bus not initialized")

        async with self._lock:
            if event_name in self._handlers:
                self._handlers[event_name].remove(handler)
                if not self._handlers[event_name]:
                    del self._handlers[event_name]
                logger.debug(f"Unsubscribed from event: {event_name}")

    async def get_event_history(
        self, event_name: Optional[str] = None, limit: int = 100
    ) -> List[Event]:
        """Get event history."""
        if not self._initialized:
            raise RuntimeError("Event Bus not initialized")

        history = self._event_history
        if event_name:
            history = [e for e in history if e.name == event_name]

        return history[-limit:]

    async def clear_event_history(self) -> None:
        """Clear event history."""
        if not self._initialized:
            raise RuntimeError("Event Bus not initialized")

        self._event_history.clear()
        logger.info("Cleared event history")

    async def get_subscriber_count(self, event_name: str) -> int:
        """Get number of subscribers for an event."""
        if not self._initialized:
            raise RuntimeError("Event Bus not initialized")

        return len(self._handlers.get(event_name, []))

    async def shutdown(self) -> None:
        """Shutdown the event bus."""
        if not self._initialized:
            return

        logger.info("Shutting down Event Bus")

        # Stop processing events
        self._processing = False

        # Wait for queue to be empty
        await self._event_queue.join()

        # Clear handlers
        self._handlers.clear()

        self._initialized = False
        logger.info("Event Bus shutdown complete")

    async def get_health(self) -> float:
        """Get event bus health score."""
        if not self._initialized:
            return 0.0

        try:
            # Check if event processing is working
            test_event = Event(
                name="health_check",
                data={"timestamp": time.time()},
                timestamp=time.time(),
                priority=EventPriority.CRITICAL,
            )

            # Create a future to wait for event processing
            future = asyncio.Future()

            async def health_check_handler(event: Event):
                if event.name == "health_check":
                    future.set_result(True)

            # Subscribe to health check event
            await self.subscribe("health_check", health_check_handler)

            # Publish test event
            await self.publish(test_event)

            # Wait for event to be processed
            await asyncio.wait_for(future, timeout=1.0)

            # Unsubscribe from health check event
            await self.unsubscribe("health_check", health_check_handler)

            return 1.0

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return 0.0
