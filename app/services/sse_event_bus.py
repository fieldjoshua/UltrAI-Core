import asyncio
import json
from typing import AsyncGenerator, Dict, Optional


class SSEEventBus:
    """Simple in-process event bus for Server-Sent Events keyed by correlation_id.

    This is intentionally minimal and does not persist events across process restarts.
    """

    def __init__(self) -> None:
        self._queues: Dict[str, asyncio.Queue[str]] = {}
        self._lock = asyncio.Lock()

    async def _get_queue(self, correlation_id: str) -> asyncio.Queue[str]:
        async with self._lock:
            if correlation_id not in self._queues:
                self._queues[correlation_id] = asyncio.Queue(maxsize=1000)
            return self._queues[correlation_id]

    async def publish(self, correlation_id: str, event_name: str, data: dict) -> None:
        """Publish an event for a given correlation_id.

        Encodes as an SSE frame:
          event: <event_name>\n
          data: <json>\n\n
        """
        if not correlation_id:
            return
        queue = await self._get_queue(correlation_id)
        payload = {
            "event": event_name,
            "data": data,
        }
        frame = f"event: {event_name}\n" f"data: {json.dumps(payload)}\n\n"
        try:
            queue.put_nowait(frame)
        except asyncio.QueueFull:
            # Drop oldest by getting one and retry once
            try:
                _ = queue.get_nowait()
            except Exception:
                pass
            try:
                queue.put_nowait(frame)
            except Exception:
                pass

    async def subscribe(self, correlation_id: str, heartbeat_seconds: int = 15) -> AsyncGenerator[str, None]:
        """Yield SSE frames for a correlation_id, with periodic heartbeats."""
        queue = await self._get_queue(correlation_id)

        async def heartbeat() -> None:
            while True:
                await asyncio.sleep(heartbeat_seconds)
                try:
                    queue.put_nowait("data: {\"event\": \"heartbeat\"}\n\n")
                except Exception:
                    # Ignore heartbeat enqueue failures
                    pass

        # Start heartbeat task
        hb_task: Optional[asyncio.Task] = asyncio.create_task(heartbeat())

        try:
            # Initial connected event
            yield "event: connected\n" "data: {\"event\": \"connected\"}\n\n"
            while True:
                item = await queue.get()
                yield item
        finally:
            if hb_task:
                hb_task.cancel()


# Singleton instance
sse_event_bus = SSEEventBus()


