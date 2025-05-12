"""
Unit tests for the BaseOrchestrator.

This module contains tests for the BaseOrchestrator functionality.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.orchestration.config import OrchestratorConfig, ModelConfig, LLMProvider, RequestConfig
from src.orchestration.base_orchestrator import BaseOrchestrator, OrchestratorResponse


class TestBaseOrchestrator(unittest.TestCase):
    """Test cases for BaseOrchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test configuration
        self.model_config = ModelConfig(
            provider=LLMProvider.MOCK,
            model_id="test-model",
            is_primary=True
        )
        
        self.orch_config = OrchestratorConfig(
            models=[self.model_config],
            cache_enabled=False,
            parallel_execution=True
        )
    
    @patch('src.adapters.adapter_factory.get_adapter_for_model')
    def test_initialization(self, mock_get_adapter):
        """Test orchestrator initialization."""
        # Mock the adapter factory
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        # Create orchestrator
        orchestrator = BaseOrchestrator(self.orch_config)
        
        # Verify adapter was created
        mock_get_adapter.assert_called_once_with(self.model_config)
        
        # Verify model was registered
        self.assertEqual(len(orchestrator.model_adapters), 1)
        model_key = f"{self.model_config.provider.value}:{self.model_config.model_id}"
        self.assertIn(model_key, orchestrator.model_adapters)
        self.assertEqual(orchestrator.model_adapters[model_key], mock_adapter)
    
    @patch('src.adapters.adapter_factory.get_adapter_for_model')
    def test_add_model(self, mock_get_adapter):
        """Test adding a model to the orchestrator."""
        # Mock the adapter factory
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        # Create orchestrator
        orchestrator = BaseOrchestrator(self.orch_config)
        
        # Reset mock to verify next call
        mock_get_adapter.reset_mock()
        
        # Create new model config
        new_model = ModelConfig(
            provider=LLMProvider.MOCK,
            model_id="new-model",
            is_primary=False
        )
        
        # Add the model
        result = orchestrator.add_model(new_model)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify adapter was created
        mock_get_adapter.assert_called_once_with(new_model)
        
        # Verify model was registered
        self.assertEqual(len(orchestrator.model_adapters), 2)
        model_key = f"{new_model.provider.value}:{new_model.model_id}"
        self.assertIn(model_key, orchestrator.model_adapters)
        self.assertEqual(orchestrator.model_adapters[model_key], mock_adapter)
        
        # Verify model was added to config
        self.assertEqual(len(orchestrator.config.models), 2)
        self.assertIn(new_model, orchestrator.config.models)
    
    @patch('src.adapters.adapter_factory.get_adapter_for_model')
    def test_remove_model(self, mock_get_adapter):
        """Test removing a model from the orchestrator."""
        # Mock the adapter factory
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        # Create orchestrator
        orchestrator = BaseOrchestrator(self.orch_config)
        
        # Remove the model
        result = orchestrator.remove_model(LLMProvider.MOCK, "test-model")
        
        # Verify result
        self.assertTrue(result)
        
        # Verify model was removed from adapters
        self.assertEqual(len(orchestrator.model_adapters), 0)
        
        # Verify model was removed from config
        self.assertEqual(len(orchestrator.config.models), 0)
    
    @patch('src.adapters.adapter_factory.get_adapter_for_model')
    def test_get_available_models(self, mock_get_adapter):
        """Test getting available models."""
        # Mock the adapter factory
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        # Create orchestrator with two models
        model1 = ModelConfig(
            provider=LLMProvider.MOCK,
            model_id="model1",
            is_primary=True,
            weight=1.0
        )
        
        model2 = ModelConfig(
            provider=LLMProvider.MOCK,
            model_id="model2",
            is_primary=False,
            weight=0.5
        )
        
        config = OrchestratorConfig(
            models=[model1, model2],
            cache_enabled=False,
            parallel_execution=True
        )
        
        orchestrator = BaseOrchestrator(config)
        
        # Get available models
        models = orchestrator.get_available_models()
        
        # Verify result
        self.assertEqual(len(models), 2)
        
        self.assertEqual(models[0]["provider"], "mock")
        self.assertEqual(models[0]["model_id"], "model1")
        self.assertTrue(models[0]["is_primary"])
        self.assertEqual(models[0]["weight"], 1.0)
        
        self.assertEqual(models[1]["provider"], "mock")
        self.assertEqual(models[1]["model_id"], "model2")
        self.assertFalse(models[1]["is_primary"])
        self.assertEqual(models[1]["weight"], 0.5)
    
    @patch('src.adapters.adapter_factory.get_adapter_for_model')
    def test_execute_request(self, mock_get_adapter):
        """Test executing a request."""
        # Mock the adapter factory
        mock_adapter = MagicMock()
        mock_adapter.generate = asyncio.coroutine(lambda **kwargs: "Mock response")
        mock_get_adapter.return_value = mock_adapter
        
        # Create orchestrator
        orchestrator = BaseOrchestrator(self.orch_config)
        
        # Create request
        request = RequestConfig(prompt="Test prompt")
        
        # Execute request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(orchestrator.execute_request(request))
        loop.close()
        
        # Verify adapter was called
        mock_adapter.generate.assert_called_once()
        call_kwargs = mock_adapter.generate.call_args[1]
        self.assertEqual(call_kwargs["prompt"], "Test prompt")
        
        # Verify response
        self.assertIsInstance(response, OrchestratorResponse)
        self.assertEqual(response.content, "Mock response")
        self.assertEqual(len(response.model_responses), 1)
        
        model_key = f"{self.model_config.provider.value}:{self.model_config.model_id}"
        self.assertIn(model_key, response.model_responses)
        self.assertEqual(response.model_responses[model_key]["content"], "Mock response")
    
    @patch('src.adapters.adapter_factory.get_adapter_for_model')
    def test_execute_request_with_error(self, mock_get_adapter):
        """Test executing a request with an error."""
        # Mock the adapter factory
        mock_adapter = MagicMock()
        mock_adapter.generate = asyncio.coroutine(lambda **kwargs: (_ for _ in ()).throw(Exception("Test error")))
        mock_get_adapter.return_value = mock_adapter
        
        # Create orchestrator
        orchestrator = BaseOrchestrator(self.orch_config)
        
        # Create request
        request = RequestConfig(prompt="Test prompt")
        
        # Execute request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(orchestrator.execute_request(request))
        loop.close()
        
        # Verify adapter was called
        mock_adapter.generate.assert_called_once()
        
        # Verify error response
        self.assertIsInstance(response, OrchestratorResponse)
        self.assertEqual(response.content, "Error: All models failed to generate responses")
        self.assertEqual(len(response.model_responses), 1)
        
        model_key = f"{self.model_config.provider.value}:{self.model_config.model_id}"
        self.assertIn(model_key, response.model_responses)
        self.assertIn("error", response.model_responses[model_key])
        self.assertEqual(response.model_responses[model_key]["error"], "Test error")


if __name__ == "__main__":
    unittest.main()