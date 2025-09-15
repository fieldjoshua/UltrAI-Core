import pytest
from unittest.mock import Mock
from app.services.analysis_pipeline import AnalysisPipeline, AnalysisResult


class DummyModel:
    def __init__(self, model_id):
        self.model_id = model_id


@pytest.fixture
def pipeline():
    # Stub model_registry to always return one dummy model
    registry = Mock()
    registry.get_available_models = lambda task: [DummyModel("m1")]
    return AnalysisPipeline(model_registry=registry)


@pytest.mark.asyncio
async def test_process_text_default_layers(pipeline):
    text = "hello world"
    results = await pipeline.process_text(text)
    expected_layers = ["base", "meta", "ultra", "hyper"]
    assert list(results.keys()) == expected_layers
    for layer, res in results.items():
        assert isinstance(res, AnalysisResult)
        assert res.layer_name == layer
        assert res.content == text
        assert res.confidence == 1.0
        assert res.metadata["model_used"] == "m1"
        assert res.metadata["token_count"] == len(text.split())


@pytest.mark.asyncio
async def test_process_text_with_unknown_layer_skipped(pipeline):
    text = "test"
    results = await pipeline.process_text(text, layers=["unknown", "base"])
    assert "unknown" not in results
    assert "base" in results
