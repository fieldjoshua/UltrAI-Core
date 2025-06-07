import pytest
from app.services.model_registry import ModelRegistry, ModelConfig


class DummyModelClass:
    def __init__(self, foo=None):
        self.foo = foo


@pytest.fixture
def registry():
    return ModelRegistry()


def test_register_and_create_instance(registry):
    # Register a dummy model class
    config = ModelConfig(
        name="d",
        version="v1",
        provider="p",
        max_tokens=100,
        temperature=0.5,
        timeout_seconds=10,
        rate_limit={"requests_per_minute": 5},
    )
    registry.register_model_class("d", DummyModelClass, config)
    # Create instance
    instance = registry.create_model_instance("d", foo="bar")
    assert instance.config.name == "d"
    assert isinstance(instance.instance, DummyModelClass)
    assert instance.instance.foo == "bar"
    # Fetch instance
    fetched = registry.get_model_instance("d")
    assert fetched is instance


def test_list_models_and_unregister(registry):
    config = ModelConfig(
        name="m",
        version="1",
        provider="p",
        max_tokens=50,
        temperature=0.7,
        timeout_seconds=5,
        rate_limit={"requests_per_minute": 10},
    )
    registry.register_model_class("m", DummyModelClass, config)
    registry.create_model_instance("m", foo="x")
    models = registry.list_models()
    assert any(m["name"] == "m" for m in models)
    # Unregister
    registry.unregister_model_class("m")
    with pytest.raises(ValueError):
        registry.create_model_instance("m", foo="x")


def test_update_config_and_record_usage(registry):
    config = ModelConfig(
        name="u",
        version="1",
        provider="p",
        max_tokens=20,
        temperature=0.1,
        timeout_seconds=2,
        rate_limit={"requests_per_minute": 2},
    )
    registry.register_model_class("u", DummyModelClass, config)
    registry.create_model_instance("u", foo="z")
    # Update config
    registry.update_model_config("u", {"temperature": 0.9})
    inst = registry.get_model_instance("u")
    assert inst.config.temperature == pytest.approx(0.9)
    # Record usage
    registry.record_model_usage("u", success=True)
    stats = registry.get_model_stats("u")
    assert stats["success_count"] == 1
    registry.record_model_usage("u", success=False)
    stats2 = registry.get_model_stats("u")
    assert stats2["error_count"] == 1


def test_errors_on_invalid_operations(registry):
    # get_model_instance returns None when model not registered
    assert registry.get_model_instance("nonexistent") is None
    with pytest.raises(ValueError):
        registry.get_model_stats("nonexistent")
    with pytest.raises(ValueError):
        registry.update_model_config("nonexistent", {})
    with pytest.raises(ValueError):
        registry.record_model_usage("nonexistent", success=True)
