import logging
import socket
from typing import List

logger = logging.getLogger("server_utils")


def is_port_available(port: int) -> bool:
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            return True
        except socket.error:
            return False


def find_available_port(start_port: int) -> int:
    """Find an available port starting from start_port"""
    port = start_port
    while not is_port_available(port) and port < start_port + 100:
        port += 1
    return port


def cleanup_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files created during request processing"""
    import os

    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {file_path}: {str(e)}")
