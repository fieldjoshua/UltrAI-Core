"""
Unit tests for the ModelRegistry service.
"""

import pytest
from datetime import datetime

from app.services.model_registry import ModelRegistry, ModelConfig, ModelInstance


class MockModel:
    """Mock model class for testing."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs


@pytest.fixture
def model_registry():
    """Create a ModelRegistry instance for testing."""
    return ModelRegistry()


@pytest.fixture
def sample_config():
    """Create a sample model configuration."""
    return ModelConfig(
        name="test-model",
        version="1.0.0",
        provider="test-provider",
        max_tokens=2048,
        temperature=0.7,
        timeout_seconds=30,
        rate_limit={"requests_per_minute": 60},
    )


def test_register_model_class(model_registry, sample_config):
    """Test registering a model class."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    assert "test-model" in model_registry._model_classes  # noqa: S101
    assert model_registry._model_classes["test-model"] == MockModel  # noqa: S101


def test_register_duplicate_model_class(model_registry, sample_config):
    """Test registering a duplicate model class."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    with pytest.raises(
        ValueError, match="Model class test-model is already registered"
    ):
        model_registry.register_model_class("test-model", MockModel, sample_config)


def test_unregister_model_class(model_registry, sample_config):
    """Test unregistering a model class."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    model_registry.unregister_model_class("test-model")
    assert "test-model" not in model_registry._model_classes  # noqa: S101


def test_unregister_nonexistent_model_class(model_registry):
    """Test unregistering a nonexistent model class."""
    with pytest.raises(ValueError, match="Model class test-model is not registered"):
        model_registry.unregister_model_class("test-model")


def test_create_model_instance(model_registry, sample_config):
    """Test creating a model instance."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    instance = model_registry.create_model_instance("test-model", version="2.0.0")

    assert "test-model" in model_registry._models  # noqa: S101
    assert isinstance(instance, ModelInstance)  # noqa: S101
    assert instance.config.name == "test-model"  # noqa: S101
    assert instance.config.version == "2.0.0"  # noqa: S101
    assert isinstance(instance.instance, MockModel)  # noqa: S101


def test_create_instance_nonexistent_model(model_registry):
    """Test creating an instance of a nonexistent model."""
    with pytest.raises(ValueError, match="Model class test-model is not registered"):
        model_registry.create_model_instance("test-model")


def test_get_model_instance(model_registry, sample_config):
    """Test getting a model instance."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    created = model_registry.create_model_instance("test-model")
    retrieved = model_registry.get_model_instance("test-model")

    assert retrieved == created  # noqa: S101
    assert retrieved is not None  # noqa: S101


def test_get_nonexistent_model_instance(model_registry):
    """Test getting a nonexistent model instance."""
    assert model_registry.get_model_instance("test-model") is None  # noqa: S101


def test_list_models(model_registry, sample_config):
    """Test listing all models."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    model_registry.create_model_instance("test-model")

    models = model_registry.list_models()
    assert len(models) == 1  # noqa: S101
    assert models[0]["name"] == "test-model"  # noqa: S101
    assert models[0]["config"]["name"] == "test-model"  # noqa: S101
    assert models[0]["error_count"] == 0  # noqa: S101
    assert models[0]["success_count"] == 0  # noqa: S101


def test_update_model_config(model_registry, sample_config):
    """Test updating model configuration."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    model_registry.create_model_instance("test-model")

    updates = {"temperature": 0.5, "max_tokens": 4096}
    model_registry.update_model_config("test-model", updates)

    instance = model_registry.get_model_instance("test-model")
    assert instance is not None  # noqa: S101
    assert instance.config.temperature == 0.5  # noqa: S101
    assert instance.config.max_tokens == 4096  # noqa: S101


def test_update_nonexistent_model_config(model_registry):
    """Test updating configuration of a nonexistent model."""
    with pytest.raises(ValueError, match="Model test-model is not registered"):
        model_registry.update_model_config("test-model", {"temperature": 0.5})


def test_record_model_usage(model_registry, sample_config):
    """Test recording model usage statistics."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    model_registry.create_model_instance("test-model")

    # Record successful usage
    model_registry.record_model_usage("test-model", True)
    instance = model_registry.get_model_instance("test-model")
    assert instance is not None  # noqa: S101
    assert instance.success_count == 1  # noqa: S101
    assert instance.error_count == 0  # noqa: S101
    assert instance.last_used is not None  # noqa: S101

    # Record failed usage
    model_registry.record_model_usage("test-model", False)
    instance = model_registry.get_model_instance("test-model")
    assert instance is not None  # noqa: S101
    assert instance.success_count == 1  # noqa: S101
    assert instance.error_count == 1  # noqa: S101


def test_record_usage_nonexistent_model(model_registry):
    """Test recording usage for a nonexistent model."""
    with pytest.raises(ValueError, match="Model test-model is not registered"):
        model_registry.record_model_usage("test-model", True)


def test_get_model_stats(model_registry, sample_config):
    """Test getting model usage statistics."""
    model_registry.register_model_class("test-model", MockModel, sample_config)
    model_registry.create_model_instance("test-model")

    # Record some usage
    model_registry.record_model_usage("test-model", True)
    model_registry.record_model_usage("test-model", False)

    stats = model_registry.get_model_stats("test-model")
    assert stats["success_count"] == 1  # noqa: S101
    assert stats["error_count"] == 1  # noqa: S101
    assert "last_used" in stats  # noqa: S101
    assert isinstance(stats["last_used"], datetime)  # noqa: S101


def test_get_stats_nonexistent_model(model_registry):
    """Test getting statistics for a nonexistent model."""
    with pytest.raises(ValueError, match="Model test-model is not registered"):
        model_registry.get_model_stats("test-model")
