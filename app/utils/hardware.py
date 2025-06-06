"""
Hardware acceleration detection and management utilities.
"""

import platform
from typing import Dict, Any

import torch


def detect_hardware_acceleration() -> Dict[str, bool]:
    """
    Detect available hardware acceleration capabilities.

    Returns:
        Dict[str, bool]: Dictionary of hardware acceleration capabilities
    """
    capabilities = {
        "cuda": False,
        "mps": False,
        "cpu": True,  # CPU is always available
    }

    # Check for CUDA
    if torch.cuda.is_available():
        capabilities["cuda"] = True

    # Check for Apple Silicon MPS
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        if hasattr(torch, "mps") and torch.mps.is_available():
            capabilities["mps"] = True

    return capabilities


def get_optimal_device() -> str:
    """
    Determine the optimal device for model execution.

    Returns:
        str: Device identifier ('cuda', 'mps', or 'cpu')
    """
    capabilities = detect_hardware_acceleration()

    if capabilities["cuda"]:
        return "cuda"
    elif capabilities["mps"]:
        return "mps"
    else:
        return "cpu"


def get_device_info() -> Dict[str, Any]:
    """
    Get detailed information about the current device.

    Returns:
        Dict[str, Any]: Device information including type, memory, etc.
    """
    device = get_optimal_device()
    info = {
        "device": device,
        "capabilities": detect_hardware_acceleration(),
    }

    if device == "cuda":
        info.update(
            {
                "device_name": torch.cuda.get_device_name(0),
                "device_count": torch.cuda.device_count(),
                "memory_allocated": torch.cuda.memory_allocated(0),
                "memory_reserved": torch.cuda.memory_reserved(0),
            }
        )
    elif device == "mps":
        info.update(
            {
                "device_name": "Apple Silicon MPS",
                "memory_available": None,  # MPS doesn't provide memory info
            }
        )
    else:
        info.update(
            {
                "device_name": "CPU",
                "memory_available": None,  # CPU memory info would require psutil
            }
        )

    return info


def set_device_preferences(preferences: Dict[str, bool]) -> None:
    """
    Set device preferences for model execution.

    Args:
        preferences (Dict[str, bool]): Dictionary of device preferences
    """
    # This is a placeholder for future implementation
    # Will be used to set device preferences based on user configuration
    pass
