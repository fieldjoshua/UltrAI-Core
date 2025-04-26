"""
State Manager - Core component responsible for managing system state.
"""

from typing import Dict, Any, Optional, List, Callable
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
import time
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateType(Enum):
    """State types."""

    MEMORY = "memory"
    PERSISTENT = "persistent"
    CACHED = "cached"


@dataclass
class StateValue:
    """State value with metadata."""

    value: Any
    type: StateType
    last_updated: float
    version: int = 1
    is_encrypted: bool = False


class StateManager:
    """Manages system state."""

    def __init__(self, state_dir: Optional[str] = None):
        self._state: Dict[str, StateValue] = {}
        self._state_dir = state_dir or os.getenv("ULTRA_STATE_DIR", "state")
        self._state_file = os.path.join(self._state_dir, "state.json")
        self._initialized = False
        self._lock = asyncio.Lock()
        self._observers: Dict[str, List[Callable]] = {}
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes

    async def initialize(self) -> None:
        """Initialize the state manager."""
        if self._initialized:
            logger.warning("State Manager already initialized")
            return

        logger.info("Initializing State Manager")

        try:
            # Create state directory if it doesn't exist
            os.makedirs(self._state_dir, exist_ok=True)

            # Load persistent state
            await self._load_persistent_state()

            # Start cache cleanup
            asyncio.create_task(self._cleanup_cache())

            self._initialized = True
            logger.info("State Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize State Manager: {str(e)}")
            raise

    async def _load_persistent_state(self) -> None:
        """Load persistent state from file."""
        if not os.path.exists(self._state_file):
            logger.info(f"State file not found: {self._state_file}")
            return

        try:
            with open(self._state_file, "r") as f:
                state_data = json.load(f)

            for key, value in state_data.items():
                self._state[key] = StateValue(
                    value=value["value"],
                    type=StateType.PERSISTENT,
                    last_updated=value["last_updated"],
                    version=value.get("version", 1),
                    is_encrypted=value.get("is_encrypted", False),
                )

            logger.info(f"Loaded persistent state from file: {self._state_file}")

        except Exception as e:
            logger.error(f"Error loading state file: {str(e)}")
            raise

    async def _save_persistent_state(self) -> None:
        """Save persistent state to file."""
        try:
            state_data = {
                key: {
                    "value": value.value,
                    "last_updated": value.last_updated,
                    "version": value.version,
                    "is_encrypted": value.is_encrypted,
                }
                for key, value in self._state.items()
                if value.type == StateType.PERSISTENT
            }

            with open(self._state_file, "w") as f:
                json.dump(state_data, f, indent=2)

            logger.info(f"Saved persistent state to file: {self._state_file}")

        except Exception as e:
            logger.error(f"Error saving state file: {str(e)}")
            raise

    async def _cleanup_cache(self) -> None:
        """Clean up expired cache entries."""
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key
                    for key, (_, timestamp) in self._cache.items()
                    if current_time - timestamp > self._cache_ttl
                ]

                for key in expired_keys:
                    del self._cache[key]

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error cleaning up cache: {str(e)}")

    async def get(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        # Check cache first
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp <= self._cache_ttl:
                return value
            else:
                del self._cache[key]

        # Get from state
        state_value = self._state.get(key)
        if state_value is None:
            return default

        # Cache the value
        self._cache[key] = (state_value.value, time.time())

        return state_value.value

    async def set(
        self, key: str, value: Any, state_type: StateType = StateType.MEMORY
    ) -> None:
        """Set state value."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        async with self._lock:
            # Update state
            if key in self._state:
                state_value = self._state[key]
                state_value.value = value
                state_value.last_updated = time.time()
                state_value.version += 1
            else:
                self._state[key] = StateValue(
                    value=value, type=state_type, last_updated=time.time(), version=1
                )

            # Update cache
            self._cache[key] = (value, time.time())

            # Save persistent state if needed
            if state_type == StateType.PERSISTENT:
                await self._save_persistent_state()

            # Notify observers
            await self._notify_observers(key, value)

    async def delete(self, key: str) -> None:
        """Delete state value."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        async with self._lock:
            if key in self._state:
                state_value = self._state[key]
                del self._state[key]

                # Remove from cache
                if key in self._cache:
                    del self._cache[key]

                # Save persistent state if needed
                if state_value.type == StateType.PERSISTENT:
                    await self._save_persistent_state()

                # Notify observers
                await self._notify_observers(key, None)

    async def observe(self, key: str, callback: Callable) -> None:
        """Observe state changes."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        if key not in self._observers:
            self._observers[key] = []

        self._observers[key].append(callback)

    async def unobserve(self, key: str, callback: Callable) -> None:
        """Stop observing state changes."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        if key in self._observers:
            self._observers[key].remove(callback)
            if not self._observers[key]:
                del self._observers[key]

    async def _notify_observers(self, key: str, value: Any) -> None:
        """Notify observers of state changes."""
        if key in self._observers:
            for callback in self._observers[key]:
                try:
                    await callback(key, value)
                except Exception as e:
                    logger.error(f"Error in state observer for {key}: {str(e)}")

    async def get_all(self) -> Dict[str, Any]:
        """Get all state values."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        return {key: value.value for key, value in self._state.items()}

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state value metadata."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        state_value = self._state.get(key)
        if state_value is None:
            return None

        return {
            "type": state_value.type.value,
            "last_updated": state_value.last_updated,
            "version": state_value.version,
            "is_encrypted": state_value.is_encrypted,
        }

    async def clear(self) -> None:
        """Clear all state values."""
        if not self._initialized:
            raise RuntimeError("State Manager not initialized")

        async with self._lock:
            self._state.clear()
            self._cache.clear()
            await self._save_persistent_state()

    async def shutdown(self) -> None:
        """Shutdown the state manager."""
        if not self._initialized:
            return

        logger.info("Shutting down State Manager")

        # Save persistent state
        await self._save_persistent_state()

        # Clear cache
        self._cache.clear()

        self._initialized = False
        logger.info("State Manager shutdown complete")

    async def get_health(self) -> float:
        """Get state manager health score."""
        if not self._initialized:
            return 0.0

        try:
            # Check if state file is accessible
            if os.path.exists(self._state_file):
                with open(self._state_file, "r") as f:
                    json.load(f)

            return 1.0

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return 0.0
