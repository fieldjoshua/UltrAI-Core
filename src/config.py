from dataclasses import dataclass
from typing import Dict, Any
import yaml

@dataclass
class ModelConfig:
    api_key: str
    max_tokens: int
    temperature: float
    timeout: int
    base_url: str = ""
    
@dataclass
class OrchestratorConfig:
    cache_enabled: bool = True
    max_retries: int = 3
    max_cache_age_hours: int = 24
    log_level: str = "INFO"
    quality_evaluation_enabled: bool = True

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self.llama = ModelConfig(**config['llama'])
        self.chatgpt = ModelConfig(**config['chatgpt'])
        self.gemini = ModelConfig(**config['gemini'])
        self.orchestrator = OrchestratorConfig(**config['orchestrator']) 