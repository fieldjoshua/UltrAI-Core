"""
Dependency Manager for Ultra Backend

This module provides a unified approach to handle optional dependencies in the Ultra backend.
It allows graceful degradation of services when optional dependencies are not available.
"""

import importlib
import logging
import os
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar

# Set up logging
from app.utils.logging import get_logger

logger = get_logger("dependency_manager", "logs/dependency.log")

# Type definitions
T = TypeVar("T")


class DependencyStatus:
    """Class representing dependency status"""

    def __init__(
        self,
        name: str,
        is_available: bool,
        is_required: bool,
        module_name: str,
        error: Optional[str] = None,
        installation_cmd: Optional[str] = None,
    ):
        """
        Initialize dependency status

        Args:
            name: Human-readable name of the dependency
            is_available: Whether the dependency is available
            is_required: Whether the dependency is required for core functionality
            module_name: Python module name
            error: Error message if dependency is not available
            installation_cmd: Command to install the dependency
        """
        self.name = name
        self.is_available = is_available
        self.is_required = is_required
        self.module_name = module_name
        self.error = error
        self.installation_cmd = installation_cmd or f"pip install {module_name}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to a dictionary"""
        return {
            "name": self.name,
            "is_available": self.is_available,
            "is_required": self.is_required,
            "module_name": self.module_name,
            "error": self.error,
            "installation_cmd": self.installation_cmd,
        }


class DependencyRegistry:
    """Registry for tracking dependency status"""

    def __init__(self):
        """Initialize dependency registry"""
        self.dependencies: Dict[str, DependencyStatus] = {}
        self.feature_flags: Dict[str, bool] = {}

    def register_dependency(
        self, status: DependencyStatus, feature_name: Optional[str] = None
    ) -> None:
        """
        Register a dependency status

        Args:
            status: Dependency status
            feature_name: Optional feature name to associate with this dependency
        """
        self.dependencies[status.module_name] = status

        # If a feature name is provided, set its flag based on dependency availability
        if feature_name:
            env_flag = f"ENABLE_{feature_name.upper()}"
            # Check if there's an explicit environment override
            env_value = os.getenv(env_flag)

            if env_value is not None:
                # Environment variable takes precedence if it exists
                is_enabled = env_value.lower() in ("true", "1", "yes")
            else:
                # Otherwise, base it on dependency availability
                is_enabled = status.is_available

            self.feature_flags[feature_name] = is_enabled
            logger.info(
                f"Feature '{feature_name}' {'enabled' if is_enabled else 'disabled'} "
                f"(dependency '{status.name}' is {'available' if status.is_available else 'unavailable'})"
            )

    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled

        Args:
            feature_name: Feature name to check

        Returns:
            True if feature is enabled, False otherwise
        """
        return self.feature_flags.get(feature_name, False)

    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statuses for all dependencies

        Returns:
            Dictionary of dependency statuses
        """
        return {key: status.to_dict() for key, status in self.dependencies.items()}

    def get_required_status(self) -> Tuple[bool, List[str]]:
        """
        Check if all required dependencies are available

        Returns:
            (all_available, missing_dependencies) tuple
        """
        missing = []
        for name, status in self.dependencies.items():
            if status.is_required and not status.is_available:
                missing.append(name)

        return len(missing) == 0, missing

    def get_feature_flags(self) -> Dict[str, bool]:
        """
        Get all feature flags

        Returns:
            Dictionary of feature flags
        """
        return self.feature_flags.copy()


# Create a global registry
dependency_registry = DependencyRegistry()


class DependencyNotAvailableError(Exception):
    """Exception raised when trying to use an unavailable dependency"""

    pass


