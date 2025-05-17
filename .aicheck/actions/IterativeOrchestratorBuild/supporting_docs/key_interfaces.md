# Key Interfaces

This document defines the core interfaces for the Iterative Orchestrator system. These interfaces establish the contract between components, enabling modular development and testing.

## 1. Orchestrator Interface

The core interface for orchestration functionality:

```python
class OrchestratorInterface:
    """Interface for LLM orchestration."""

    async def check_models_availability(self) -> Dict[str, bool]:
        """
        Check which models are available and responsive.

        Returns:
            Dict[str, bool]: Mapping of model names to availability status
        """
        pass

    async def process(self,
                     prompt: str,
                     selected_models: Optional[List[str]] = None,
                     ultra_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a prompt using multiple LLMs and synthesize the results.

        Args:
            prompt (str): The prompt to analyze
            selected_models (list, optional): Models to use for analysis
            ultra_model (str, optional): Model to use for synthesis

        Returns:
            dict: The orchestrated response
        """
        pass
```

## 2. LLM Adapter Interface

Interface for LLM-specific implementations:

```python
class LLMAdapterInterface:
    """Interface for LLM-specific adapters."""

    async def is_available(self) -> bool:
        """
        Check if this LLM is available for use.

        Returns:
            bool: True if available, False otherwise
        """
        pass

    async def generate(self,
                      prompt: str,
                      parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response from this LLM.

        Args:
            prompt (str): The prompt to send
            parameters (dict, optional): Generation parameters

        Returns:
            dict: The LLM response
        """
        pass

    def get_provider(self) -> str:
        """
        Get the provider name for this LLM.

        Returns:
            str: Provider name (e.g., 'openai', 'anthropic')
        """
        pass
```

## 3. Document Processor Interface

Interface for document processing:

```python
class DocumentProcessorInterface:
    """Interface for document processing."""

    async def extract_content(self,
                             document: Union[str, bytes, IO]) -> str:
        """
        Extract text content from a document.

        Args:
            document: Document content or file path

        Returns:
            str: Extracted text content
        """
        pass

    async def get_metadata(self,
                          document: Union[str, bytes, IO]) -> Dict[str, Any]:
        """
        Extract metadata from a document.

        Args:
            document: Document content or file path

        Returns:
            dict: Document metadata
        """
        pass
```

## 4. Analysis Pattern Interface

Interface for analysis patterns:

```python
class AnalysisPatternInterface:
    """Interface for analysis patterns."""

    def get_name(self) -> str:
        """
        Get the name of this analysis pattern.

        Returns:
            str: Pattern name
        """
        pass

    def get_description(self) -> str:
        """
        Get a description of this analysis pattern.

        Returns:
            str: Pattern description
        """
        pass

    async def format_prompt(self,
                           base_prompt: str,
                           document_content: Optional[str] = None) -> str:
        """
        Format a prompt according to this analysis pattern.

        Args:
            base_prompt (str): The base prompt
            document_content (str, optional): Document content

        Returns:
            str: Formatted prompt
        """
        pass

    async def format_synthesis_prompt(self,
                                     base_prompt: str,
                                     responses: Dict[str, Any]) -> str:
        """
        Format a synthesis prompt for this analysis pattern.

        Args:
            base_prompt (str): The base prompt
            responses (dict): LLM responses

        Returns:
            str: Synthesis prompt
        """
        pass
```

## 5. Cache Interface

Interface for response caching:

```python
class CacheInterface:
    """Interface for response caching."""

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a cached value.

        Args:
            key (str): Cache key

        Returns:
            Any: Cached value or None if not found
        """
        pass

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a cached value.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl (int, optional): Time to live in seconds
        """
        pass

    async def invalidate(self, key: str) -> None:
        """
        Invalidate a cached value.

        Args:
            key (str): Cache key to invalidate
        """
        pass
```

## 6. Configuration Interface

Interface for configuration management:

```python
class ConfigurationInterface:
    """Interface for configuration management."""

    def get_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configuration for all models.

        Returns:
            dict: Model configurations
        """
        pass

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific model.

        Args:
            model_name (str): Name of the model

        Returns:
            dict: Model configuration or None if not found
        """
        pass

    def get_default_models(self) -> List[str]:
        """
        Get the default models to use.

        Returns:
            list: Default model names
        """
        pass

    def get_default_ultra_model(self) -> str:
        """
        Get the default ultra model for synthesis.

        Returns:
            str: Default ultra model name
        """
        pass
```

## 7. Enhanced Orchestrator Interface

Extended interface for advanced orchestration:

```python
class EnhancedOrchestratorInterface(OrchestratorInterface):
    """Interface for enhanced orchestration."""

    async def process_with_document(self,
                                   prompt: str,
                                   document: Union[str, bytes, IO],
                                   analysis_pattern: Optional[str] = None,
                                   selected_models: Optional[List[str]] = None,
                                   ultra_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a prompt with an attached document.

        Args:
            prompt (str): The prompt to analyze
            document: Document content or file path
            analysis_pattern (str, optional): Analysis pattern to use
            selected_models (list, optional): Models to use for analysis
            ultra_model (str, optional): Model to use for synthesis

        Returns:
            dict: The orchestrated response
        """
        pass

    def get_available_patterns(self) -> List[str]:
        """
        Get available analysis patterns.

        Returns:
            list: Names of available patterns
        """
        pass
```

## 8. Mock Service Interface

Interface for mock functionality:

```python
class MockServiceInterface:
    """Interface for mock functionality."""

    async def generate_mock_response(self,
                                    prompt: str,
                                    model: str,
                                    provider: str) -> Dict[str, Any]:
        """
        Generate a mock response for testing.

        Args:
            prompt (str): The prompt
            model (str): Model name
            provider (str): Provider name

        Returns:
            dict: Mock response
        """
        pass

    def is_mock_enabled(self) -> bool:
        """
        Check if mock mode is enabled.

        Returns:
            bool: True if mock mode is enabled
        """
        pass
```

## Implementation Notes

1. **Interface Stability**: These interfaces establish a contract between components and should remain stable
2. **Extension Points**: New functionality should be added through interface extensions
3. **Backwards Compatibility**: Interface changes must maintain backwards compatibility where possible
4. **Documentation**: All interface implementations must include comprehensive documentation
5. **Testing**: Interface implementations should include tests against the interface contract
