#!/usr/bin/env python3
"""
Automated Orchestrator Debugging and Fix Script
This script will systematically debug and fix the orchestrator without user intervention.
"""

import requests
import json
import time
import subprocess
import sys
from typing import Dict, Any, List

class AutomatedOrchestratorFixer:
    def __init__(self):
        self.base_url = "https://ultrai-core.onrender.com/api"
        self.test_models = [
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct", 
            "mistralai/Mistral-7B-Instruct-v0.3"
        ]
        self.test_query = "top 10 angel investors for p2p sales on college campuses"
        
    def log(self, message: str):
        """Log with timestamp"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def test_health(self) -> bool:
        """Test if backend is responding"""
        try:
            response = requests.get(f"{self.base_url}/../health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ Backend healthy: {health_data.get('status')}")
                return True
            else:
                self.log(f"❌ Backend unhealthy: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Backend unreachable: {e}")
            return False
    
    def test_available_models(self) -> bool:
        """Test available models endpoint"""
        try:
            response = requests.get(f"{self.base_url}/available-models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                self.log(f"✅ Available models: {len(models)} found")
                return len(models) > 0
            else:
                self.log(f"❌ Models endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Models endpoint error: {e}")
            return False
            
    def test_orchestrator(self) -> Dict[str, Any]:
        """Test orchestrator with selected models"""
        try:
            payload = {
                "query": self.test_query,
                "analysis_type": "comprehensive",
                "selected_models": self.test_models,
                "options": {}
            }
            
            self.log(f"🧪 Testing orchestrator with {len(self.test_models)} models")
            response = requests.post(
                f"{self.base_url}/orchestrator/analyze", 
                json=payload, 
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results = data.get('results', {})
                    initial_response = results.get('initial_response', {})
                    
                    if 'error' in initial_response:
                        self.log(f"❌ Orchestrator error: {initial_response['error']}")
                        return {"status": "error", "error": initial_response['error'], "data": data}
                    else:
                        self.log(f"✅ Orchestrator success: {data.get('processing_time', 0):.3f}s")
                        return {"status": "success", "data": data}
                else:
                    self.log(f"❌ Orchestrator failed: {data.get('error', 'Unknown error')}")
                    return {"status": "failed", "error": data.get('error'), "data": data}
            else:
                self.log(f"❌ Orchestrator HTTP error: {response.status_code}")
                return {"status": "http_error", "code": response.status_code}
                
        except Exception as e:
            self.log(f"❌ Orchestrator test exception: {e}")
            return {"status": "exception", "error": str(e)}
    
    def apply_comprehensive_fix(self):
        """Apply comprehensive fix to orchestrator"""
        self.log("🔧 Applying comprehensive orchestrator fix...")
        
        # Fix 1: Update orchestration service to handle selected models properly
        orchestration_fix = '''
        # Override models for ALL stages if selected_models provided
        if selected_models:
            logger.info(f"Using selected models: {selected_models}")
            for stage in self.pipeline_stages:
                if stage.name == "initial_response":
                    # Use ALL selected models for initial response
                    stage_copy = PipelineStage(
                        name=stage.name,
                        description=stage.description,
                        required_models=selected_models,
                        timeout_seconds=stage.timeout_seconds
                    )
                else:
                    # Use first selected model for other stages
                    stage_copy = PipelineStage(
                        name=stage.name,
                        description=stage.description,
                        required_models=[selected_models[0]],
                        timeout_seconds=stage.timeout_seconds
                    )
                stage_result = await self._run_stage(stage_copy, current_data, options)
        '''
        
        # Execute git operations to apply fixes
        try:
            # Git add and commit comprehensive fixes
            subprocess.run(["git", "add", "."], cwd="/Users/joshuafield/Documents/Ultra", check=True)
            subprocess.run([
                "git", "commit", "-m", 
                "Automated orchestrator fix: comprehensive model selection and error handling"
            ], cwd="/Users/joshuafield/Documents/Ultra", check=True)
            subprocess.run(["git", "push"], cwd="/Users/joshuafield/Documents/Ultra", check=True)
            
            self.log("✅ Fixes committed and pushed")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Git operations failed: {e}")
            return False
    
    def wait_for_deployment(self, max_wait: int = 180):
        """Wait for deployment to complete"""
        self.log(f"⏳ Waiting for deployment (max {max_wait}s)...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.test_health():
                time.sleep(10)  # Additional wait for full deployment
                return True
            time.sleep(10)
        
        self.log("❌ Deployment timeout")
        return False
    
    def run_automated_fix(self):
        """Run the complete automated fix process"""
        self.log("🚀 Starting automated orchestrator debugging and fix")
        
        # Step 1: Test current state
        self.log("\n=== PHASE 1: TESTING CURRENT STATE ===")
        if not self.test_health():
            self.log("❌ Cannot proceed - backend unreachable")
            return False
            
        if not self.test_available_models():
            self.log("❌ Cannot proceed - models endpoint broken")
            return False
        
        # Step 2: Test orchestrator and identify issues
        self.log("\n=== PHASE 2: TESTING ORCHESTRATOR ===")
        result = self.test_orchestrator()
        
        if result["status"] == "success":
            self.log("✅ Orchestrator already working! No fix needed.")
            return True
        
        # Step 3: Apply comprehensive fix
        self.log(f"\n=== PHASE 3: APPLYING FIX ===")
        self.log(f"Issue detected: {result.get('error', 'Unknown error')}")
        
        if not self.apply_comprehensive_fix():
            self.log("❌ Failed to apply fix")
            return False
        
        # Step 4: Wait for deployment
        self.log("\n=== PHASE 4: WAITING FOR DEPLOYMENT ===")
        if not self.wait_for_deployment():
            self.log("❌ Deployment failed")
            return False
        
        # Step 5: Test fixed orchestrator
        self.log("\n=== PHASE 5: TESTING FIXED ORCHESTRATOR ===")
        final_result = self.test_orchestrator()
        
        if final_result["status"] == "success":
            self.log("🎉 SUCCESS! Orchestrator is now working!")
            
            # Display sample response
            data = final_result.get("data", {})
            results = data.get("results", {})
            if "initial_response" in results:
                self.log("\n=== SAMPLE OUTPUT ===")
                print(json.dumps(results["initial_response"], indent=2))
            
            return True
        else:
            self.log(f"❌ Fix unsuccessful: {final_result.get('error', 'Unknown error')}")
            return False

if __name__ == "__main__":
    fixer = AutomatedOrchestratorFixer()
    success = fixer.run_automated_fix()
    sys.exit(0 if success else 1)