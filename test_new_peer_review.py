#!/usr/bin/env python3
"""Test the updated peer review prompt behavior."""

import requests
import json
import time
from datetime import datetime

def test_peer_review():
    """Test with a query that might have factual disagreements."""
    
    url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"
    
    # Use a factual query where models might have different information
    payload = {
        "query": "What is the current population of Tokyo, Japan?",
        "selected_models": ["claude-3-5-haiku-20241022", "gemini-1.5-flash"],
        "include_pipeline_details": True
    }
    
    print(f"Testing Updated Peer Review Prompt at {datetime.now()}")
    print(f"URL: {url}")
    print(f"Query: {payload['query']}")
    print(f"Models: {payload['selected_models']}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save response
            filename = f'peer_review_test_{int(time.time())}.json'
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                print(f"Response saved to {filename}")
            
            print(f"\n✅ Success: {data.get('success')}")
            print(f"⏱️  Processing Time: {data.get('processing_time', 0):.2f} seconds")
            
            if 'results' in data:
                results = data['results']
                
                # Compare initial vs peer-reviewed responses
                print("\n📊 COMPARING RESPONSES:")
                
                initial_responses = {}
                revised_responses = {}
                
                # Get initial responses
                if 'initial_response' in results and 'output' in results['initial_response']:
                    initial_responses = results['initial_response']['output'].get('responses', {})
                
                # Get peer-reviewed responses
                if 'peer_review_and_revision' in results and 'output' in results['peer_review_and_revision']:
                    revised_responses = results['peer_review_and_revision']['output'].get('revised_responses', {})
                
                # Compare each model
                for model in initial_responses:
                    print(f"\n🤖 {model}:")
                    
                    initial = str(initial_responses.get(model, ""))
                    revised = revised_responses.get(model, "")
                    
                    print(f"\n  Initial Response:")
                    print(f"  {initial[:200]}...")
                    
                    print(f"\n  Revised Response (after peer review):")
                    print(f"  {revised[:200]}...")
                    
                    # Check if response changed
                    if initial != revised:
                        print(f"\n  ✅ Response was REVISED after peer review")
                    else:
                        print(f"\n  ⚪ Response UNCHANGED after peer review")
                
                # Show final synthesis
                if 'ultra_synthesis' in results and 'output' in results['ultra_synthesis']:
                    synthesis = results['ultra_synthesis']['output'].get('synthesis', '')
                    print(f"\n🎯 FINAL ULTRA SYNTHESIS:")
                    print(f"{synthesis[:400]}...")
                    
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_peer_review()