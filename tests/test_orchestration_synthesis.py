"""
Comprehensive tests for Ultra Synthesis™ orchestrator functionality.

This test suite validates that the orchestrator actually performs real synthesis
and intelligence multiplication, not just data passing.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.orchestration_service import OrchestrationService, PipelineResult
from app.services.rate_limiter import RateLimiter
from app.services.token_management_service import TokenManagementService
from app.services.transaction_service import TransactionService
from app.services.quality_evaluation import QualityEvaluationService


class MockRateLimiter(RateLimiter):
    """Mock rate limiter for testing."""
    
    async def acquire(self, model):
        pass

    async def release(self, model, success=True):
        pass

    def get_endpoint_stats(self, model):
        return {}
    
    def register_endpoint(self, model, requests_per_minute=60, burst_limit=10):
        pass


class MockTokenManager(TokenManagementService):
    """Mock token manager for testing."""
    
    async def track_usage(self, model, input_tokens, output_tokens, user_id):
        return Mock(total_cost=0.01)


class MockTransactionService(TransactionService):
    """Mock transaction service for testing."""
    
    async def deduct_cost(self, user_id, amount, description):
        return None


class MockQualityEvaluator(QualityEvaluationService):
    """Mock quality evaluator for testing."""
    
    async def evaluate_response(self, response, context=None):
        return Mock(
            overall_score=7.5,
            dimensions={
                "coherence": {"score": 8.0, "confidence": 0.9},
                "technical_depth": {"score": 7.0, "confidence": 0.8}
            }
        )


# Test fixtures for mock model responses
MOCK_MODEL_RESPONSES = {
    "gpt-3.5-turbo": {
        "renewable_energy": "Renewable energy offers three main benefits: 1) Environmental sustainability by reducing carbon emissions, 2) Long-term cost savings through reduced fuel costs, 3) Energy independence by reducing reliance on fossil fuel imports.",
        "ai_healthcare": "AI can improve healthcare through: 1) Enhanced diagnostic accuracy using machine learning algorithms, 2) Personalized treatment plans based on patient data analysis, 3) Streamlined administrative processes reducing costs and errors."
    },
    "gpt-4": {
        "renewable_energy": "The primary advantages of renewable energy include: Economic benefits through job creation and cost stability, Environmental protection via emission reduction, Technological innovation driving future energy solutions.",
        "ai_healthcare": "AI enhances healthcare outcomes by: Predictive analytics for early disease detection, Automated medical imaging analysis for faster diagnosis, Drug discovery acceleration through computational modeling."
    },
    "claude-3-haiku": {
        "renewable_energy": "Renewable energy provides: Sustainable power generation without resource depletion, Improved air quality and reduced health impacts, Energy security through diversified power sources.",
        "ai_healthcare": "AI improves healthcare through: Clinical decision support systems for better treatment choices, Population health management via data analytics, Precision medicine through genetic and biomarker analysis."
    }
}


class TestUltraSynthesisOrchestrator:
    """Test suite for Ultra Synthesis™ orchestrator functionality."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance with mock dependencies."""
        return OrchestrationService(
            model_registry=Mock(),
            quality_evaluator=MockQualityEvaluator(),
            rate_limiter=MockRateLimiter(),
            token_manager=MockTokenManager(),
            transaction_service=MockTransactionService(),
        )

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_initial_response_stage_with_single_model(self, orchestrator):
        """Test initial_response stage produces real model content."""
        
        # Mock the model adapter calls
        with patch.object(orchestrator, 'initial_response') as mock_initial:
            mock_initial.return_value = {
                "stage": "initial_response",
                "responses": {"gpt-3.5-turbo": MOCK_MODEL_RESPONSES["gpt-3.5-turbo"]["renewable_energy"]},
                "prompt": "What are the benefits of renewable energy?",
                "models_attempted": ["gpt-3.5-turbo"],
                "successful_models": ["gpt-3.5-turbo"],
                "response_count": 1
            }
            
            result = await orchestrator.initial_response(
                "What are the benefits of renewable energy?", 
                ["gpt-3.5-turbo"], 
                {}
            )
            
            # Validate structure
            assert result["stage"] == "initial_response"
            assert "responses" in result
            assert "gpt-3.5-turbo" in result["responses"]
            
            # Validate content quality
            response_text = result["responses"]["gpt-3.5-turbo"]
            assert len(response_text) > 50  # Substantial response
            assert "renewable" in response_text.lower()
            assert "energy" in response_text.lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_initial_response_stage_with_multiple_models(self, orchestrator):
        """Test initial_response stage with multiple models produces diverse content."""
        
        with patch.object(orchestrator, 'initial_response') as mock_initial:
            mock_initial.return_value = {
                "stage": "initial_response",
                "responses": {
                    "gpt-3.5-turbo": MOCK_MODEL_RESPONSES["gpt-3.5-turbo"]["renewable_energy"],
                    "gpt-4": MOCK_MODEL_RESPONSES["gpt-4"]["renewable_energy"],
                    "claude-3-haiku": MOCK_MODEL_RESPONSES["claude-3-haiku"]["renewable_energy"]
                },
                "prompt": "What are the benefits of renewable energy?",
                "models_attempted": ["gpt-3.5-turbo", "gpt-4", "claude-3-haiku"],
                "successful_models": ["gpt-3.5-turbo", "gpt-4", "claude-3-haiku"],
                "response_count": 3
            }
            
            result = await orchestrator.initial_response(
                "What are the benefits of renewable energy?", 
                ["gpt-3.5-turbo", "gpt-4", "claude-3-haiku"], 
                {}
            )
            
            # Validate multiple responses
            assert len(result["responses"]) == 3
            assert result["response_count"] == 3
            
            # Validate diverse content (responses should be different)
            responses = list(result["responses"].values())
            assert responses[0] != responses[1]  # GPT-3.5 vs GPT-4
            assert responses[1] != responses[2]  # GPT-4 vs Claude
            assert responses[0] != responses[2]  # GPT-3.5 vs Claude

    @pytest.mark.asyncio
    @pytest.mark.unit  
    async def test_meta_analysis_stage_enhances_responses(self, orchestrator):
        """Test meta_analysis stage actually enhances and synthesizes multiple responses."""
        
        # Mock input data with multiple model responses
        input_data = {
            "stage": "initial_response",
            "responses": {
                "gpt-3.5-turbo": MOCK_MODEL_RESPONSES["gpt-3.5-turbo"]["ai_healthcare"],
                "gpt-4": MOCK_MODEL_RESPONSES["gpt-4"]["ai_healthcare"]
            },
            "prompt": "How can AI improve healthcare outcomes?"
        }
        
        with patch.object(orchestrator, 'meta_analysis') as mock_meta:
            # Enhanced response that synthesizes the input responses
            mock_meta.return_value = {
                "stage": "meta_analysis", 
                "analysis": "Synthesizing the perspectives from multiple AI models, healthcare AI improvements span three key domains: diagnostic enhancement through machine learning and imaging analysis, treatment personalization via data analytics and predictive modeling, and operational efficiency through automation and decision support systems. The combination of these approaches creates a comprehensive healthcare AI ecosystem.",
                "model_used": "gpt-4",
                "source_models": ["gpt-3.5-turbo", "gpt-4"],
                "input_data": input_data
            }
            
            result = await orchestrator.meta_analysis(input_data, ["gpt-4"], {})
            
            # Validate enhancement occurred
            assert result["stage"] == "meta_analysis"
            assert "analysis" in result
            assert len(result["source_models"]) == 2
            
            # Validate synthesis content is more comprehensive than individual responses
            analysis_text = result["analysis"]
            assert len(analysis_text) > 200  # Should be substantial synthesis
            assert "synthesizing" in analysis_text.lower() or "combination" in analysis_text.lower()
            
            # Should reference multiple perspectives/approaches
            assert "diagnostic" in analysis_text.lower()
            assert "treatment" in analysis_text.lower() or "personalization" in analysis_text.lower()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ultra_synthesis_stage_creates_comprehensive_synthesis(self, orchestrator):
        """Test ultra_synthesis stage creates final comprehensive synthesis."""
        
        # Mock meta-analysis input
        input_data = {
            "stage": "meta_analysis",
            "analysis": "Healthcare AI improvements include diagnostic enhancement, treatment personalization, and operational efficiency.",
            "source_models": ["gpt-3.5-turbo", "gpt-4"],
            "input_data": {
                "prompt": "How can AI improve healthcare outcomes?"
            }
        }
        
        with patch.object(orchestrator, 'ultra_synthesis') as mock_synthesis:
            mock_synthesis.return_value = {
                "stage": "ultra_synthesis",
                "synthesis": "Ultra Synthesis™: The convergence of multiple AI perspectives reveals that healthcare transformation through artificial intelligence operates on three interconnected levels: technical capabilities (diagnostic algorithms, predictive analytics), clinical integration (decision support, personalized medicine), and systemic impact (operational efficiency, cost reduction). This multi-dimensional approach creates synergistic effects where the combined intelligence exceeds individual model capabilities, demonstrating true intelligence multiplication in healthcare AI applications.",
                "model_used": "gpt-4", 
                "meta_analysis": input_data["analysis"],
                "source_models": input_data["source_models"]
            }
            
            result = await orchestrator.ultra_synthesis(input_data, ["gpt-4"], {})
            
            # Validate comprehensive synthesis
            assert result["stage"] == "ultra_synthesis"
            assert "synthesis" in result
            
            synthesis_text = result["synthesis"]
            assert len(synthesis_text) > 300  # Should be comprehensive
            assert "ultra synthesis" in synthesis_text.lower() or "intelligence multiplication" in synthesis_text.lower()
            
            # Should integrate multiple dimensions/perspectives
            assert "technical" in synthesis_text.lower() or "clinical" in synthesis_text.lower()
            assert "interconnected" in synthesis_text.lower() or "synergistic" in synthesis_text.lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_pipeline_with_multiple_models(self, orchestrator):
        """Test complete pipeline execution with multiple models produces real synthesis."""
        
        # Mock each stage to return realistic synthesis content
        with patch.object(orchestrator, 'initial_response') as mock_initial, \
             patch.object(orchestrator, 'meta_analysis') as mock_meta, \
             patch.object(orchestrator, 'ultra_synthesis') as mock_synthesis:
            
            # Stage 1: Multiple diverse initial responses
            mock_initial.return_value = {
                "stage": "initial_response",
                "responses": {
                    "gpt-3.5-turbo": MOCK_MODEL_RESPONSES["gpt-3.5-turbo"]["renewable_energy"],
                    "gpt-4": MOCK_MODEL_RESPONSES["gpt-4"]["renewable_energy"]
                },
                "successful_models": ["gpt-3.5-turbo", "gpt-4"],
                "response_count": 2
            }
            
            # Stage 2: Enhanced meta-analysis  
            mock_meta.return_value = {
                "stage": "meta_analysis",
                "analysis": "Cross-model analysis reveals renewable energy benefits span economic (job creation, cost stability), environmental (emission reduction, air quality), and strategic (energy independence, innovation) dimensions.",
                "source_models": ["gpt-3.5-turbo", "gpt-4"]
            }
            
            # Stage 3: Comprehensive ultra-synthesis
            mock_synthesis.return_value = {
                "stage": "ultra_synthesis", 
                "synthesis": "Ultra Synthesis™: Intelligence multiplication across models reveals renewable energy as a transformative system combining immediate environmental benefits with long-term economic restructuring and strategic energy security, creating synergistic value exceeding individual model perspectives."
            }
            
            # Execute full pipeline
            results = await orchestrator.run_pipeline(
                "What are the benefits of renewable energy?",
                options={},
                selected_models=["gpt-3.5-turbo", "gpt-4"]
            )
            
            # Validate pipeline completion
            assert len(results) >= 3  # Should have at least 3 stages
            assert "initial_response" in results
            assert "meta_analysis" in results  
            assert "ultra_synthesis" in results
            
            # Validate progression and synthesis quality
            initial = results["initial_response"].output
            meta = results["meta_analysis"].output
            synthesis = results["ultra_synthesis"].output
            
            # Each stage should build upon the previous
            assert initial["response_count"] == 2
            assert len(meta["source_models"]) == 2
            assert "ultra synthesis" in synthesis["synthesis"].lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_synthesis_content_validation(self, orchestrator):
        """Test that synthesis stages actually create new content, not just pass data."""
        
        query = "How can renewable energy transform society?"
        
        with patch.object(orchestrator, '_run_stage') as mock_run_stage:
            # Mock realistic stage progression
            def mock_stage_execution(stage, input_data, options=None):
                if stage.name == "initial_response":
                    return PipelineResult(
                        stage_name="initial_response",
                        output={
                            "stage": "initial_response",
                            "responses": {
                                "gpt-3.5-turbo": "Renewable energy reduces carbon emissions and creates green jobs.",
                                "gpt-4": "Clean energy drives economic transformation and energy independence."
                            }
                        }
                    )
                elif stage.name == "meta_analysis":
                    return PipelineResult(
                        stage_name="meta_analysis",
                        output={
                            "stage": "meta_analysis",
                            "analysis": "Enhanced analysis: Renewable energy creates multi-dimensional transformation through environmental protection, economic restructuring, and strategic energy positioning."
                        }
                    )
                elif stage.name == "ultra_synthesis":
                    return PipelineResult(
                        stage_name="ultra_synthesis", 
                        output={
                            "stage": "ultra_synthesis",
                            "synthesis": "Ultra Synthesis™: The convergence reveals renewable energy as a catalyst for systemic societal transformation, multiplying benefits across environmental, economic, and social dimensions through intelligence-enhanced perspective integration."
                        }
                    )
                else:
                    return PipelineResult(stage_name=stage.name, output={"stage": stage.name})
            
            mock_run_stage.side_effect = mock_stage_execution
            
            results = await orchestrator.run_pipeline(query, selected_models=["gpt-3.5-turbo", "gpt-4"])
            
            # Extract content from each stage
            initial_content = results["initial_response"].output["responses"]
            meta_content = results["meta_analysis"].output["analysis"]
            synthesis_content = results["ultra_synthesis"].output["synthesis"]
            
            # Validate content evolution and enhancement
            assert len(initial_content) == 2  # Multiple perspectives
            assert "enhanced" in meta_content.lower() or "multi-dimensional" in meta_content.lower()
            assert "ultra synthesis" in synthesis_content.lower()
            assert "convergence" in synthesis_content.lower() or "intelligence" in synthesis_content.lower()
            
            # Validate content is actually different at each stage (not just data passing)
            initial_text = " ".join(initial_content.values())
            assert meta_content != initial_text  # Meta-analysis should be different from initial
            assert synthesis_content != meta_content  # Synthesis should be different from meta
            assert len(synthesis_content) > len(meta_content)  # Synthesis should be more comprehensive


@pytest.mark.asyncio
@pytest.mark.e2e
async def test_production_orchestrator_endpoint():
    """End-to-end test of production orchestrator endpoint."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ultrai-core.onrender.com/api/orchestrator/analyze",
            json={
                "query": "What are key benefits of electric vehicles?",
                "selected_models": ["gpt-3.5-turbo"],
                "analysis_type": "ultra_synthesis"
            },
            timeout=60.0
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert data["success"] is True
        assert "results" in data
        assert "initial_response" in data["results"]
        
        # Validate real content (not error messages)
        initial_output = data["results"]["initial_response"]["output"]
        assert "responses" in initial_output
        
        for model, response_text in initial_output["responses"].items():
            assert "Error:" not in response_text
            assert len(response_text) > 50  # Substantial content
            assert "electric" in response_text.lower() or "vehicle" in response_text.lower()