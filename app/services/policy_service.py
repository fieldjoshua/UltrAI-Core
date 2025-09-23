import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


logger = logging.getLogger("policy_service")


class PolicyService:
    """Loads and serves operational policies with periodic refresh."""

    def __init__(self, policy_file: Optional[Path] = None) -> None:
        project_root = Path(__file__).parents[2]
        default_path = project_root / "ops" / "policies.yaml"
        self._policy_file: Path = policy_file or default_path
        self._policies: Dict[str, Any] = {}
        self._version: str = "0.0.0"
        self._last_loaded_iso: Optional[str] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._load_policies_safely()

    def get_version(self) -> str:
        return self._version

    def get_policies(self) -> Dict[str, Any]:
        return self._policies

    def get_last_loaded_iso(self) -> Optional[str]:
        return self._last_loaded_iso

    def reload(self) -> bool:
        return self._load_policies_safely()

    def _load_policies_safely(self) -> bool:
        try:
            if yaml is None:
                logger.error("PyYAML not available; cannot load policies")
                return False
            if not self._policy_file.exists():
                logger.warning(f"Policy file not found at {self._policy_file}")
                return False
            with self._policy_file.open("r", encoding="utf-8") as f:
                data: Dict[str, Any] = yaml.safe_load(f) or {}
            version = str(data.get("version", "0.0.0"))
            policies = data.get("policies", {})

            if not isinstance(policies, dict):
                logger.error("Invalid policies format; expected a mapping")
                return False

            # Minimal validation
            api_keys = policies.get("api_keys", {})
            if not isinstance(api_keys, dict) or "min_provider_keys_required" not in api_keys:
                logger.error("Invalid api_keys policy section")
                return False

            from datetime import datetime
            self._version = version
            self._policies = policies
            self._last_loaded_iso = datetime.utcnow().isoformat() + "Z"
            logger.info(f"Policies loaded (version {self._version}) from {self._policy_file}")
            return True
        except Exception as exc:  # Production safety: never raise
            logger.exception(f"Failed to load policies: {exc}")
            return False

    async def refresh_forever(self, interval_seconds: int = 300) -> None:
        """Periodically reload policies in the background."""
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                self._load_policies_safely()
            except Exception:  # pragma: no cover
                logger.exception("Policy refresh loop error")

    def start_background_refresh(self, interval_seconds: int = 300) -> None:
        if self._refresh_task and not self._refresh_task.done():
            return
        try:
            loop = asyncio.get_event_loop()
            self._refresh_task = loop.create_task(self.refresh_forever(interval_seconds))
            logger.info("Policy refresh task started")
        except RuntimeError:
            # No running loop (e.g., during import); caller can start later on startup
            logger.debug("No running loop; defer starting policy refresh task")


# Singleton
policy_service = PolicyService()
