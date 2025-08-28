#!/usr/bin/env python3
"""Debug Ultra Synthesis flow to see full response structure."""

import requests
import json
from datetime import datetime

def debug_ultra_synthesis():
    """Debug the full response structure."""
    
    url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"
    
    payload = {
        "query": "Explain quantum computing in simple terms",
        "selected_models": ["gpt-4o", "claude-3-5-sonnet-20241022"],
        "include_pipeline_details": True
    }
    
    print(f"Testing Ultra Synthesis at {datetime.now()}")
    print(f"URL: {url}")
    print(f"Query: {payload['query']}")
    print(f"Models: {payload['selected_models']}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save full response for analysis
            with open('ultra_synthesis_response.json', 'w') as f:
                json.dump(data, f, indent=2)
                print("Full response saved to ultra_synthesis_response.json")
            
            print(f"\nSuccess: {data.get('success')}")
            print(f"Processing Time: {data.get('processing_time', 0):.2f} seconds")
            
            if 'pipeline_info' in data:
                info = data['pipeline_info']
                print(f"\nPipeline Info:")
                print(f"  Stages completed: {info.get('stages_completed')}")
                print(f"  Total stages: {info.get('total_stages')}")
                print(f"  Pipeline type: {info.get('pipeline_type')}")
                print(f"  Models used: {info.get('models_used')}")
            
            if 'results' in data:
                results = data['results']
                print(f"\nResults structure:")
                print(f"  Keys: {list(results.keys())}")
                
                # Check each stage
                for stage in ['initial_response', 'peer_review_and_revision', 'ultra_synthesis']:
                    print(f"\n{stage}:")
                    if stage in results:
                        stage_data = results[stage]
                        if isinstance(stage_data, dict):
                            print(f"  Type: dict")
                            print(f"  Keys: {list(stage_data.keys())}")
                            if 'output' in stage_data:
                                output = stage_data['output']
                                if isinstance(output, dict):
                                    print(f"  Output keys: {list(output.keys())}")
                                    if 'responses' in output:
                                        print(f"  Responses: {list(output['responses'].keys())}")
                                    if 'revised_responses' in output:
                                        print(f"  Revised responses: {list(output['revised_responses'].keys())}")
                                else:
                                    print(f"  Output type: {type(output).__name__}")
                            if 'error' in stage_data:
                                print(f"  Error: {stage_data['error']}")
                        else:
                            print(f"  Type: {type(stage_data).__name__}")
                    else:
                        print(f"  NOT FOUND in results")
                        
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_ultra_synthesis()