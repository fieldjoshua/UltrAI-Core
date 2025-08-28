#!/usr/bin/env python3
"""
Test script to verify Ultra Synthesis orchestration flow
Can be run locally or against production
"""

import json
import requests
import os
import sys
from typing import Dict, Any, List

# Configuration
API_URL = os.getenv("API_URL", "https://ultrai-core.onrender.com/api")
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

def test_orchestration_flow():
    """Test the complete orchestration flow"""
    
    print(f"🔍 Testing orchestration flow against: {API_URL}")
    print(f"📊 Mock mode: {USE_MOCK}")
    
    # Test payload
    payload = {
        "query": "What are the key differences between Python and JavaScript for web development?",
        "selected_models": ["gpt-4o", "claude-3-sonnet", "gemini-pro"],
        "options": {
            "pattern": "gut",
            "include_pipeline_details": True  # Get full pipeline details
        }
    }
    
    print("\n📤 Sending orchestration request...")
    print(f"Query: {payload['query']}")
    print(f"Models: {', '.join(payload['selected_models'])}")
    
    try:
        response = requests.post(
            f"{API_URL}/orchestrator/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120.0
        )
        
        print(f"\n📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            analyze_response(data)
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def analyze_response(data: Dict[str, Any]):
    """Analyze the orchestration response"""
    
    print("\n📊 Response Analysis:")
    print(f"Success: {data.get('success', False)}")
    print(f"Processing time: {data.get('processing_time', 0):.2f}s")
    
    if data.get('error'):
        print(f"❌ Error: {data['error']}")
        return
    
    # Check pipeline info
    pipeline_info = data.get('pipeline_info', {})
    print(f"\n🔄 Pipeline Information:")
    print(f"Stages completed: {', '.join(pipeline_info.get('stages_completed', []))}")
    print(f"Total stages: {pipeline_info.get('total_stages', 0)}")
    print(f"Models used: {', '.join(pipeline_info.get('models_used', []))}")
    
    # Analyze results
    results = data.get('results', {})
    
    # Check initial responses
    if 'initial_response' in results:
        initial = results['initial_response']
        print(f"\n1️⃣ Initial Response Stage:")
        if isinstance(initial, dict):
            output = initial.get('output', {})
            if isinstance(output, dict):
                responses = output.get('responses', {})
                successful = output.get('successful_models', [])
                print(f"   Models attempted: {output.get('models_attempted', [])}")
                print(f"   Successful models: {successful}")
                print(f"   Response count: {len(responses)}")
                
                # Show sample responses
                for model, response in list(responses.items())[:2]:
                    sample = str(response)[:100] + "..." if len(str(response)) > 100 else str(response)
                    print(f"   {model}: {sample}")
    
    # Check peer review stage
    if 'peer_review_and_revision' in results:
        peer_review = results['peer_review_and_revision']
        print(f"\n2️⃣ Peer Review Stage:")
        if isinstance(peer_review, dict):
            output = peer_review.get('output', {})
            if isinstance(output, dict):
                print(f"   Status: {peer_review.get('status', 'unknown')}")
                revised = output.get('revised_responses', {})
                print(f"   Revised response count: {len(revised)}")
    
    # Check ultra synthesis
    if 'ultra_synthesis' in results:
        ultra = results['ultra_synthesis']
        print(f"\n3️⃣ Ultra Synthesis Stage:")
        if isinstance(ultra, dict):
            if ultra.get('error'):
                print(f"   ❌ Error: {ultra['error']}")
            else:
                output = ultra.get('output', ultra)
                synthesis = output.get('synthesis', '') if isinstance(output, dict) else str(output)
                
                if synthesis and synthesis != 'No Ultra Synthesis™ available':
                    print(f"   ✅ Synthesis generated successfully")
                    print(f"   Model used: {output.get('model_used', 'unknown') if isinstance(output, dict) else 'unknown'}")
                    print(f"   Length: {len(synthesis)} characters")
                    
                    # Show preview
                    preview = synthesis[:200] + "..." if len(synthesis) > 200 else synthesis
                    print(f"\n   Preview: {preview}")
                else:
                    print(f"   ❌ No synthesis generated")
    
    # Check saved files
    if data.get('saved_files'):
        print(f"\n💾 Saved files:")
        for file_type, path in data['saved_files'].items():
            print(f"   {file_type}: {path}")

if __name__ == "__main__":
    # Run the test
    test_orchestration_flow()