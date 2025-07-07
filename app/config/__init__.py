"""app.config package

Exposes:
- Config: main application configuration (config.py)
- ORCH_CONFIG: orchestrator specific configuration (orchestrator_config.py)
"""

from importlib import import_module
from types import ModuleType
from typing import TYPE_CHECKING

# Lazily import to avoid heavy dotenv parsing during module discovery
_config_mod: ModuleType | None = None
_orch_config_mod: ModuleType | None = None


def _lazy_import():
    global _config_mod, _orch_config_mod
    if _config_mod is None:
        _config_mod = import_module("app.config.config")
    if _orch_config_mod is None:
        _orch_config_mod = import_module("app.config.orchestrator_config")


if TYPE_CHECKING:  # provide typing without runtime import cost
    from .config import Config  # noqa: F401
    from .orchestrator_config import CONFIG as ORCH_CONFIG  # noqa: F401
else:
    _lazy_import()
    Config = getattr(_config_mod, "Config")  # type: ignore
    ORCH_CONFIG = getattr(_orch_config_mod, "CONFIG")  # type: ignore

__all__ = ["Config", "ORCH_CONFIG"]
