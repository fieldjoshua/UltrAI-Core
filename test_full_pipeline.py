#!/usr/bin/env python3
"""Test the full 3-stage Ultra Synthesis pipeline."""

import requests
import json
import time
from datetime import datetime

def test_full_pipeline():
    """Test with models that are more likely to all respond."""
    
    url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"
    
    # Use a mix of models with lower rate limit pressure
    payload = {
        "query": "What are the advantages and disadvantages of remote work?",
        "selected_models": ["gpt-3.5-turbo", "claude-3-5-haiku-20241022", "gemini-1.5-flash"],
        "include_pipeline_details": True
    }
    
    print(f"Testing FULL Ultra Synthesis Pipeline at {datetime.now()}")
    print(f"URL: {url}")
    print(f"Query: {payload['query']}")
    print(f"Models: {payload['selected_models']}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save full response
            filename = f'full_pipeline_{int(time.time())}.json'
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                print(f"Full response saved to {filename}")
            
            print(f"\n✅ Success: {data.get('success')}")
            print(f"⏱️  Processing Time: {data.get('processing_time', 0):.2f} seconds")
            
            if 'pipeline_info' in data:
                info = data['pipeline_info']
                print(f"\n📊 Pipeline Info:")
                print(f"   Stages completed: {info.get('stages_completed')}")
                print(f"   Pipeline type: {info.get('pipeline_type')}")
                print(f"   Models used: {info.get('models_used')}")
            
            if 'results' in data:
                results = data['results']
                
                # Check Stage 1: Initial Response
                print(f"\n🚀 STAGE 1: Initial Response")
                if 'initial_response' in results:
                    initial = results['initial_response']
                    if 'output' in initial and 'responses' in initial['output']:
                        responses = initial['output']['responses']
                        print(f"   Models attempted: {initial['output'].get('models_attempted', [])}")
                        print(f"   Successful models: {initial['output'].get('successful_models', [])}")
                        print(f"   Responses received:")
                        for model in responses:
                            if isinstance(responses[model], dict) and 'error' in responses[model]:
                                print(f"     - {model}: ❌ {responses[model]['error']}")
                            else:
                                text = str(responses[model])[:100]
                                print(f"     - {model}: ✅ {text}...")
                
                # Check Stage 2: Peer Review
                print(f"\n🔄 STAGE 2: Peer Review & Revision")
                if 'peer_review_and_revision' in results:
                    peer = results['peer_review_and_revision']
                    if 'output' in peer and 'revised_responses' in peer['output']:
                        revised = peer['output']['revised_responses']
                        print(f"   ✅ Peer review completed!")
                        print(f"   Models that revised their responses:")
                        for model in revised:
                            print(f"     - {model}: Revised response available")
                    else:
                        print(f"   ❌ No revised responses found")
                else:
                    print(f"   ⏭️  SKIPPED (requires 2+ successful initial responses)")
                
                # Check Stage 3: Ultra Synthesis
                print(f"\n🎯 STAGE 3: Ultra Synthesis™")
                if 'ultra_synthesis' in results:
                    ultra = results['ultra_synthesis']
                    if 'output' in ultra:
                        output = ultra['output']
                        print(f"   ✅ Ultra Synthesis completed!")
                        print(f"   Synthesis model: {output.get('model_used', 'Unknown')}")
                        print(f"   Source models: {output.get('source_models', [])}")
                        
                        synthesis_text = output.get('synthesis', '')
                        if synthesis_text:
                            print(f"   Length: {len(synthesis_text)} characters")
                            print(f"\n   Preview:")
                            print("   " + "-" * 60)
                            preview = synthesis_text[:300].replace('\n', '\n   ')
                            print(f"   {preview}...")
                        
                        # Check quality indicators
                        if 'quality_indicators' in output:
                            qi = output['quality_indicators']
                            if 'confidence' in qi:
                                print(f"\n   Quality Metrics:")
                                print(f"     - Overall confidence: {qi['confidence'].get('confidence_level', 'N/A')}")
                            if 'consensus' in qi:
                                print(f"     - Consensus level: {qi['consensus'].get('consensus_level', 'N/A')}")
                else:
                    print(f"   ❌ Ultra Synthesis not found")
                    
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n⏱️  Request timed out after 120 seconds")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_full_pipeline()