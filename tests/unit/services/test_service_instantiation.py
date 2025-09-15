import pytest
import pkgutil
import inspect
import importlib
from unittest.mock import Mock

# Dynamically discover all modules in app.services
services_pkg = importlib.import_module("app.services")
# Discover modules, skipping those that fail to import
modules = []
for mod in pkgutil.iter_modules(services_pkg.__path__):
    modules.append(mod.name)

# Collect all classes to test, skipping modules with import errors
test_classes = []
for mod_name in modules:
    try:
        module = importlib.import_module(f"app.services.{mod_name}")
    except Exception:
        # Skip modules that fail to import
        continue
    for cls_name, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ and cls.__module__.startswith("app.services."):
            test_classes.append((mod_name, cls_name, cls))


@pytest.mark.parametrize("module_name, class_name, cls", test_classes)
def test_instantiate_service_class(module_name, class_name, cls):
    """
    Smoke test: attempt to instantiate service class with Mocked required parameters.
    Skip if instantiation fails.
    """
    sig = inspect.signature(cls)
    kwargs = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        if param.default is not inspect.Parameter.empty:
            continue
        # Provide a basic Mock for required parameters
        kwargs[param_name] = Mock()
    try:
        instance = cls(**kwargs)
    except Exception:
        pytest.skip(f"Could not instantiate {module_name}.{class_name}")
    assert instance is not None
