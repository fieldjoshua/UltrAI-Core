import pytest
import json
from datetime import datetime
from src.models import ModelResponse, QualityMetrics


@pytest.fixture
def sample_quality_metrics():
    return QualityMetrics(
        coherence_score=0.8, technical_depth=0.9, strategic_value=0.85, uniqueness=0.75
    )


@pytest.fixture
def sample_model_response(sample_quality_metrics):
    return ModelResponse(
        model_name="TestModel",
        content="Test response content",
        stage="test",
        timestamp=datetime.now().timestamp(),
        tokens_used=100,
        quality=sample_quality_metrics,
        metadata={"key": "value"},
    )


def test_model_response_initialization():
    response = ModelResponse(
        model_name="TestModel",
        content="Test content",
        stage="test",
        timestamp=datetime.now().timestamp(),
    )

    assert response.model_name == "TestModel"
    assert response.content == "Test content"
    assert response.stage == "test"
    assert response.tokens_used == 0
    assert isinstance(response.quality, QualityMetrics)
    assert isinstance(response.metadata, dict)
    assert len(response.metadata) == 0


def test_model_response_with_quality(sample_model_response):
    assert sample_model_response.model_name == "TestModel"
    assert sample_model_response.content == "Test response content"
    assert sample_model_response.stage == "test"
    assert sample_model_response.tokens_used == 100
    assert sample_model_response.quality.coherence_score == 0.8
    assert sample_model_response.quality.technical_depth == 0.9
    assert sample_model_response.quality.strategic_value == 0.85
    assert sample_model_response.quality.uniqueness == 0.75
    assert sample_model_response.metadata["key"] == "value"


def test_model_response_to_json(sample_model_response):
    json_str = sample_model_response.to_json()
    data = json.loads(json_str)

    assert data["model_name"] == "TestModel"
    assert data["stage"] == "test"
    assert data["tokens_used"] == 100
    assert data["quality_scores"]["coherence"] == 0.8
    assert data["quality_scores"]["technical_depth"] == 0.9
    assert data["quality_scores"]["strategic_value"] == 0.85
    assert data["quality_scores"]["uniqueness"] == 0.75
    assert data["metadata"]["key"] == "value"


def test_model_response_timestamp():
    timestamp = datetime.now().timestamp()
    response = ModelResponse(
        model_name="TestModel",
        content="Test content",
        stage="test",
        timestamp=timestamp,
    )

    assert response.timestamp == timestamp


def test_model_response_metadata():
    metadata = {"key1": "value1", "key2": 123}
    response = ModelResponse(
        model_name="TestModel",
        content="Test content",
        stage="test",
        timestamp=datetime.now().timestamp(),
        metadata=metadata,
    )

    assert response.metadata == metadata
    assert response.metadata["key1"] == "value1"
    assert response.metadata["key2"] == 123


def test_model_response_quality_default():
    response = ModelResponse(
        model_name="TestModel",
        content="Test content",
        stage="test",
        timestamp=datetime.now().timestamp(),
    )

    assert isinstance(response.quality, QualityMetrics)
    assert response.quality.coherence_score == 0.0
    assert response.quality.technical_depth == 0.0
    assert response.quality.strategic_value == 0.0
    assert response.quality.uniqueness == 0.0
