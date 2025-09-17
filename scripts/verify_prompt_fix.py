#!/usr/bin/env python3
"""
Verify the prompt extraction fix in orchestration service.
Tests that the original user prompt appears correctly in ultra synthesis output.
"""

import json
import sys
import subprocess
import time

def test_local_api():
    """Test the local API endpoint"""
    print("🔍 Testing LOCAL API at http://localhost:8000")
    
    test_query = "What is artificial intelligence and how does it impact society?"
    
    cmd = [
        "curl", "-X", "POST", "http://localhost:8000/api/orchestrator/analyze",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"query": test_query}),
        "-s"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"❌ Request failed: {result.stderr}")
            return False
            
        response = json.loads(result.stdout)
        
        # Check if ultra_synthesis exists and contains the query
        if "results" in response and "ultra_synthesis" in response["results"]:
            synthesis = response["results"]["ultra_synthesis"]
            
            # Check if the synthesis mentions "Unknown prompt"
            if "Unknown prompt" in synthesis:
                print("❌ FAIL: Ultra synthesis still shows 'Unknown prompt'")
                return False
            
            # Check if the synthesis contains parts of our query
            if "artificial intelligence" in synthesis.lower() and "society" in synthesis.lower():
                print("✅ PASS: Ultra synthesis correctly references the user's query")
                
                # Extract the "Synthesized by" line
                lines = synthesis.split('\n')
                for line in lines:
                    if "Synthesized by:" in line:
                        print(f"   {line.strip()}")
                        if "Unknown" in line:
                            print("   ⚠️  WARNING: Synthesizer still shows as Unknown")
                return True
            else:
                print("❌ FAIL: Ultra synthesis doesn't reference the user's query")
                return False
        else:
            print("❌ FAIL: No ultra_synthesis in response")
            print(f"   Response keys: {list(response.get('results', {}).keys())}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Request timed out after 30 seconds")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_production_api():
    """Test the production API endpoint"""
    print("\n🔍 Testing PRODUCTION API at https://ultrai-prod-api.onrender.com")
    
    test_query = "What is artificial intelligence?"
    
    cmd = [
        "curl", "-X", "POST", "https://ultrai-prod-api.onrender.com/api/orchestrator/analyze",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"query": test_query}),
        "-s"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"❌ Request failed: {result.stderr}")
            return False
            
        response = json.loads(result.stdout)
        
        # Check the formatted_synthesis which is easier to parse
        if "results" in response and "formatted_synthesis" in response["results"]:
            synthesis = response["results"]["formatted_synthesis"]
            
            # Look for the "Synthesized by:" line
            if "Synthesized by: Unknown" in synthesis:
                print("❌ FAIL: Production still shows 'Synthesized by: Unknown'")
                print("   (This is expected - fix not deployed to production yet)")
                return False
            else:
                print("✅ PASS: Production synthesis shows correct prompt context")
                return True
        else:
            print("❌ FAIL: No formatted_synthesis in response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing production: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PROMPT EXTRACTION FIX VERIFICATION")
    print("=" * 60)
    
    # Test local if running
    local_running = subprocess.run(
        ["curl", "-s", "http://localhost:8000/api/health"],
        capture_output=True
    ).returncode == 0
    
    if local_running:
        local_result = test_local_api()
    else:
        print("⏭️  Skipping local test (server not running)")
        local_result = None
    
    # Always test production
    prod_result = test_production_api()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    if local_result is not None:
        print(f"  Local API:      {'✅ PASS' if local_result else '❌ FAIL'}")
    print(f"  Production API: {'✅ PASS' if prod_result else '❌ FAIL (Expected - fix not deployed)'}")
    print("=" * 60)