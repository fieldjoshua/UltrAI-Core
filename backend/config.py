import os


class Config:
    """Configuration object to hold runtime settings"""

    # Basic configuration
    use_mock = False

    # Document storage paths
    DOCUMENT_STORAGE_PATH = os.getenv("DOCUMENT_STORAGE_PATH", "document_storage")

    # Create necessary directories on startup
    @classmethod
    def create_directories(cls):
        """Create necessary directories for the application"""
        os.makedirs("temp_uploads", exist_ok=True)
        os.makedirs(cls.DOCUMENT_STORAGE_PATH, exist_ok=True)
        os.makedirs("temp", exist_ok=True)
        os.makedirs("logs", exist_ok=True)