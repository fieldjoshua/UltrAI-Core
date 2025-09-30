"""
Unit tests for OutputFormatter service.
"""

import json
import pytest
from app.services.output_formatter import OutputFormatter


class TestOutputFormatter:
    """Test OutputFormatter functionality."""

    @pytest.fixture
    def formatter(self):
        """Create OutputFormatter instance."""
        return OutputFormatter()

    @pytest.fixture
    def sample_pipeline_results(self):
        """Sample pipeline results for testing."""
        return {
            "initial_response": {
                "responses": {
                    "gpt-4": "GPT-4 provides a comprehensive analysis of machine learning best practices, emphasizing the importance of data quality over algorithm selection.",
                    "claude-3-opus": "Claude's analysis focuses on the correlation between training data variety and model robustness, highlighting edge case performance issues."
                },
                "successful_models": ["gpt-4", "claude-3-opus"]
            },
            "peer_review_and_revision": {
                "revised_responses": {
                    "claude-3-opus": "After reviewing the initial responses, I can see that all models converge on data quality being the primary factor. The synthesis should balance these perspectives."
                },
                "revision_count": 1,
                "models_with_revisions": ["claude-3-opus"]
            },
            "ultra_synthesis": {
                "synthesis": "Based on the analysis of multiple AI models, the key findings indicate that machine learning algorithms perform best when trained on diverse, high-quality datasets. The most significant factor affecting model performance is the quality and variety of training data rather than the specific algorithm used.",
                "model_used": "gpt-4"
            }
        }

    def test_format_pipeline_output_basic_keys(self, formatter, sample_pipeline_results):
        """Test that formatted output contains expected keys."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        # Check top-level keys exist
        assert "synthesis" in result
        assert "synthesis_model" in result
        assert "initial_responses" in result
        assert "peer_review_responses" in result
        assert "pipeline_summary" in result
        assert "full_document" in result

    def test_synthesis_formatting(self, formatter, sample_pipeline_results):
        """Test synthesis text formatting."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        synthesis = result["synthesis"]
        assert "text" in synthesis
        assert "sections" in synthesis
        assert "word_count" in synthesis
        assert "formatted_text" in synthesis

        # Check word count is reasonable
        assert synthesis["word_count"] > 0
        assert synthesis["word_count"] == len(synthesis["text"].split())

    def test_initial_responses_formatting(self, formatter, sample_pipeline_results):
        """Test initial responses formatting."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        initial = result["initial_responses"]
        assert "responses" in initial
        assert "model_count" in initial
        assert "successful_models" in initial

        assert initial["model_count"] == 2
        assert "gpt-4" in initial["responses"]
        assert "claude-3-opus" in initial["responses"]

        # Check response structure
        gpt4_response = initial["responses"]["gpt-4"]
        assert "text" in gpt4_response
        assert "word_count" in gpt4_response
        assert "preview" in gpt4_response

    def test_peer_review_formatting(self, formatter, sample_pipeline_results):
        """Test peer review responses formatting."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        peer_review = result["peer_review_responses"]
        assert "responses" in peer_review
        assert "revision_count" in peer_review
        assert "models_with_revisions" in peer_review

        assert peer_review["revision_count"] == 1
        assert "claude-3-opus" in peer_review["responses"]

    def test_pipeline_summary_formatting(self, formatter, sample_pipeline_results):
        """Test pipeline summary formatting."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        summary = result["pipeline_summary"]
        assert "stages_completed" in summary
        assert "total_models_used" in summary
        assert "stage_count" in summary
        assert "success" in summary

        assert len(summary["stages_completed"]) == 3
        assert len(summary["total_models_used"]) == 2
        assert summary["stage_count"] == 3
        assert summary["success"] is True

    def test_full_document_structure(self, formatter, sample_pipeline_results):
        """Test full document contains expected sections."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        full_doc = result["full_document"]

        # Check for expected section headers
        assert "🌟 ULTRA SYNTHESIS™ RESULTS 🌟" in full_doc
        assert "📊 ULTRA SYNTHESIS" in full_doc
        assert "🎯 INITIAL RESPONSES" in full_doc
        assert "📈 PIPELINE SUMMARY" in full_doc

        # Check for model names
        assert "gpt-4" in full_doc
        assert "claude-3-opus" in full_doc

    def test_full_document_snapshot(self, formatter, sample_pipeline_results):
        """Test full document matches expected snapshot."""
        result = formatter.format_pipeline_output(sample_pipeline_results)

        full_doc = result["full_document"]

        # Normalize whitespace for comparison
        normalized_doc = "\n".join(line.rstrip() for line in full_doc.split("\n"))

        # Read expected snapshot
        snapshot_path = "/workspace/tests/__snapshots__/output_formatter_full_document.txt"
        try:
            with open(snapshot_path, 'r') as f:
                expected = f.read().strip()
        except FileNotFoundError:
            # Create snapshot if it doesn't exist
            with open(snapshot_path, 'w') as f:
                f.write(normalized_doc)
            expected = normalized_doc

        assert normalized_doc == expected

    def test_empty_pipeline_results(self, formatter):
        """Test formatting with empty pipeline results."""
        result = formatter.format_pipeline_output({})

        assert "synthesis" in result
        assert "synthesis_model" in result
        assert "pipeline_summary" in result
        assert "full_document" in result

        # Empty synthesis should have empty text
        assert result["synthesis"]["text"] == ""

    def test_missing_stages_handling(self, formatter):
        """Test handling of missing pipeline stages."""
        incomplete_results = {
            "ultra_synthesis": {
                "synthesis": "Only ultra synthesis available.",
                "model_used": "gpt-4"
            }
        }

        result = formatter.format_pipeline_output(incomplete_results)

        # Should still format what exists
        assert "synthesis" in result
        assert "pipeline_summary" in result

        # Summary should reflect only completed stages
        summary = result["pipeline_summary"]
        assert "ultra_synthesis" in summary["stages_completed"]
        assert summary["stage_count"] == 1