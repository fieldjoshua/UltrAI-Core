"""
System Orchestrator - Core component responsible for system coordination and management.
"""

import asyncio
import importlib.util
import logging
import os
import sys
from dataclasses import dataclass
from enum import Enum
from importlib.abc import Loader
from typing import Any, Callable, Dict, List, Optional, cast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System states."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ComponentStatus:
    """Component status information."""

    name: str
    state: SystemState
    health: float  # 0.0 to 1.0
    last_updated: float
    error_count: int
    warning_count: int


class SystemOrchestrator:
    """Manages system components and their lifecycle."""

    def __init__(self):
        self._components: Dict[str, Any] = {}
        self._state: SystemState = SystemState.INITIALIZING
        self._component_status: Dict[str, ComponentStatus] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._initialized = False
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> None:
        """Initialize the system orchestrator."""
        if self._initialized:
            logger.warning("System Orchestrator already initialized")
            return

        logger.info("Initializing System Orchestrator")
        self._state = SystemState.INITIALIZING

        try:
            # Initialize core components
            await self._initialize_core_components()

            # Start monitoring
            await self._start_monitoring()

            self._state = SystemState.RUNNING
            self._initialized = True
            logger.info("System Orchestrator initialized successfully")

        except Exception as e:
            self._state = SystemState.ERROR
            logger.error(f"Failed to initialize System Orchestrator: {str(e)}")
            raise

    async def _initialize_core_components(self) -> None:
        """Initialize core system components."""
        try:
            # Add core directory to Python path if not already there
            core_dir = os.path.dirname(os.path.abspath(__file__))
            if core_dir not in sys.path:
                sys.path.append(core_dir)

            # Initialize configuration manager
            config_spec = importlib.util.find_spec("config_manager")
            if config_spec is None:
                raise ImportError("Could not find config_manager module")
            config_module = importlib.util.module_from_spec(config_spec)
            cast(Loader, config_spec.loader).exec_module(config_module)
            self._components["config"] = config_module.ConfigurationManager()
            await self._components["config"].initialize()

            # Initialize event bus
            event_spec = importlib.util.find_spec("event_bus")
            if event_spec is None:
                raise ImportError("Could not find event_bus module")
            event_module = importlib.util.module_from_spec(event_spec)
            cast(Loader, event_spec.loader).exec_module(event_module)
            self._components["events"] = event_module.EventBus()
            await self._components["events"].initialize()

            # Initialize state manager
            state_spec = importlib.util.find_spec("state_manager")
            if state_spec is None:
                raise ImportError("Could not find state_manager module")
            state_module = importlib.util.module_from_spec(state_spec)
            cast(Loader, state_spec.loader).exec_module(state_module)
            self._components["state"] = state_module.StateManager()
            await self._components["state"].initialize()

        except Exception as e:
            logger.error(f"Failed to initialize core components: {str(e)}")
            raise

    async def _start_monitoring(self) -> None:
        """Start system monitoring."""
        asyncio.create_task(self._monitor_components())

    async def _monitor_components(self) -> None:
        """Monitor component health and status."""
        while not self._shutdown_event.is_set():
            for name, component in self._components.items():
                try:
                    health = await component.get_health()
                    self._update_component_status(name, health)
                except Exception as e:
                    logger.error(f"Error monitoring component {name}: {str(e)}")
                    self._update_component_status(name, 0.0, error=True)
            await asyncio.sleep(5)  # Check every 5 seconds

    def _update_component_status(
        self, name: str, health: float, error: bool = False
    ) -> None:
        """Update component status."""
        if name not in self._component_status:
            self._component_status[name] = ComponentStatus(
                name=name,
                state=SystemState.RUNNING,
                health=health,
                last_updated=asyncio.get_event_loop().time(),
                error_count=0,
                warning_count=0,
            )
        else:
            status = self._component_status[name]
            status.health = health
            status.last_updated = asyncio.get_event_loop().time()
            if error:
                status.error_count += 1
                status.state = SystemState.ERROR
            elif health < 0.5:
                status.warning_count += 1
                status.state = SystemState.ERROR
            else:
                status.state = SystemState.RUNNING

    async def register_component(self, name: str, component: Any) -> None:
        """Register a new component."""
        if name in self._components:
            raise ValueError(f"Component {name} already registered")

        self._components[name] = component
        logger.info(f"Registered component: {name}")

    async def unregister_component(self, name: str) -> None:
        """Unregister a component."""
        if name not in self._components:
            raise ValueError(f"Component {name} not found")

        del self._components[name]
        if name in self._component_status:
            del self._component_status[name]
        logger.info(f"Unregistered component: {name}")

    async def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name."""
        return self._components.get(name)

    async def get_component_status(self, name: str) -> Optional[ComponentStatus]:
        """Get component status."""
        return self._component_status.get(name)

    async def get_system_state(self) -> SystemState:
        """Get current system state."""
        return self._state

    async def shutdown(self) -> None:
        """Shutdown the system orchestrator."""
        if not self._initialized:
            return

        logger.info("Shutting down System Orchestrator")
        self._state = SystemState.SHUTTING_DOWN
        self._shutdown_event.set()

        # Shutdown components in reverse order
        for name, component in reversed(list(self._components.items())):
            try:
                await component.shutdown()
                logger.info(f"Shutdown component: {name}")
            except Exception as e:
                logger.error(f"Error shutting down component {name}: {str(e)}")

        self._state = SystemState.STOPPED
        self._initialized = False
        logger.info("System Orchestrator shutdown complete")

    async def get_health(self) -> float:
        """Get system health score."""
        if not self._component_status:
            return 1.0

        total_health = sum(status.health for status in self._component_status.values())
        return total_health / len(self._component_status)
