"""
Contract tests for AnalysisResponse schema and fixtures consistency.
"""

import json
import os
from pathlib import Path


class TestAnalysisResponseContract:
    """Test AnalysisResponse schema compliance and fixture validity."""

    def test_schema_exists_and_valid(self):
        """Test that the JSON schema file exists and is valid JSON."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "analysis_response.schema.json"
        assert schema_path.exists(), f"Schema file not found at {schema_path}"

        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Basic schema validation
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "success" in schema["properties"]
        assert "results" in schema["properties"]
        assert "required" in schema
        assert "success" in schema["required"]
        assert "results" in schema["required"]

    def test_fixture_files_exist(self):
        """Test that all fixture files exist."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"
        expected_files = [
            "analysis_response_simple.json",
            "analysis_response_detailed.json",
            "analysis_response_error.json"
        ]

        for filename in expected_files:
            fixture_path = fixtures_dir / filename
            assert fixture_path.exists(), f"Fixture file not found: {fixture_path}"

    def test_fixtures_are_valid_json(self):
        """Test that all fixture files contain valid JSON."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        for filename in ["analysis_response_simple.json", "analysis_response_detailed.json", "analysis_response_error.json"]:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                data = json.load(f)

            # Basic structure validation
            assert isinstance(data, dict), f"Fixture {filename} is not a valid JSON object"

    def test_fixtures_match_schema_structure(self):
        """Test that fixture files match expected schema structure."""
        schema_path = Path(__file__).parent.parent.parent / "docs" / "analysis_response.schema.json"
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Test each fixture
        test_cases = [
            ("analysis_response_simple.json", True, "results"),
            ("analysis_response_detailed.json", True, "results"),
            ("analysis_response_error.json", False, None)
        ]

        for filename, should_succeed, results_key in test_cases:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                data = json.load(f)

            # All fixtures should have success field
            assert "success" in data
            assert isinstance(data["success"], bool)

            # Error fixture should have error message
            if not should_succeed:
                assert "error" in data
                assert isinstance(data["error"], str)
                assert data["error"]
            else:
                # Success fixtures should have results
                assert results_key in data
                assert isinstance(data[results_key], dict)

    def test_required_fields_present_in_fixtures(self):
        """Test that all fixtures have the required fields."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        for filename in ["analysis_response_simple.json", "analysis_response_detailed.json", "analysis_response_error.json"]:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                data = json.load(f)

            # Required fields from schema
            assert "success" in data
            assert "results" in data

            # Type validation
            assert isinstance(data["success"], bool)
            assert isinstance(data["results"], dict)

    def test_processing_time_format(self):
        """Test that processing_time is a valid number when present."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        for filename in ["analysis_response_simple.json", "analysis_response_detailed.json", "analysis_response_error.json"]:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                data = json.load(f)

            if "processing_time" in data:
                assert isinstance(data["processing_time"], (int, float))
                assert data["processing_time"] >= 0

    def test_pipeline_info_structure(self):
        """Test that pipeline_info follows expected structure when present."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        for filename in ["analysis_response_simple.json", "analysis_response_detailed.json", "analysis_response_error.json"]:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                data = json.load(f)

            if "pipeline_info" in data:
                pipeline_info = data["pipeline_info"]
                assert isinstance(pipeline_info, dict)

                # Should have correlation_id for traceability
                if "correlation_id" in pipeline_info:
                    assert isinstance(pipeline_info["correlation_id"], str)

                # Stages should be a list when present
                if "stages" in pipeline_info:
                    assert isinstance(pipeline_info["stages"], list)
                    for stage in pipeline_info["stages"]:
                        assert isinstance(stage, dict)
                        if "name" in stage:
                            assert isinstance(stage["name"], str)

    def test_error_fixture_specific_validation(self):
        """Test error fixture has proper error structure."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"
        error_path = fixtures_dir / "analysis_response_error.json"

        with open(error_path, 'r') as f:
            data = json.load(f)

        # Error fixture should fail
        assert data["success"] is False
        assert "error" in data
        assert "results" in data
        assert data["results"] == {}  # Empty results on error

        # Should have pipeline info for debugging
        assert "pipeline_info" in data
        assert "error_stage" in data["pipeline_info"]

    def test_detailed_fixture_completeness(self):
        """Test that detailed fixture includes all optional sections."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"
        detailed_path = fixtures_dir / "analysis_response_detailed.json"

        with open(detailed_path, 'r') as f:
            data = json.load(f)

        results = data["results"]

        # Should have all optional sections
        assert "initial_responses" in results
        assert "meta_analysis" in results
        assert "pipeline_summary" in results
        assert "formatted_output" in results

        # Ultra synthesis should be present
        assert "ultra_synthesis" in results

        # Check structure of complex sections
        initial_responses = results["initial_responses"]
        assert "responses" in initial_responses
        assert "model_count" in initial_responses
        assert initial_responses["model_count"] == len(initial_responses["responses"])

    def test_fixtures_consistency_across_types(self):
        """Test that common fields are consistent across fixture types."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        fixtures = {}
        for filename in ["analysis_response_simple.json", "analysis_response_detailed.json", "analysis_response_error.json"]:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                fixtures[filename] = json.load(f)

        # All fixtures should have consistent structure for common fields
        for fixture_name, data in fixtures.items():
            # Success fixtures should have results
            if data["success"]:
                assert "results" in data
                assert isinstance(data["results"], dict)

                # Processing time should be present and reasonable
                if "processing_time" in data:
                    assert data["processing_time"] > 0
                    assert data["processing_time"] < 300  # Less than 5 minutes

                # Pipeline info should be present for traceability
                if "pipeline_info" in data:
                    assert "correlation_id" in data["pipeline_info"]

    def test_no_unknown_fields_in_fixtures(self):
        """Test that fixtures don't contain unknown or deprecated fields."""
        fixtures_dir = Path(__file__).parent.parent.parent / "reports" / "samples"

        # Define allowed top-level fields from schema
        allowed_fields = {
            "success", "results", "error", "processing_time",
            "saved_files", "pipeline_info"
        }

        for filename in ["analysis_response_simple.json", "analysis_response_detailed.json", "analysis_response_error.json"]:
            fixture_path = fixtures_dir / filename
            with open(fixture_path, 'r') as f:
                data = json.load(f)

            # Check no unexpected top-level fields
            fixture_fields = set(data.keys())
            unknown_fields = fixture_fields - allowed_fields
            assert not unknown_fields, f"Unknown fields in {filename}: {unknown_fields}"