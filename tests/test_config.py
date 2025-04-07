import pytest
from ..config import Config, ModelConfig, OrchestratorConfig

def test_config_loading():
    config = Config()
    
    assert isinstance(config.llama, ModelConfig)
    assert isinstance(config.chatgpt, ModelConfig)
    assert isinstance(config.gemini, ModelConfig)
    assert isinstance(config.orchestrator, OrchestratorConfig)