class OptionalDependency(Generic[T]):
    """Class for handling optional dependencies"""

    def __init__(
        self,
        module_name: str,
        display_name: str = None,
        is_required: bool = False,
        feature_name: Optional[str] = None,
        installation_cmd: Optional[str] = None,
        fallback_factory: Optional[Callable[[], T]] = None,
    ):
        """
        Initialize optional dependency

        Args:
            module_name: Module name to import
            display_name: Human-readable name (defaults to module_name)
            is_required: Whether this dependency is required
            feature_name: Feature that depends on this module
            installation_cmd: Custom installation command
            fallback_factory: Function to create a fallback implementation
        """
        self.module_name = module_name
        self.display_name = display_name or module_name
        self.is_required = is_required
        self.feature_name = feature_name
        self.installation_cmd = installation_cmd
        self.fallback_factory = fallback_factory
        self.module: Optional[Any] = None
        self._error_message: Optional[str] = None

        # Try to import the module
        try:
            self.module = importlib.import_module(module_name)
            status = DependencyStatus(
                name=self.display_name,
                is_available=True,
                is_required=is_required,
                module_name=module_name,
                installation_cmd=installation_cmd,
            )
            logger.info(f"Successfully loaded dependency: {self.display_name}")
        except ImportError as e:
            self._error_message = str(e)
            status = DependencyStatus(
                name=self.display_name,
                is_available=False,
                is_required=is_required,
                module_name=module_name,
                error=str(e),
                installation_cmd=installation_cmd,
            )
            if is_required:
                logger.error(
                    f"Required dependency {self.display_name} ({module_name}) is not available: {str(e)}"
                )
                if not fallback_factory:
                    logger.critical(
                        f"No fallback for required dependency {self.display_name}. "
                        f"Install with: {installation_cmd or f'pip install {module_name}'}"
                    )
            else:
                logger.warning(
                    f"Optional dependency {self.display_name} ({module_name}) is not available: {str(e)}. "
                    f"Some features may be disabled. "
                    f"Install with: {installation_cmd or f'pip install {module_name}'}"
                )

        # Register the dependency status
        dependency_registry.register_dependency(status, feature_name)

    def is_available(self) -> bool:
        """
        Check if the dependency is available

        Returns:
            True if dependency is available, False otherwise
        """
        return self.module is not None

    def get_module(self) -> Any:
        """
        Get the imported module

        Returns:
            Imported module

        Raises:
            DependencyNotAvailableError: If dependency is not available
        """
        if self.module is None:
            raise DependencyNotAvailableError(
                f"Dependency {self.display_name} ({self.module_name}) is not available. "
                f"Error: {self._error_message}. "
                f"Install with: {self.installation_cmd or f'pip install {self.module_name}'}"
            )
        return self.module

    def get_implementation(self) -> T:
        """
        Get implementation of the dependency or fallback

        Returns:
            Implementation of the dependency or fallback

        Raises:
            DependencyNotAvailableError: If dependency is not available and no fallback
        """
        if self.module is not None:
            return self.module

        if self.fallback_factory is not None:
            logger.info(
                f"Using fallback implementation for {self.display_name} ({self.module_name})"
            )
            return self.fallback_factory()

        raise DependencyNotAvailableError(
            f"Dependency {self.display_name} ({self.module_name}) is not available "
            f"and no fallback is configured. "
            f"Error: {self._error_message}. "
            f"Install with: {self.installation_cmd or f'pip install {self.module_name}'}"
        )

    def get_attribute(self, attribute_name: str) -> Any:
        """
        Get an attribute from the module

        Args:
            attribute_name: Name of the attribute to get

        Returns:
            Attribute from the module

        Raises:
            DependencyNotAvailableError: If dependency is not available
            AttributeError: If attribute doesn't exist
        """
        module = self.get_module()
        return getattr(module, attribute_name)


# Common dependency definitions
jwt_dependency = OptionalDependency(
    module_name="jwt",
    display_name="PyJWT",
    is_required=False,
    feature_name="jwt_auth",
    installation_cmd="pip install PyJWT",
)

redis_dependency = OptionalDependency(
    module_name="redis",
    display_name="Redis",
    is_required=False,
    feature_name="redis_cache",
    installation_cmd="pip install redis",
)

sqlalchemy_dependency = OptionalDependency(
    module_name="sqlalchemy",
    display_name="SQLAlchemy",
    is_required=True,
    feature_name="database",
    installation_cmd="pip install SQLAlchemy",
)

sentry_dependency = OptionalDependency(
    module_name="sentry_sdk",
    display_name="Sentry SDK",
    is_required=False,
    feature_name="sentry",
    installation_cmd="pip install sentry-sdk",
)

# AI providers
openai_dependency = OptionalDependency(
    module_name="openai",
    display_name="OpenAI API",
    is_required=False,
    feature_name="openai",
    installation_cmd="pip install openai",
)

anthropic_dependency = OptionalDependency(
    module_name="anthropic",
    display_name="Anthropic API",
    is_required=False,
    feature_name="anthropic",
    installation_cmd="pip install anthropic",
)

google_ai_dependency = OptionalDependency(
    module_name="google.generativeai",
    display_name="Google Generative AI",
    is_required=False,
    feature_name="google_ai",
    installation_cmd="pip install google-generativeai",
)


def get_dependency_status() -> Dict[str, Any]:
    """
    Get status information for all dependencies

    Returns:
        Dictionary with dependency status information
    """
    return {
        "dependencies": dependency_registry.get_all_statuses(),
        "features": dependency_registry.get_feature_flags(),
        "all_required_available": dependency_registry.get_required_status()[0],
    }
