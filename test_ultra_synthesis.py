#!/usr/bin/env python3
"""Test Ultra Synthesis flow in production."""

import requests
import json
from datetime import datetime

def test_ultra_synthesis():
    """Test the Ultra Synthesis orchestration endpoint."""
    
    # Production API URL
    url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"
    
    # Test payload
    payload = {
        "query": "What are the key benefits of using TypeScript over JavaScript for large-scale applications?",
        "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-flash"],
        "include_pipeline_details": True
    }
    
    print(f"Testing Ultra Synthesis at {datetime.now()}")
    print(f"URL: {url}")
    print(f"Selected models: {payload['selected_models']}")
    print("-" * 80)
    
    try:
        # Make the request
        response = requests.post(url, json=payload, timeout=120)
        
        # Check status
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\nSuccess: {data.get('success')}")
            print(f"Processing Time: {data.get('processing_time', 0):.2f} seconds")
            
            # Check pipeline info
            if 'pipeline_info' in data:
                info = data['pipeline_info']
                print(f"\nPipeline Info:")
                print(f"  - Stages completed: {info.get('stages_completed')}")
                print(f"  - Pipeline type: {info.get('pipeline_type')}")
                print(f"  - Models used: {info.get('models_used')}")
            
            # Check results
            if 'results' in data:
                results = data['results']
                
                # Check for ultra synthesis
                if 'ultra_synthesis' in results:
                    print(f"\n✅ ULTRA SYNTHESIS FOUND!")
                    synthesis = results['ultra_synthesis']
                    
                    # Extract the actual synthesis text
                    synthesis_text = None
                    if isinstance(synthesis, str):
                        synthesis_text = synthesis
                    elif isinstance(synthesis, dict):
                        if 'output' in synthesis and isinstance(synthesis['output'], dict):
                            if 'synthesis' in synthesis['output']:
                                synthesis_text = synthesis['output']['synthesis']
                        elif 'synthesis' in synthesis:
                            synthesis_text = synthesis['synthesis']
                    
                    if synthesis_text:
                        print(f"Length: {len(synthesis_text)} characters")
                        print(f"\nPreview of Ultra Synthesis:")
                        print("-" * 40)
                        print(synthesis_text[:500] + "...")
                    else:
                        print("Could not extract synthesis text, structure:")
                        print(json.dumps(synthesis, indent=2)[:500])
                else:
                    print(f"\n❌ NO ULTRA SYNTHESIS IN RESULTS")
                    print(f"Available keys: {list(results.keys())}")
                
                # Check initial responses
                if 'initial_response' in results:
                    initial = results['initial_response']
                    if isinstance(initial, dict) and 'output' in initial and isinstance(initial['output'], dict) and 'responses' in initial['output']:
                        responses = initial['output']['responses']
                        print(f"\nInitial Responses:")
                        for model, response in responses.items():
                            if isinstance(response, dict) and 'generated_text' in response:
                                print(f"  - {model}: ✅ Got response ({len(response['generated_text'])} chars)")
                            elif isinstance(response, dict):
                                print(f"  - {model}: ❌ {response.get('error', 'No response')}")
                            else:
                                print(f"  - {model}: ❌ Invalid response format")
                
                # Check peer review
                if 'peer_review_and_revision' in results:
                    peer = results['peer_review_and_revision']
                    if 'output' in peer and 'revised_responses' in peer['output']:
                        print(f"\nPeer Review: ✅ Found {len(peer['output']['revised_responses'])} revised responses")
                    else:
                        print(f"\nPeer Review: ❌ Not found or empty")
                        
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("Request timed out after 120 seconds")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ultra_synthesis()