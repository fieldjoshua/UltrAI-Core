"""
Stub service for LLM configuration management.
"""


class LLMConfigService:
    """Stub implementation for available LLM models."""

    def get_available_models(self):
        """Return an empty list of models by default."""
        return []


# Export singleton instance
llm_config_service = LLMConfigService()
