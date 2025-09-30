"""
Contract tests for AnalysisResponse to detect schema drift.

These tests validate that backend responses match the defined schema
and that sample JSON files remain consistent with the contract.
"""

import json
import pytest
from pathlib import Path


def load_json(file_path: str) -> dict:
    """Load JSON file from path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_schema() -> dict:
    """Load the analysis_response JSON schema."""
    schema_path = Path(__file__).parent.parent.parent / "docs" / "analysis_response.schema.json"
    return load_json(str(schema_path))


def load_sample(sample_name: str) -> dict:
    """Load a sample JSON file."""
    sample_path = Path(__file__).parent.parent.parent / "reports" / "samples" / f"analysis_response_{sample_name}.json"
    return load_json(str(sample_path))


class TestAnalysisResponseContract:
    """Test suite for AnalysisResponse contract validation."""
    
    def test_schema_file_exists(self):
        """Ensure the schema file exists and is valid JSON."""
        schema = load_schema()
        assert schema is not None
        assert "$schema" in schema
        assert schema["title"] == "AnalysisResponse"
    
    def test_schema_required_fields(self):
        """Validate schema has required top-level fields defined."""
        schema = load_schema()
        properties = schema.get("properties", {})
        
        assert "success" in properties
        assert "results" in properties
        assert "error" in properties
        assert "processing_time" in properties
        assert "pipeline_info" in properties
    
    def test_simple_sample_structure(self):
        """Validate simple.json matches required contract fields."""
        sample = load_sample("simple")
        
        assert "success" in sample
        assert "results" in sample
        assert sample["success"] is True
        
        results = sample["results"]
        assert "ultra_synthesis" in results or "formatted_synthesis" in results
        assert "status" in results
        assert results["status"] == "completed"
    
    def test_detailed_sample_structure(self):
        """Validate detailed.json includes all pipeline stages."""
        sample = load_sample("detailed")
        
        assert sample["success"] is True
        results = sample["results"]
        
        assert "initial_response" in results or "formatted_output" in results
        
        if "formatted_output" in results:
            formatted = results["formatted_output"]
            assert "synthesis" in formatted
            assert "pipeline_summary" in formatted
            
            synthesis = formatted["synthesis"]
            assert "text" in synthesis
            assert "sections" in synthesis
            assert isinstance(synthesis["sections"], list)
    
    def test_error_sample_structure(self):
        """Validate error.json includes error fields and success=false."""
        sample = load_sample("error")
        
        assert sample["success"] is False
        assert "error" in sample or ("results" in sample and "error" in sample["results"])
        
        if "results" in sample:
            assert sample["results"]["status"] == "failed"
    
    def test_pipeline_info_shape(self):
        """Validate pipeline_info has expected structure across samples."""
        for sample_name in ["simple", "detailed", "error"]:
            sample = load_sample(sample_name)
            
            if "pipeline_info" in sample and sample["pipeline_info"]:
                pipeline_info = sample["pipeline_info"]
                
                assert "stages_completed" in pipeline_info
                assert isinstance(pipeline_info["stages_completed"], list)
                
                assert "total_stages" in pipeline_info
                assert isinstance(pipeline_info["total_stages"], int)
                
                assert "models_used" in pipeline_info
                assert isinstance(pipeline_info["models_used"], list)
    
    def test_synthesis_field_consistency(self):
        """Ensure synthesis fields are strings or dicts, never null in success case."""
        simple = load_sample("simple")
        detailed = load_sample("detailed")
        
        if simple["success"]:
            assert "ultra_synthesis" in simple["results"] or "formatted_synthesis" in simple["results"]
            synthesis = simple["results"].get("ultra_synthesis") or simple["results"].get("formatted_synthesis")
            assert synthesis is not None
            assert isinstance(synthesis, (str, dict))
        
        if detailed["success"] and "formatted_output" in detailed["results"]:
            formatted = detailed["results"]["formatted_output"]
            assert "synthesis" in formatted
            assert "text" in formatted["synthesis"]
            assert isinstance(formatted["synthesis"]["text"], str)
    
    def test_processing_time_type(self):
        """Validate processing_time is numeric when present."""
        for sample_name in ["simple", "detailed", "error"]:
            sample = load_sample(sample_name)
            
            if "processing_time" in sample and sample["processing_time"] is not None:
                assert isinstance(sample["processing_time"], (int, float))
                assert sample["processing_time"] > 0
    
    def test_no_unexpected_null_values_in_success(self):
        """Ensure critical fields are not null when success=true."""
        simple = load_sample("simple")
        
        if simple["success"]:
            assert simple["results"] is not None
            assert simple["results"].get("status") is not None
            assert "ultra_synthesis" in simple["results"] or "formatted_synthesis" in simple["results"]
    
    def test_error_message_present_on_failure(self):
        """Ensure error messages exist when success=false."""
        error_sample = load_sample("error")
        
        assert error_sample["success"] is False
        
        has_top_level_error = error_sample.get("error") is not None
        has_results_error = (
            "results" in error_sample 
            and error_sample["results"] is not None 
            and error_sample["results"].get("error") is not None
        )
        
        assert has_top_level_error or has_results_error, \
            "Error sample must have error message in 'error' or 'results.error'"
    
    def test_stages_completed_valid_values(self):
        """Validate stages_completed contains known stage names."""
        valid_stages = {
            "initial_response",
            "peer_review_and_revision",
            "ultra_synthesis",
            "meta_analysis"
        }
        
        for sample_name in ["simple", "detailed", "error"]:
            sample = load_sample(sample_name)
            
            if "pipeline_info" in sample and sample["pipeline_info"]:
                stages = sample["pipeline_info"]["stages_completed"]
                for stage in stages:
                    assert stage in valid_stages, \
                        f"Unknown stage '{stage}' in {sample_name}.json"
    
    def test_models_used_non_empty_on_success(self):
        """Ensure models_used list is not empty when analysis succeeds."""
        for sample_name in ["simple", "detailed"]:
            sample = load_sample(sample_name)
            
            if sample["success"] and "pipeline_info" in sample:
                models = sample["pipeline_info"]["models_used"]
                assert len(models) > 0, \
                    f"models_used should not be empty in {sample_name}.json"


class TestFrontendFixtureContract:
    """Validate frontend fixtures match backend sample contract."""
    
    def load_frontend_fixture(self, fixture_name: str) -> dict:
        """Load frontend fixture JSON."""
        fixture_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "__fixtures__" / "orchestration" / f"{fixture_name}.json"
        return load_json(str(fixture_path))
    
    def test_frontend_simple_matches_backend(self):
        """Ensure frontend simple.json has same structure as backend."""
        frontend = self.load_frontend_fixture("simple")
        backend = load_sample("simple")
        
        assert frontend["success"] == backend["success"]
        assert "results" in frontend
        assert "ultra_synthesis" in frontend["results"] or "formatted_synthesis" in frontend["results"]
    
    def test_frontend_detailed_matches_backend(self):
        """Ensure frontend detailed.json has same structure as backend."""
        frontend = self.load_frontend_fixture("detailed")
        backend = load_sample("detailed")
        
        assert frontend["success"] == backend["success"]
        assert "results" in frontend
        
        if "formatted_output" in backend["results"]:
            assert "formatted_output" in frontend["results"] or "initial_response" in frontend["results"]
    
    def test_frontend_error_matches_backend(self):
        """Ensure frontend error.json has same structure as backend."""
        frontend = self.load_frontend_fixture("error")
        backend = load_sample("error")
        
        assert frontend["success"] == backend["success"] == False
        assert "error" in frontend or "error" in frontend["results"]
    
    def test_frontend_fixtures_have_pipeline_info(self):
        """Validate all frontend fixtures include pipeline_info."""
        for fixture_name in ["simple", "detailed", "error"]:
            fixture = self.load_frontend_fixture(fixture_name)
            assert "pipeline_info" in fixture, \
                f"Frontend {fixture_name}.json missing pipeline_info"


class TestSchemaEvolution:
    """Tests to catch breaking changes in schema evolution."""
    
    def test_backward_compatibility_success_field(self):
        """Ensure 'success' field remains a boolean."""
        for sample_name in ["simple", "detailed", "error"]:
            sample = load_sample(sample_name)
            assert isinstance(sample["success"], bool)
    
    def test_backward_compatibility_results_field(self):
        """Ensure 'results' field remains an object."""
        for sample_name in ["simple", "detailed", "error"]:
            sample = load_sample(sample_name)
            assert isinstance(sample["results"], dict)
    
    def test_no_breaking_changes_to_simple_mode(self):
        """Ensure simple mode response shape hasn't changed."""
        sample = load_sample("simple")
        
        assert "success" in sample
        assert "results" in sample
        assert "processing_time" in sample
        assert "pipeline_info" in sample
        
        results = sample["results"]
        assert "status" in results
        assert "ultra_synthesis" in results or "formatted_synthesis" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
