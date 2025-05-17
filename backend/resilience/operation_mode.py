"""
System operation mode manager for Ultra.

This module provides a system operation mode manager that tracks the current operation
mode of the system and handles graceful degradation.
"""

import asyncio
import json
import logging
import os
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Configure logger
logger = logging.getLogger("operation_mode")


class OperationMode(str, Enum):
    """System operation modes."""

    NORMAL = "normal"
    DEGRADED = "degraded"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"


class DegradationSeverity(str, Enum):
    """Severity levels for component degradation."""

    LOW = "low"  # Minor issue, no significant impact
    MEDIUM = "medium"  # Moderate issue, some functionality affected
    HIGH = "high"  # Severe issue, major functionality affected
    CRITICAL = "critical"  # Critical issue, system barely functional


class DegradationReason:
    """Reason for system degradation."""

    def __init__(
        self,
        component: str,
        message: str,
        severity: DegradationSeverity = DegradationSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a degradation reason.

        Args:
            component: Name of the degraded component
            message: Description of the degradation
            severity: Severity of the degradation
            details: Additional details about the degradation
        """
        self.component = component
        self.message = message
        self.severity = severity
        self.details = details or {}
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the degradation reason to a dictionary."""
        return {
            "component": self.component,
            "message": self.message,
            "severity": self.severity,
            "details": self.details,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DegradationReason":
        """Create a degradation reason from a dictionary."""
        return cls(
            component=data["component"],
            message=data["message"],
            severity=data["severity"],
            details=data.get("details", {}),
        )


class SystemOperationMode:
    """
    System operation mode manager.

    Tracks the current operation mode of the system and handles graceful degradation
    when components fail.
    """

    def __init__(
        self,
        state_file: Optional[str] = None,
        auto_update_mode: bool = True,
    ):
        """
        Initialize the system operation mode manager.

        Args:
            state_file: Path to store the operation mode state
            auto_update_mode: Whether to automatically update the mode based on degraded components
        """
        self.state_file = state_file
        self.auto_update_mode = auto_update_mode

        self.current_mode = OperationMode.NORMAL
        self.degraded_components: Dict[str, DegradationReason] = {}
        self.mode_change_listeners: List[Callable] = []
        self._lock = asyncio.Lock()

        # Create state file directory if it doesn't exist
        if state_file:
            os.makedirs(os.path.dirname(state_file), exist_ok=True)

            # Load state if it exists
            if os.path.exists(state_file):
                try:
                    self._load_state_sync()
                except Exception as e:
                    logger.error(f"Error loading operation mode state: {e}")

        logger.info(
            f"Initialized system operation mode manager with "
            f"state_file={state_file}, auto_update_mode={auto_update_mode}"
        )

    async def set_mode(
        self,
        mode: OperationMode,
        reason: Optional[str] = None,
        component: Optional[str] = None,
    ) -> None:
        """
        Set the system operation mode.

        Args:
            mode: New operation mode
            reason: Reason for the mode change
            component: Component that triggered the mode change
        """
        async with self._lock:
            if mode == self.current_mode:
                return

            old_mode = self.current_mode
            self.current_mode = mode

            # Add degradation reason if provided
            if reason and component and mode != OperationMode.NORMAL:
                self.degraded_components[component] = DegradationReason(
                    component=component,
                    message=reason,
                    severity=DegradationSeverity.MEDIUM,
                )

            # Clear degradation reasons if switching to normal mode
            if mode == OperationMode.NORMAL:
                self.degraded_components.clear()

            # Save state
            await self._save_state()

            # Notify listeners
            await self._notify_mode_change(old_mode, mode)

            logger.info(
                f"System operation mode changed from {old_mode} to {mode}"
                + (f" ({reason})" if reason else "")
            )

    async def get_mode(self) -> OperationMode:
        """Get the current system operation mode."""
        async with self._lock:
            return self.current_mode

    async def mark_component_degraded(
        self,
        component: str,
        message: str,
        severity: DegradationSeverity = DegradationSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Mark a component as degraded.

        Args:
            component: Name of the component
            message: Description of the degradation
            severity: Severity of the degradation
            details: Additional details about the degradation
        """
        async with self._lock:
            # Add degradation reason
            self.degraded_components[component] = DegradationReason(
                component=component,
                message=message,
                severity=severity,
                details=details or {},
            )

            # Auto-update mode if enabled
            if self.auto_update_mode:
                await self._update_mode_from_components()

            # Save state
            await self._save_state()

            logger.warning(
                f"Component {component} marked as degraded: {message} "
                f"(severity: {severity.name})"
            )

    async def mark_component_normal(self, component: str) -> None:
        """
        Mark a component as normal (not degraded).

        Args:
            component: Name of the component
        """
        async with self._lock:
            # Remove degradation reason
            if component in self.degraded_components:
                del self.degraded_components[component]

                # Auto-update mode if enabled
                if self.auto_update_mode:
                    await self._update_mode_from_components()

                # Save state
                await self._save_state()

                logger.info(f"Component {component} marked as normal")

    async def get_degraded_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all degraded components.

        Returns:
            Dictionary of component names to degradation reasons
        """
        async with self._lock:
            return {
                name: reason.to_dict()
                for name, reason in self.degraded_components.items()
            }

    async def add_mode_change_listener(
        self,
        listener: Callable[[OperationMode, OperationMode, Dict[str, Any]], None],
    ) -> None:
        """
        Add a listener for mode changes.

        Args:
            listener: Function to call when the mode changes
        """
        async with self._lock:
            self.mode_change_listeners.append(listener)

    async def remove_mode_change_listener(self, listener: Callable) -> None:
        """
        Remove a mode change listener.

        Args:
            listener: Listener to remove
        """
        async with self._lock:
            if listener in self.mode_change_listeners:
                self.mode_change_listeners.remove(listener)

    async def get_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the system status.

        Returns:
            Dictionary with system status information
        """
        async with self._lock:
            return {
                "mode": self.current_mode,
                "degraded_components": {
                    name: reason.to_dict()
                    for name, reason in self.degraded_components.items()
                },
                "healthy": self.current_mode == OperationMode.NORMAL,
                "timestamp": time.time(),
            }

    async def _update_mode_from_components(self) -> None:
        """Update the operation mode based on degraded components."""
        if not self.degraded_components:
            # No degraded components, set mode to normal
            if self.current_mode != OperationMode.NORMAL:
                old_mode = self.current_mode
                self.current_mode = OperationMode.NORMAL
                await self._notify_mode_change(old_mode, self.current_mode)
            return

        # Check for critical severity
        for reason in self.degraded_components.values():
            if reason.severity == DegradationSeverity.CRITICAL:
                if self.current_mode != OperationMode.EMERGENCY:
                    old_mode = self.current_mode
                    self.current_mode = OperationMode.EMERGENCY
                    await self._notify_mode_change(old_mode, self.current_mode)
                return

        # Check for high severity
        for reason in self.degraded_components.values():
            if reason.severity == DegradationSeverity.HIGH:
                if self.current_mode != OperationMode.EMERGENCY:
                    old_mode = self.current_mode
                    self.current_mode = OperationMode.EMERGENCY
                    await self._notify_mode_change(old_mode, self.current_mode)
                return

        # Check for medium severity
        for reason in self.degraded_components.values():
            if reason.severity == DegradationSeverity.MEDIUM:
                if self.current_mode != OperationMode.DEGRADED:
                    old_mode = self.current_mode
                    self.current_mode = OperationMode.DEGRADED
                    await self._notify_mode_change(old_mode, self.current_mode)
                return

        # Only low severity degradation, keep normal mode
        if self.current_mode != OperationMode.NORMAL:
            old_mode = self.current_mode
            self.current_mode = OperationMode.NORMAL
            await self._notify_mode_change(old_mode, self.current_mode)

    async def _notify_mode_change(
        self,
        old_mode: OperationMode,
        new_mode: OperationMode,
    ) -> None:
        """
        Notify listeners of a mode change.

        Args:
            old_mode: Previous operation mode
            new_mode: New operation mode
        """
        # Get a snapshot of the degraded components
        degraded_components = {
            name: reason.to_dict() for name, reason in self.degraded_components.items()
        }

        for listener in self.mode_change_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(old_mode, new_mode, degraded_components)
                else:
                    listener(old_mode, new_mode, degraded_components)
            except Exception as e:
                logger.error(f"Error in mode change listener: {e}")

    async def _save_state(self) -> None:
        """Save operation mode state to a file."""
        if not self.state_file:
            return

        try:
            # Create state object
            state = {
                "mode": self.current_mode,
                "degraded_components": {
                    name: reason.to_dict()
                    for name, reason in self.degraded_components.items()
                },
                "timestamp": time.time(),
            }

            # Write state to temporary file
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, "w") as f:
                json.dump(state, f, indent=2)

            # Atomically replace the old file
            os.replace(temp_file, self.state_file)

            logger.debug(f"Saved operation mode state to {self.state_file}")
        except Exception as e:
            logger.error(f"Error saving operation mode state: {e}")

    def _load_state_sync(self) -> None:
        """Load operation mode state from a file (synchronous version)."""
        if not self.state_file or not os.path.exists(self.state_file):
            return

        try:
            # Read state from file
            with open(self.state_file, "r") as f:
                state = json.load(f)

            # Validate state
            if not isinstance(state, dict) or "mode" not in state:
                logger.error(f"Invalid operation mode state in {self.state_file}")
                return

            # Set operation mode
            self.current_mode = state["mode"]

            # Load degraded components
            if "degraded_components" in state and isinstance(
                state["degraded_components"], dict
            ):
                self.degraded_components = {}
                for name, reason_dict in state["degraded_components"].items():
                    try:
                        self.degraded_components[name] = DegradationReason.from_dict(
                            reason_dict
                        )
                    except Exception as e:
                        logger.error(
                            f"Error loading degradation reason for {name}: {e}"
                        )

            logger.info(
                f"Loaded operation mode state from {self.state_file}: "
                f"mode={self.current_mode}, "
                f"degraded_components={len(self.degraded_components)}"
            )
        except Exception as e:
            logger.error(f"Error loading operation mode state: {e}")


class FeatureFlag:
    """
    Feature flag that can be enabled or disabled based on the system operation mode.

    Feature flags can be used to enable or disable features based on the system operation
    mode, allowing for graceful degradation when components fail.
    """

    def __init__(
        self,
        name: str,
        default_enabled: bool = True,
        disabled_in_modes: Optional[List[OperationMode]] = None,
        requires_components: Optional[List[str]] = None,
    ):
        """
        Initialize a feature flag.

        Args:
            name: Feature name
            default_enabled: Whether the feature is enabled by default
            disabled_in_modes: Operation modes in which the feature is disabled
            requires_components: Components required for the feature to work
        """
        self.name = name
        self.default_enabled = default_enabled
        self.disabled_in_modes = disabled_in_modes or [OperationMode.EMERGENCY]
        self.requires_components = requires_components or []
        self._enabled_override: Optional[bool] = None

        logger.info(
            f"Initialized feature flag {name} with "
            f"default_enabled={default_enabled}, "
            f"disabled_in_modes={disabled_in_modes}, "
            f"requires_components={requires_components}"
        )

    async def is_enabled(
        self,
        operation_mode: SystemOperationMode,
    ) -> bool:
        """
        Check if the feature is enabled.

        Args:
            operation_mode: System operation mode manager

        Returns:
            True if the feature is enabled, False otherwise
        """
        # Check manual override
        if self._enabled_override is not None:
            return self._enabled_override

        # Get current mode
        current_mode = await operation_mode.get_mode()

        # Check if feature is disabled in current mode
        if current_mode in self.disabled_in_modes:
            return False

        # Check if required components are degraded
        if self.requires_components:
            degraded_components = await operation_mode.get_degraded_components()

            for component in self.requires_components:
                if component in degraded_components:
                    return False

        return self.default_enabled

    def set_enabled(self, enabled: Optional[bool]) -> None:
        """
        Manually override the feature flag state.

        Args:
            enabled: True to enable, False to disable, None to use default behavior
        """
        self._enabled_override = enabled

        if enabled is None:
            logger.info(f"Feature flag {self.name} set to use default behavior")
        else:
            logger.info(f"Feature flag {self.name} manually set to {enabled}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get the feature flag status.

        Returns:
            Dictionary with feature flag status information
        """
        return {
            "name": self.name,
            "default_enabled": self.default_enabled,
            "disabled_in_modes": self.disabled_in_modes,
            "requires_components": self.requires_components,
            "manual_override": self._enabled_override,
        }


class FeatureFlagRegistry:
    """
    Registry for feature flags.

    Provides a central registry for feature flags and their availability based on
    the system operation mode.
    """

    def __init__(self, operation_mode: SystemOperationMode):
        """
        Initialize the feature flag registry.

        Args:
            operation_mode: System operation mode manager
        """
        self.operation_mode = operation_mode
        self.feature_flags: Dict[str, FeatureFlag] = {}
        self._lock = asyncio.Lock()

        logger.info("Initialized feature flag registry")

    async def register_feature_flag(
        self,
        name: str,
        default_enabled: bool = True,
        disabled_in_modes: Optional[List[OperationMode]] = None,
        requires_components: Optional[List[str]] = None,
    ) -> FeatureFlag:
        """
        Register a feature flag.

        Args:
            name: Feature name
            default_enabled: Whether the feature is enabled by default
            disabled_in_modes: Operation modes in which the feature is disabled
            requires_components: Components required for the feature to work

        Returns:
            The registered feature flag
        """
        async with self._lock:
            # Create feature flag
            feature_flag = FeatureFlag(
                name=name,
                default_enabled=default_enabled,
                disabled_in_modes=disabled_in_modes,
                requires_components=requires_components,
            )

            # Add to registry
            self.feature_flags[name] = feature_flag

            return feature_flag

    async def get_feature_flag(self, name: str) -> Optional[FeatureFlag]:
        """
        Get a feature flag.

        Args:
            name: Feature name

        Returns:
            The feature flag, or None if not found
        """
        async with self._lock:
            return self.feature_flags.get(name)

    async def is_feature_enabled(self, name: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            name: Feature name

        Returns:
            True if the feature is enabled, False otherwise
        """
        async with self._lock:
            feature_flag = self.feature_flags.get(name)
            if not feature_flag:
                logger.warning(f"Feature flag {name} not found, defaulting to enabled")
                return True

            return await feature_flag.is_enabled(self.operation_mode)

    async def set_feature_enabled(
        self,
        name: str,
        enabled: Optional[bool],
    ) -> bool:
        """
        Set a feature's enabled state.

        Args:
            name: Feature name
            enabled: True to enable, False to disable, None to use default behavior

        Returns:
            True if the feature was found and updated, False otherwise
        """
        async with self._lock:
            feature_flag = self.feature_flags.get(name)
            if not feature_flag:
                logger.warning(f"Feature flag {name} not found")
                return False

            feature_flag.set_enabled(enabled)
            return True

    async def get_all_feature_flags(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all feature flags and their status.

        Returns:
            Dictionary of feature names to their status
        """
        async with self._lock:
            result = {}

            for name, feature_flag in self.feature_flags.items():
                # Get feature flag status
                status = feature_flag.get_status()

                # Add enabled status
                status["enabled"] = await feature_flag.is_enabled(self.operation_mode)

                result[name] = status

            return result
