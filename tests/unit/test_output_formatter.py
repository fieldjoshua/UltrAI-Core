"""
Unit tests for OutputFormatter service.

Tests formatting of pipeline results including synthesis text, sections extraction,
and full document generation.
"""

import pytest
from app.services.output_formatter import OutputFormatter


@pytest.fixture
def formatter():
    """Create an OutputFormatter instance for testing."""
    return OutputFormatter()


@pytest.fixture
def sample_pipeline_results():
    """Sample pipeline results matching actual orchestration output."""
    return {
        "initial_response": {
            "responses": {
                "gpt-4o": "Renewable energy offers multiple benefits including reduced carbon emissions.",
                "claude-3-5-sonnet-20241022": "The advantages of renewable energy span environmental protection.",
                "gemini-1.5-pro": "Key benefits include clean energy production and job creation."
            },
            "successful_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
        },
        "peer_review_and_revision": {
            "revised_responses": {
                "gpt-4o": "Renewable energy provides crucial environmental benefits.",
                "claude-3-5-sonnet-20241022": "Comprehensive benefits include climate change mitigation.",
                "gemini-1.5-pro": "Renewable energy delivers measurable benefits with emission reductions."
            },
            "revision_count": 0
        },
        "ultra_synthesis": {
            "synthesis": "## Key Benefits\n\n1. Environmental Impact\n2. Economic Advantages\n\n## Conclusion\n\nRenewable energy is essential.",
            "model_used": "gpt-4o"
        }
    }


def test_format_pipeline_output_structure(formatter, sample_pipeline_results):
    """Test that format_pipeline_output returns expected top-level structure."""
    result = formatter.format_pipeline_output(sample_pipeline_results)
    
    assert "synthesis" in result
    assert "synthesis_model" in result
    assert "pipeline_summary" in result
    assert "full_document" in result


def test_synthesis_contains_required_fields(formatter, sample_pipeline_results):
    """Test that synthesis object contains text, sections, word_count, formatted_text."""
    result = formatter.format_pipeline_output(sample_pipeline_results)
    
    synthesis = result["synthesis"]
    assert "text" in synthesis
    assert "sections" in synthesis
    assert "word_count" in synthesis
    assert "formatted_text" in synthesis
    
    assert isinstance(synthesis["text"], str)
    assert isinstance(synthesis["sections"], list)
    assert isinstance(synthesis["word_count"], int)
    assert isinstance(synthesis["formatted_text"], str)


def test_sections_extraction(formatter, sample_pipeline_results):
    """Test that markdown sections are properly extracted."""
    result = formatter.format_pipeline_output(sample_pipeline_results)
    
    sections = result["synthesis"]["sections"]
    assert len(sections) == 2
    
    assert sections[0]["title"] == "Key Benefits"
    assert sections[0]["level"] == 2
    assert "1. Environmental Impact" in sections[0]["content"]
    
    assert sections[1]["title"] == "Conclusion"
    assert sections[1]["level"] == 2


def test_pipeline_summary_structure(formatter, sample_pipeline_results):
    """Test pipeline_summary contains stages_completed, total_models_used, success."""
    result = formatter.format_pipeline_output(sample_pipeline_results)
    
    summary = result["pipeline_summary"]
    assert "stages_completed" in summary
    assert "total_models_used" in summary
    assert "stage_count" in summary
    assert "success" in summary
    
    assert isinstance(summary["stages_completed"], list)
    assert isinstance(summary["total_models_used"], list)
    assert summary["success"] is True


def test_full_document_contains_key_sections(formatter, sample_pipeline_results):
    """Test that full_document contains expected header and sections."""
    result = formatter.format_pipeline_output(sample_pipeline_results)
    
    full_doc = result["full_document"]
    assert "ULTRA SYNTHESIS™ RESULTS" in full_doc
    assert "📊 ULTRA SYNTHESIS" in full_doc
    assert "📈 PIPELINE SUMMARY" in full_doc
    assert "Synthesized by: gpt-4o" in full_doc


def test_full_document_snapshot(formatter, sample_pipeline_results):
    """Generate snapshot of full_document for visual validation (trimmed)."""
    result = formatter.format_pipeline_output(
        sample_pipeline_results,
        include_initial_responses=True,
        include_peer_review=True,
        include_metadata=False
    )
    
    full_doc = result["full_document"]
    
    # Save snapshot (first 2000 chars for readability)
    snapshot_path = "tests/__snapshots__/output_formatter_full_document.txt"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        f.write("# OutputFormatter full_document snapshot\n")
        f.write("# Generated from test_output_formatter.py::test_full_document_snapshot\n")
        f.write("# Sample pipeline with 3 models, 3 stages\n\n")
        f.write(full_doc[:2000])
        if len(full_doc) > 2000:
            f.write(f"\n\n... (truncated {len(full_doc) - 2000} chars)")
    
    assert len(full_doc) > 200
    assert "Key Benefits" in full_doc


def test_include_initial_responses(formatter, sample_pipeline_results):
    """Test that initial_responses are included when flag is True."""
    result = formatter.format_pipeline_output(
        sample_pipeline_results,
        include_initial_responses=True
    )
    
    assert "initial_responses" in result
    initial = result["initial_responses"]
    assert "responses" in initial
    assert "model_count" in initial
    assert initial["model_count"] == 3
    assert len(initial["responses"]) == 3


def test_exclude_initial_responses(formatter, sample_pipeline_results):
    """Test that initial_responses are excluded when flag is False."""
    result = formatter.format_pipeline_output(
        sample_pipeline_results,
        include_initial_responses=False
    )
    
    assert "initial_responses" not in result


def test_include_peer_review(formatter, sample_pipeline_results):
    """Test that peer_review_responses are included when flag is True."""
    result = formatter.format_pipeline_output(
        sample_pipeline_results,
        include_peer_review=True
    )
    
    assert "peer_review_responses" in result
    peer_review = result["peer_review_responses"]
    assert "responses" in peer_review
    assert "revision_count" in peer_review


def test_handle_empty_synthesis(formatter):
    """Test handling of empty/None synthesis text."""
    pipeline_results = {
        "ultra_synthesis": {
            "synthesis": None,
            "model_used": "gpt-4o"
        }
    }
    
    result = formatter.format_pipeline_output(pipeline_results)
    assert result["synthesis"]["text"] == ""
    assert result["synthesis"]["word_count"] == 0


def test_handle_non_string_synthesis(formatter):
    """Test handling of non-string synthesis (dict/object)."""
    pipeline_results = {
        "ultra_synthesis": {
            "synthesis": {"content": "test", "metadata": {}},
            "model_used": "gpt-4o"
        }
    }
    
    result = formatter.format_pipeline_output(pipeline_results)
    assert isinstance(result["synthesis"]["text"], str)
    assert len(result["synthesis"]["text"]) > 0


def test_word_count_accuracy(formatter):
    """Test that word_count is accurate."""
    pipeline_results = {
        "ultra_synthesis": {
            "synthesis": "This is a test with exactly seven words.",
            "model_used": "gpt-4o"
        }
    }
    
    result = formatter.format_pipeline_output(pipeline_results)
    assert result["synthesis"]["word_count"] == 8
