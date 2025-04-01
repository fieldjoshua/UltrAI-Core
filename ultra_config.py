import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class UltraConfig:
    """Universal configuration settings for the Ultra platform."""
    # API Settings
    api_timeout: int = 30
    max_retries: int = 3
    rate_limit_requests: int = 60
    rate_limit_period: int = 60  # seconds
    
    # Model Settings
    default_model: str = "chatgpt"
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    
    # Data Processing Settings
    max_data_size: int = 1000000  # 1MB
    supported_formats: list = None
    default_output_format: str = "json"
    
    # Visualization Settings
    default_plot_style: str = "seaborn"
    figure_size: tuple = (10, 6)
    dpi: int = 300
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: str = "ultra.log"
    max_log_size: int = 10485760  # 10MB
    backup_count: int = 5
    
    # File System Settings
    output_dir: str = "output"
    temp_dir: str = "temp"
    cache_dir: str = "cache"
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["json", "csv", "txt", "md"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UltraConfig':
        """Create config from dictionary."""
        return cls(**data)

class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = UltraConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.config = UltraConfig.from_dict(data)
            else:
                self._save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._save_config()
    
    def _save_config(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values."""
        current_dict = self.config.to_dict()
        current_dict.update(updates)
        self.config = UltraConfig.from_dict(current_dict)
        self._save_config()
    
    def get_config(self) -> UltraConfig:
        """Get current configuration."""
        return self.config
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            # Validate paths
            for path in [self.config.output_dir, self.config.temp_dir, self.config.cache_dir]:
                os.makedirs(path, exist_ok=True)
            
            # Validate numeric values
            assert self.config.api_timeout > 0
            assert self.config.max_retries >= 0
            assert self.config.rate_limit_requests > 0
            assert self.config.rate_limit_period > 0
            assert 0 <= self.config.temperature <= 1
            assert 0 <= self.config.top_p <= 1
            
            # Validate formats
            assert self.config.default_output_format in self.config.supported_formats
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = UltraConfig()
        self._save_config()

def get_env_config() -> Dict[str, Any]:
    """Get configuration from environment variables."""
    config = {}
    prefix = "ULTRA_"
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            try:
                # Try to convert to appropriate type
                if value.lower() == "true":
                    config[config_key] = True
                elif value.lower() == "false":
                    config[config_key] = False
                elif value.isdigit():
                    config[config_key] = int(value)
                elif value.replace(".", "").isdigit():
                    config[config_key] = float(value)
                else:
                    config[config_key] = value
            except Exception:
                config[config_key] = value
    
    return config 