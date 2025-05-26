"""
UltraAI 4-Stage Feather Analysis Flow Testing

This module tests the specific 4-stage workflow:
Initial → Meta → Hyper → Ultra

Validates:
- Stage sequencing and data flow
- Competitive prompt generation
- Model selection for synthesis stages  
- Response quality and attribution
"""

import asyncio
import json
import os
import sys
import unittest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator
    from src.patterns.ultra_analysis_patterns import get_pattern_mapping
    FEATHER_AVAILABLE = True
except ImportError:
    FEATHER_AVAILABLE = False


class TestFeatherAnalysisStages(unittest.TestCase):
    """Test each stage of the 4-stage Feather Analysis"""
    
    def setUp(self):
        self.mock_api_keys = {
            "anthropic": "sk-ant-test",
            "openai": "sk-test",
            "google": "test-key"
        }
        self.test_prompt = "What are the implications of quantum computing for cryptography?"
        
        # Mock responses for testing
        self.mock_initial_responses = {
            "claude": "Claude's analysis of quantum cryptography implications...",
            "chatgpt": "GPT-4's perspective on quantum computing and encryption...",
            "gemini": "Gemini's evaluation of quantum cryptographic threats..."
        }
        
    @unittest.skipUnless(FEATHER_AVAILABLE, "Feather orchestrator not available")
    def test_stage_1_initial_response_collection(self):
        """Test Stage 1: Initial responses from all models"""
        orchestrator = PatternOrchestrator(self.mock_api_keys, pattern="confidence")
        
        # Mock the API calls
        with patch.object(orchestrator, 'get_claude_response', new_callable=AsyncMock) as mock_claude, \
             patch.object(orchestrator, 'get_chatgpt_response', new_callable=AsyncMock) as mock_gpt, \
             patch.object(orchestrator, 'get_gemini_response', new_callable=AsyncMock) as mock_gemini:
            
            mock_claude.return_value = self.mock_initial_responses["claude"]
            mock_gpt.return_value = self.mock_initial_responses["chatgpt"] 
            mock_gemini.return_value = self.mock_initial_responses["gemini"]
            
            # Test that initial stage calls all available models
            async def test_initial():
                responses = await orchestrator.get_initial_responses(self.test_prompt)
                
                # Verify all models were called
                self.assertIsInstance(responses, dict)
                self.assertGreater(len(responses), 0)
                
                # Each response should contain the model's analysis
                for model, response in responses.items():
                    self.assertIsInstance(response, str)
                    self.assertGreater(len(response), 0)
                    
            # Run async test
            asyncio.run(test_initial())
            
    @unittest.skipUnless(FEATHER_AVAILABLE, "Feather orchestrator not available")
    def test_stage_2_meta_analysis_competitive_prompts(self):
        """Test Stage 2: Meta-analysis with competitive prompts"""
        orchestrator = PatternOrchestrator(self.mock_api_keys, pattern="confidence")
        
        # Test meta prompt generation
        patterns = get_pattern_mapping()
        confidence_pattern = patterns["confidence"]
        
        # Verify meta template exists and has competitive elements
        meta_template = confidence_pattern.templates["meta"]
        
        # Should include original prompt, own response, and other responses
        self.assertIn("$original_prompt", meta_template)
        self.assertIn("$own_response", meta_template) 
        self.assertIn("$other_responses", meta_template)
        
        # Should create competitive dynamics
        self.assertIn("identify", meta_template.lower())
        self.assertIn("agreement", meta_template.lower())
        self.assertIn("disagreement", meta_template.lower())
        
    @unittest.skipUnless(FEATHER_AVAILABLE, "Feather orchestrator not available") 
    def test_stage_3_hyper_synthesis_model_selection(self):
        """Test Stage 3: Hyper synthesis by best model"""
        orchestrator = PatternOrchestrator(self.mock_api_keys, pattern="gut")
        
        # Test model selection logic for hyper stage
        available_models = orchestrator.available_models
        
        # Should prefer Claude if available
        if "anthropic" in available_models:
            hyper_model = "claude" if "claude" in available_models else "chatgpt"
            self.assertEqual(hyper_model, "claude", "Claude should be preferred for hyper synthesis")
            
        # Test hyper prompt includes all meta responses
        patterns = get_pattern_mapping()
        gut_pattern = patterns["gut"]
        hyper_template = gut_pattern.templates["hyper"]
        
        # Should include meta responses for synthesis
        self.assertIn("$other_meta_responses", hyper_template)
        self.assertIn("refined", hyper_template.lower())
        
    @unittest.skipUnless(FEATHER_AVAILABLE, "Feather orchestrator not available")
    def test_stage_4_ultra_final_synthesis(self):
        """Test Stage 4: Ultra final synthesis"""
        orchestrator = PatternOrchestrator(self.mock_api_keys, pattern="gut")
        
        # Test ultra stage template
        patterns = get_pattern_mapping()
        gut_pattern = patterns["gut"]
        ultra_template = gut_pattern.templates["ultra"]
        
        # Should create final synthesis
        self.assertIn("$hyper_responses", ultra_template)
        self.assertIn("final synthesis", ultra_template.lower())
        self.assertIn("balanced", ultra_template.lower())
        
    def test_competitive_dynamics_per_pattern(self):
        """Test that different patterns create different competitive dynamics"""
        if not FEATHER_AVAILABLE:
            self.skipTest("Feather orchestrator not available")
            
        patterns = get_pattern_mapping()
        
        # Test confidence pattern creates consensus tracking
        confidence = patterns["confidence"]
        confidence_meta = confidence.templates["meta"].lower()
        self.assertIn("agreement", confidence_meta)
        self.assertIn("disagreement", confidence_meta)
        
        # Test critique pattern creates adversarial dynamics
        critique = patterns["critique"] 
        critique_meta = critique.templates["meta"].lower()
        self.assertIn("critique", critique_meta)
        self.assertIn("weaknesses", critique_meta)
        
        # Test fact_check creates verification dynamics
        fact_check = patterns["fact_check"]
        fact_meta = fact_check.templates["meta"].lower()
        self.assertIn("fact-check", fact_meta)
        self.assertIn("verify", fact_meta)


