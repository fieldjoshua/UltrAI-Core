import logging
import os
from typing import Optional

import httpx


logger = logging.getLogger("notifications")


async def notify_policy_reload(version: str) -> None:
    """Send a lightweight notification when policies reload.

    Uses SLACK_WEBHOOK_URL if present. Silent on failure.
    """
    url: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return
    payload = {"text": f"Policies reloaded to version {version}"}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(url, json=payload)
    except Exception:
        logger.debug("Slack notification failed (ignored)")


