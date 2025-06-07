"""
Models Package

This package contains data models for the Ultra API.
"""

from .document import DocumentChunk, DocumentUploadResponse, ProcessedDocument

try:
    from .llm_models import (  # type: ignore
        AnalysisMode,
        AnalysisModesResponse,
        ModelCapabilities,
        ModelInfo,
        ModelResponse,
        ModelsResponse,
        ModelStatus,
        ModelStatusInfo,
        ModelStatusResponse,
        PatternsResponse,
    )
except ImportError:
    # llm_models file may not exist in this action; skip related imports
    pass
from .pricing import (
    AddFundsRequest,
    PricingToggleRequest,
    TokenEstimateRequest,
    UserAccountRequest,
)

__all__ = [
    "DocumentChunk",
    "ProcessedDocument",
    "DocumentUploadResponse",
    "TokenEstimateRequest",
    "PricingToggleRequest",
    "UserAccountRequest",
    "AddFundsRequest",
    "ModelStatus",
    "ModelCapabilities",
    "ModelInfo",
    "ModelStatusInfo",
    "AnalysisMode",
    "ModelsResponse",
    "ModelResponse",
    "ModelStatusResponse",
    "PatternsResponse",
    "AnalysisModesResponse",
]