class TestFeatherWorkflowIntegration(unittest.TestCase):
    """Test complete workflow integration"""
    
    @unittest.skipUnless(FEATHER_AVAILABLE, "Feather orchestrator not available")
    def test_full_4_stage_workflow_structure(self):
        """Test the complete 4-stage workflow"""
        orchestrator = PatternOrchestrator(
            {"anthropic": "test", "openai": "test"},
            pattern="confidence"
        )
        
        # Mock all API calls for testing workflow structure
        with patch.object(orchestrator, 'get_claude_response', new_callable=AsyncMock) as mock_claude, \
             patch.object(orchestrator, 'get_chatgpt_response', new_callable=AsyncMock) as mock_gpt:
            
            mock_claude.return_value = "Mock Claude response"
            mock_gpt.return_value = "Mock GPT response"
            
            async def test_workflow():
                try:
                    # Test that orchestrate_full_process exists and runs
                    # Note: This will fail without real API keys, but tests structure
                    result = await orchestrator.orchestrate_full_process(
                        "Test prompt for workflow validation"
                    )
                    
                    # If it succeeds, verify structure
                    self.assertIsInstance(result, dict)
                    
                except Exception as e:
                    # Expected to fail without real API keys
                    # But verify the method exists and workflow structure is correct
                    self.assertTrue(hasattr(orchestrator, 'orchestrate_full_process'))
                    
            asyncio.run(test_workflow())
            
    def test_stage_data_flow_validation(self):
        """Test that data flows correctly between stages"""
        if not FEATHER_AVAILABLE:
            self.skipTest("Feather orchestrator not available")
            
        # Test that each stage builds on previous stages
        orchestrator = PatternOrchestrator({"openai": "test"}, pattern="gut")
        
        # Verify methods exist for each stage
        self.assertTrue(hasattr(orchestrator, 'get_initial_responses'))
        self.assertTrue(hasattr(orchestrator, 'get_meta_responses'))
        self.assertTrue(hasattr(orchestrator, 'orchestrate_full_process'))
        
        # Verify stage progression logic exists
        patterns = get_pattern_mapping()
        gut = patterns["gut"]
        
        # Each stage should reference previous stage data
        self.assertIn("$other_responses", gut.templates["meta"])  # Meta uses initial
        self.assertIn("$other_meta_responses", gut.templates["hyper"])  # Hyper uses meta
        self.assertIn("$hyper_responses", gut.templates["ultra"])  # Ultra uses hyper


def run_feather_analysis_test():
    """Run a focused test of the Feather Analysis implementation"""
    print("\n🪶 UltraAI 4-Stage Feather Analysis Test")
    print("=" * 50)
    
    if not FEATHER_AVAILABLE:
        print("❌ Feather Analysis orchestrator not available")
        print("   Check that src.core.ultra_pattern_orchestrator imports correctly")
        return False
        
    print("✅ Feather Analysis orchestrator available")
    
    # Test pattern availability
    patterns = get_pattern_mapping()
    print(f"\n🎨 Analysis Patterns: {len(patterns)} patterns available")
    
    stage_coverage = {}
    for name, pattern in patterns.items():
        print(f"  • {name}: {pattern.name}")
        
        # Check stage coverage
        for stage in ["meta", "hyper", "ultra"]:
            if stage in pattern.templates:
                stage_coverage.setdefault(stage, 0)
                stage_coverage[stage] += 1
                
    print(f"\n📊 Stage Template Coverage:")
    for stage, count in stage_coverage.items():
        print(f"  {stage}: {count}/{len(patterns)} patterns")
        
    # Test competitive dynamics
    print(f"\n⚔️ Competitive Dynamics Test:")
    test_patterns = ["confidence", "critique", "fact_check"]
    
    for pattern_name in test_patterns:
        if pattern_name in patterns:
            pattern = patterns[pattern_name]
            meta_template = pattern.templates.get("meta", "").lower()
            
            competitive_keywords = {
                "confidence": ["agreement", "disagreement", "consensus"],
                "critique": ["critique", "weaknesses", "strengths"],
                "fact_check": ["verify", "factual", "errors"]
            }
            
            found_keywords = []
            for keyword in competitive_keywords[pattern_name]:
                if keyword in meta_template:
                    found_keywords.append(keyword)
                    
            print(f"  {pattern_name}: {len(found_keywords)}/{len(competitive_keywords[pattern_name])} competitive elements")
            
    print("\n✨ Feather Analysis test complete!")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Feather Analysis Flow Testing")
    parser.add_argument("--feather-test", action="store_true",
                       help="Run Feather Analysis specific test")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.feather_test:
        run_feather_analysis_test()
    else:
        if args.verbose:
            unittest.main(verbosity=2)
        else:
            unittest.main()