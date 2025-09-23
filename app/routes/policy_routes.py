from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional
import os

from app.services.policy_service import policy_service


router = APIRouter(prefix="/api/ops", tags=["Ops"])


@router.get("/policy_version")
async def get_policy_version():
    return {
        "version": policy_service.get_version(),
        "last_loaded": policy_service.get_last_loaded_iso(),
    }


@router.post("/policy/reload")
async def reload_policies(x_policy_token: Optional[str] = Header(None)):
    # Simple header-based guard (optional)
    required = os.getenv("POLICY_RELOAD_TOKEN", "")
    if required:
        if not x_policy_token or x_policy_token != required:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    ok = policy_service.reload()
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Reload failed")
    return {
        "status": "ok",
        "version": policy_service.get_version(),
        "last_loaded": policy_service.get_last_loaded_iso(),
    }
