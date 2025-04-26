import pytest
from src.core.query_processor import (
    QueryProcessor,
    QueryRequest,
    LLMModel,
    AnalysisType,
)
from src.core.model_client import ModelClientFactory


@pytest.fixture
def query_processor():
    return QueryProcessor()


@pytest.fixture
def valid_request():
    return QueryRequest(
        query="What is the capital of France?",
        selected_models=[LLMModel.GPT4, LLMModel.GPT35],
        analysis_type=AnalysisType.CONFIDENCE,
    )


@pytest.mark.asyncio
async def test_process_query_valid_request(query_processor, valid_request):
    """Test processing a valid query request"""
    response = await query_processor.process_query(valid_request)

    assert response.query == valid_request.query
    assert len(response.results) == 2
    assert LLMModel.GPT4.value in response.results
    assert LLMModel.GPT35.value in response.results
    assert response.processing_time > 0
    assert len(response.models_used) == 2


@pytest.mark.asyncio
async def test_process_query_no_models(query_processor):
    """Test processing a query with no models specified"""
    request = QueryRequest(
        query="What is the capital of France?", analysis_type=AnalysisType.CONFIDENCE
    )

    response = await query_processor.process_query(request)

    assert len(response.results) == 1
    assert LLMModel.GPT4.value in response.results


@pytest.mark.asyncio
async def test_process_query_invalid_query(query_processor):
    """Test processing an invalid query"""
    request = QueryRequest(
        query="",  # Empty query
        selected_models=[LLMModel.GPT4],
        analysis_type=AnalysisType.CONFIDENCE,
    )

    with pytest.raises(ValueError):
        await query_processor.process_query(request)


@pytest.mark.asyncio
async def test_process_query_with_context(query_processor):
    """Test processing a query with context"""
    request = QueryRequest(
        query="What is the capital?",
        selected_models=[LLMModel.GPT4],
        analysis_type=AnalysisType.CONFIDENCE,
        context="France is a country in Europe.",
    )

    response = await query_processor.process_query(request)

    assert response.query == request.query
    assert len(response.results) == 1
    assert LLMModel.GPT4.value in response.results


@pytest.mark.asyncio
async def test_analyze_results_confidence(query_processor, valid_request):
    """Test confidence analysis of results"""
    response = await query_processor.process_query(valid_request)

    assert response.analysis["type"] == "confidence"
    assert "scores" in response.analysis
    assert "average_confidence" in response.analysis
    assert response.analysis["average_confidence"] > 0


@pytest.mark.asyncio
async def test_analyze_results_comparison(query_processor):
    """Test comparison analysis of results"""
    request = QueryRequest(
        query="What is the capital of France?",
        selected_models=[LLMModel.GPT4, LLMModel.GPT35],
        analysis_type=AnalysisType.COMPARISON,
    )

    response = await query_processor.process_query(request)

    assert response.analysis["type"] == "comparison"
    assert "model_responses" in response.analysis
    assert len(response.analysis["model_responses"]) == 2


@pytest.mark.asyncio
async def test_analyze_results_summary(query_processor):
    """Test summary analysis of results"""
    request = QueryRequest(
        query="What is the capital of France?",
        selected_models=[LLMModel.GPT4],
        analysis_type=AnalysisType.SUMMARY,
    )

    response = await query_processor.process_query(request)

    assert response.analysis["type"] == "summary"
    assert "summary" in response.analysis
    assert "key_points" in response.analysis


@pytest.mark.asyncio
async def test_analyze_results_detailed(query_processor):
    """Test detailed analysis of results"""
    request = QueryRequest(
        query="What is the capital of France?",
        selected_models=[LLMModel.GPT4, LLMModel.GPT35],
        analysis_type=AnalysisType.DETAILED,
    )

    response = await query_processor.process_query(request)

    assert response.analysis["type"] == "detailed"
    assert "model_analysis" in response.analysis
    assert len(response.analysis["model_analysis"]) == 2


def test_validate_query(query_processor):
    """Test query validation"""
    assert query_processor.validate_query("Valid query")
    assert not query_processor.validate_query("")
    assert not query_processor.validate_query(" " * 1001)  # Too long


def test_select_models(query_processor):
    """Test model selection"""
    request = QueryRequest(
        query="Test query", selected_models=[LLMModel.GPT4, LLMModel.GPT35]
    )

    selected_models = query_processor.select_models(request)
    assert len(selected_models) == 2
    assert LLMModel.GPT4 in selected_models
    assert LLMModel.GPT35 in selected_models


def test_select_models_default(query_processor):
    """Test default model selection"""
    request = QueryRequest(query="Test query", selected_models=[])

    selected_models = query_processor.select_models(request)
    assert len(selected_models) == 1
    assert LLMModel.GPT4 in selected_models
