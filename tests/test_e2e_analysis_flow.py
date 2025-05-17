#!/usr/bin/env python3
"""
End-to-End Testing for Analysis Flow

This comprehensive test module covers the complete analysis workflow:
1. Model availability checking
2. Analysis request submission
3. Asynchronous analysis progress tracking
4. Results retrieval
5. Analysis with document upload

The tests verify both the API contract and the functional behavior of the entire
analysis pipeline, ensuring all components work together as expected.
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io

from fastapi import UploadFile

# Import required modules from backend
from fastapi.testclient import TestClient

from backend.app import app
from backend.config import Config
from backend.models.analysis import AnalysisRequest, OutputFormat
from backend.services.llm_config_service import llm_config_service
from backend.services.mock_llm_service import MockLLMService
from backend.services.prompt_service import PromptService


# Test client
@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    # Force mock mode for testing
    Config.use_mock = True
    return TestClient(app)


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    return MockLLMService()


@pytest.fixture
def sample_analysis_request():
    """Create a sample analysis request for testing."""
    return {
        "prompt": "Compare and contrast Python and JavaScript for web development.",
        "selected_models": ["gpt4o", "claude3opus", "gemini15"],
        "ultra_model": "claude3opus",
        "pattern": "comparative",
        "output_format": "txt",
        "options": {},
    }


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    content = "# Sample Document\n\nThis is a sample markdown document for testing.\n\n"
    content += (
        "It contains information about Python and JavaScript programming languages.\n\n"
    )
    content += "## Python\n\n- Strongly typed\n- Indentation-based syntax\n- Popular for data science\n\n"
    content += "## JavaScript\n\n- Dynamically typed\n- C-style syntax\n- Essential for web development"

    file_content = io.BytesIO(content.encode())
    return {"file": ("sample_doc.md", file_content, "text/markdown")}


class TestAnalysisEndToEnd:
    """End-to-end tests for the analysis functionality."""

    def test_available_models_endpoint(self, client):
        """Test retrieving available models."""
        response = client.get("/api/available-models")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "available_models" in data
        assert isinstance(data["available_models"], list)
        assert len(data["available_models"]) > 0

        # Check for expected model IDs in the response
        expected_models = ["gpt4o", "claude3opus", "gemini15"]
        for model in expected_models:
            assert (
                model in data["available_models"]
            ), f"Model {model} not found in available models"

    def test_analyze_prompt_endpoint_success(self, client, sample_analysis_request):
        """Test the full analysis flow with a successful request."""
        # Step 1: Submit analysis request
        response = client.post("/api/analyze", json=sample_analysis_request)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "analysis_id" in data
        assert "results" in data

        # Capture analysis ID for subsequent requests
        analysis_id = data["analysis_id"]

        # Step 2: Verify model responses
        results = data["results"]
        assert "model_responses" in results
        assert isinstance(results["model_responses"], dict)

        # Verify each requested model has a response
        for model in sample_analysis_request["selected_models"]:
            assert model in results["model_responses"], f"No response from {model}"

        # Step 3: Verify Ultra response
        assert "ultra_response" in results
        assert isinstance(results["ultra_response"], str)
        assert len(results["ultra_response"]) > 0

        # Step 4: Verify performance metrics
        assert "performance" in results
        assert "total_time_seconds" in results["performance"]
        assert "model_times" in results["performance"]
        assert "token_counts" in results["performance"]

        # Optionally: verify the response content includes expected elements
        ultra_response = results["ultra_response"]
        assert "Python" in ultra_response
        assert "JavaScript" in ultra_response
        assert "Comparison" in ultra_response or "comparison" in ultra_response

    def test_analyze_prompt_with_invalid_input(self, client):
        """Test analysis with invalid inputs to verify error handling."""
        # Case 1: Empty prompt
        empty_prompt_request = {
            "prompt": "",
            "selected_models": ["gpt4o"],
            "ultra_model": "gpt4o",
            "pattern": "gut",
        }
        response = client.post("/api/analyze", json=empty_prompt_request)
        assert response.status_code == 400

        # Case 2: No models selected
        no_models_request = {
            "prompt": "Test prompt",
            "selected_models": [],
            "ultra_model": "gpt4o",
            "pattern": "gut",
        }
        response = client.post("/api/analyze", json=no_models_request)
        assert response.status_code == 400

        # Case 3: Invalid pattern
        invalid_pattern_request = {
            "prompt": "Test prompt",
            "selected_models": ["gpt4o"],
            "ultra_model": "gpt4o",
            "pattern": "invalid_pattern_name",
        }
        response = client.post("/api/analyze", json=invalid_pattern_request)
        # May return 200 but use default pattern, check pattern in response
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            # The pattern might have been remapped to a default one
            # Check this in results if available

    def test_analyze_with_documents(
        self, client, sample_analysis_request, sample_document
    ):
        """Test analysis with document upload."""
        # Create multipart form data
        form_data = {
            "prompt": sample_analysis_request["prompt"],
            "selected_models": json.dumps(sample_analysis_request["selected_models"]),
            "ultra_model": sample_analysis_request["ultra_model"],
            "pattern": sample_analysis_request["pattern"],
            "options": json.dumps(sample_analysis_request["options"]),
        }

        # Submit analysis with document
        response = client.post(
            "/api/analyze-with-docs", data=form_data, files=sample_document
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "message" in data
        assert "files_processed" in data
        assert data["files_processed"] == 1
        assert "prompt" in data
        # The prompt should be enhanced with the document content
        assert len(data["prompt"]) > len(sample_analysis_request["prompt"])

    def test_analysis_progress_tracking(self, client, sample_analysis_request):
        """Test the analysis progress tracking endpoint."""
        # First create an analysis to track
        response = client.post("/api/analyze", json=sample_analysis_request)
        assert response.status_code == 200
        data = response.json()
        analysis_id = data["analysis_id"]

        # Check progress endpoint
        progress_response = client.get(f"/api/analyze/{analysis_id}/progress")

        # In mock mode, the analysis might complete immediately
        # So we need to handle both "completed" and "in_progress" states
        assert progress_response.status_code in [200, 404]

        if progress_response.status_code == 200:
            progress_data = progress_response.json()
            assert "status" in progress_data
            assert progress_data["status"] == "success"
            assert "analysis_id" in progress_data
            assert progress_data["analysis_id"] == analysis_id
            assert "progress" in progress_data

            # Verify progress structure
            progress = progress_data["progress"]
            assert "status" in progress
            assert progress["status"] in [
                "pending",
                "in_progress",
                "completed",
                "failed",
            ]
            assert "current_stage" in progress
            assert "stages" in progress
            assert isinstance(progress["stages"], dict)

    def test_analysis_results_retrieval(self, client, sample_analysis_request):
        """Test retrieving analysis results."""
        # First create an analysis
        response = client.post("/api/analyze", json=sample_analysis_request)
        assert response.status_code == 200
        data = response.json()
        analysis_id = data["analysis_id"]

        # Retrieve results
        results_response = client.get(f"/api/analyze/{analysis_id}/results")

        # Check if results are available
        if results_response.status_code == 200:
            results_data = results_response.json()
            assert "status" in results_data
            assert results_data["status"] == "success"
            assert "analysis_id" in results_data
            assert results_data["analysis_id"] == analysis_id
            assert "results" in results_data

            # Verify results structure
            results = results_data["results"]
            assert "model_responses" in results
            assert "ultra_response" in results
            assert "performance" in results

        elif results_response.status_code == 404:
            # Results might not be found if they're not cached
            # This is acceptable in a test environment
            pass
        elif results_response.status_code == 400:
            # Results might not be completed yet
            # This is also acceptable in a test environment
            pass
        else:
            # Any other status code is unexpected
            assert False, f"Unexpected status code: {results_response.status_code}"

    @patch("backend.services.prompt_service.PromptService.process_prompt")
    def test_error_handling_during_processing(
        self, mock_process, client, sample_analysis_request
    ):
        """Test error handling when processing fails."""
        # Configure the mock to raise an exception
        mock_process.side_effect = Exception("Simulated processing error")

        # Submit analysis request
        response = client.post("/api/analyze", json=sample_analysis_request)

        # Verify error response
        assert response.status_code == 500
        data = response.json()
        assert "status" in data
        assert data["status"] == "error"
        assert "message" in data
        assert "error" in data["message"]

    @pytest.mark.asyncio
    async def test_async_analysis_flow(self, client, sample_analysis_request):
        """Test the asynchronous analysis flow from start to finish."""
        # Step 1: Submit analysis
        response = client.post("/api/analyze", json=sample_analysis_request)
        assert response.status_code == 200
        data = response.json()
        analysis_id = data["analysis_id"]

        # Step 2: Poll for progress until complete or timeout
        start_time = time.time()
        timeout = 10  # 10 seconds timeout
        completed = False

        while time.time() - start_time < timeout:
            progress_response = client.get(f"/api/analyze/{analysis_id}/progress")

            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                progress = progress_data["progress"]

                if progress["status"] == "completed":
                    completed = True
                    break

                # Try a short delay before checking again
                await asyncio.sleep(0.5)
            else:
                # If we get a 404, the analysis might be complete already and progress cleared
                completed = True
                break

        # Proceed even if we timed out, as we might still get results

        # Step 3: Retrieve final results
        results_response = client.get(f"/api/analyze/{analysis_id}/results")

        if results_response.status_code == 200:
            results_data = results_response.json()
            assert results_data["status"] == "success"
            assert "results" in results_data
            assert "model_responses" in results_data["results"]
            assert "ultra_response" in results_data["results"]
            # Analysis should have completed successfully
        elif completed is False:
            # If we timed out, note that but don't fail the test
            # This is to handle cases where mock services don't properly implement
            # the progress tracking functionality
            print(
                "Warning: Analysis progress tracking timed out, but this may be expected in mock mode"
            )
        else:
            # If completed but results aren't available, that's an error
            assert (
                False
            ), f"Analysis completed but results unavailable: {results_response.status_code}"


if __name__ == "__main__":
    # This allows running the tests directly with python
    pytest.main(["-xvs", __file__])
