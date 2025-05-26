#!/usr/bin/env python3
"""
Critical Production Validation Test Suite
Tests live deployment at https://ultrai-core.onrender.com

EMERGENCY TESTING - MVP Production Validation
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Production Configuration
BASE_URL = "https://ultrai-core.onrender.com"
TEST_USER_EMAIL = f"test_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"

class ProductionValidator:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "performance": {}
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log test results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def assert_response(self, response: requests.Response, expected_status: int = 200, test_name: str = ""):
        """Validate response status and log results"""
        try:
            if response.status_code == expected_status:
                self.results["tests_passed"] += 1
                self.log(f"✅ PASS: {test_name} - Status {response.status_code}", "PASS")
                return True
            else:
                self.results["tests_failed"] += 1
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                self.results["errors"].append(f"{test_name}: {error_msg}")
                self.log(f"❌ FAIL: {test_name} - {error_msg}", "FAIL")
                return False
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"{test_name}: {str(e)}")
            self.log(f"❌ ERROR: {test_name} - {str(e)}", "ERROR")
            return False

    def test_health_endpoint(self):
        """Phase 1: Health endpoint validation"""
        self.log("Testing health endpoint...")
        start_time = time.time()
        
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            response_time = time.time() - start_time
            self.results["performance"]["health_endpoint"] = response_time
            
            if self.assert_response(response, 200, "Health Endpoint"):
                data = response.json()
                self.log(f"Health Response: {json.dumps(data, indent=2)}")
                
                # Validate health response structure
                if "status" in data and data["status"] == "ok":
                    self.results["tests_passed"] += 1
                    self.log("✅ PASS: Health status is OK", "PASS")
                else:
                    self.results["tests_failed"] += 1
                    self.log("❌ FAIL: Health status not OK", "FAIL")
                    
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Health endpoint: {str(e)}")
            self.log(f"❌ CRITICAL: Health endpoint failed - {str(e)}", "CRITICAL")

    def test_api_endpoints_discovery(self):
        """Phase 1: Discover available API endpoints"""
        self.log("Discovering API endpoints...")
        
        endpoints_to_test = [
            "/auth/register",
            "/auth/login", 
            "/documents",
            "/protected",
            "/auth/verify"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                # Test endpoint availability (expect 401/405 for protected endpoints)
                response = self.session.get(f"{BASE_URL}{endpoint}", timeout=5)
                
                if response.status_code in [200, 401, 403, 405, 422]:
                    self.results["tests_passed"] += 1
                    self.log(f"✅ PASS: Endpoint {endpoint} is available (status: {response.status_code})", "PASS")
                else:
                    self.results["tests_failed"] += 1
                    self.log(f"❌ FAIL: Endpoint {endpoint} unexpected status: {response.status_code}", "FAIL")
                    
            except Exception as e:
                self.results["tests_failed"] += 1
                self.results["errors"].append(f"Endpoint {endpoint}: {str(e)}")
                self.log(f"❌ ERROR: Endpoint {endpoint} - {str(e)}", "ERROR")

    def test_user_registration(self):
        """Phase 2: User registration workflow"""
        self.log("Testing user registration...")
        start_time = time.time()
        
        try:
            registration_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "username": f"testuser_{int(time.time())}"
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/register",
                json=registration_data,
                timeout=10
            )
            
            response_time = time.time() - start_time
            self.results["performance"]["user_registration"] = response_time
            
            if self.assert_response(response, 200, "User Registration"):
                data = response.json()
                self.log(f"Registration successful: {data.get('message', 'No message')}")
                return True
            else:
                self.log(f"Registration failed: {response.text}")
                return False
                
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"User registration: {str(e)}")
            self.log(f"❌ ERROR: User registration failed - {str(e)}", "ERROR")
            return False

    def test_user_login(self):
        """Phase 2: User login workflow"""
        self.log("Testing user login...")
        start_time = time.time()
        
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data,
                timeout=10
            )
            
            response_time = time.time() - start_time
            self.results["performance"]["user_login"] = response_time
            
            if self.assert_response(response, 200, "User Login"):
                data = response.json()
                
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.results["tests_passed"] += 1
                    self.log("✅ PASS: JWT token received and set", "PASS")
                    return True
                else:
                    self.results["tests_failed"] += 1
                    self.log("❌ FAIL: No access token in login response", "FAIL")
                    return False
            else:
                self.log(f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"User login: {str(e)}")
            self.log(f"❌ ERROR: User login failed - {str(e)}", "ERROR")
            return False

    def test_authenticated_endpoints(self):
        """Phase 2: Test authenticated endpoint access"""
        if not self.auth_token:
            self.log("❌ SKIP: No auth token available for authenticated tests", "SKIP")
            return
            
        self.log("Testing authenticated endpoints...")
        
        try:
            # Test protected endpoint
            response = self.session.get(f"{BASE_URL}/protected", timeout=10)
            self.assert_response(response, 200, "Protected Endpoint")
            
            # Test documents endpoint
            response = self.session.get(f"{BASE_URL}/documents", timeout=10)
            self.assert_response(response, 200, "Documents Endpoint")
            
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Authenticated endpoints: {str(e)}")
            self.log(f"❌ ERROR: Authenticated endpoints failed - {str(e)}", "ERROR")

    def test_error_handling(self):
        """Phase 3: Error handling scenarios"""
        self.log("Testing error handling...")
        
        # Test invalid login
        try:
            invalid_login = {
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json=invalid_login,
                timeout=10
            )
            
            if response.status_code in [401, 422]:
                self.results["tests_passed"] += 1
                self.log("✅ PASS: Invalid login properly rejected", "PASS")
            else:
                self.results["tests_failed"] += 1
                self.log(f"❌ FAIL: Invalid login unexpected status: {response.status_code}", "FAIL")
                
        except Exception as e:
            self.results["tests_failed"] += 1
            self.results["errors"].append(f"Error handling: {str(e)}")
            self.log(f"❌ ERROR: Error handling test failed - {str(e)}", "ERROR")

    def test_performance_baseline(self):
        """Phase 4: Establish performance baselines"""
        self.log("Establishing performance baselines...")
        
        # Test response time for health endpoint (should be < 1 second)
        health_time = self.results["performance"].get("health_endpoint", 0)
        if health_time < 1.0:
            self.results["tests_passed"] += 1
            self.log(f"✅ PASS: Health endpoint response time: {health_time:.2f}s", "PASS")
        else:
            self.results["tests_failed"] += 1
            self.log(f"❌ FAIL: Health endpoint too slow: {health_time:.2f}s", "FAIL")

    def run_all_tests(self):
        """Execute complete test suite"""
        self.log("🚀 STARTING CRITICAL PRODUCTION VALIDATION", "START")
        self.log(f"Testing production deployment at: {BASE_URL}")
        
        # Phase 1: API Validation
        self.log("\n📋 PHASE 1: Production API Validation", "PHASE")
        self.test_health_endpoint()
        self.test_api_endpoints_discovery()
        
        # Phase 2: Critical User Flows  
        self.log("\n👤 PHASE 2: Critical User Flows", "PHASE")
        if self.test_user_registration():
            time.sleep(1)  # Brief delay between registration and login
            if self.test_user_login():
                self.test_authenticated_endpoints()
        
        # Phase 3: Error Handling
        self.log("\n⚠️  PHASE 3: Error Handling", "PHASE") 
        self.test_error_handling()
        
        # Phase 4: Performance
        self.log("\n📊 PHASE 4: Performance Baseline", "PHASE")
        self.test_performance_baseline()
        
        # Final Results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        success_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "="*60, "RESULTS")
        self.log("🏁 PRODUCTION VALIDATION COMPLETE", "RESULTS")
        self.log("="*60, "RESULTS")
        self.log(f"Tests Passed: {self.results['tests_passed']}", "RESULTS")
        self.log(f"Tests Failed: {self.results['tests_failed']}", "RESULTS")
        self.log(f"Success Rate: {success_rate:.1f}%", "RESULTS")
        
        if self.results["performance"]:
            self.log("\n📊 Performance Metrics:", "RESULTS")
            for endpoint, time_taken in self.results["performance"].items():
                self.log(f"  {endpoint}: {time_taken:.2f}s", "RESULTS")
        
        if self.results["errors"]:
            self.log("\n❌ Errors Encountered:", "RESULTS")
            for error in self.results["errors"]:
                self.log(f"  - {error}", "RESULTS")
        
        # Overall Status
        if success_rate >= 80:
            self.log("\n🎉 PRODUCTION STATUS: READY FOR DEPLOYMENT", "SUCCESS")
        elif success_rate >= 60:
            self.log("\n⚠️  PRODUCTION STATUS: NEEDS ATTENTION", "WARNING")
        else:
            self.log("\n🚨 PRODUCTION STATUS: CRITICAL ISSUES", "CRITICAL")
        
        self.log("="*60, "RESULTS")
        
        # Save results to file
        try:
            with open("production_validation_results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            self.log("✅ Results saved to production_validation_results.json", "INFO")
        except Exception as e:
            self.log(f"❌ Failed to save results: {str(e)}", "ERROR")

def main():
    """Main execution function"""
    validator = ProductionValidator()
    validator.run_all_tests()
    
    # Exit with error code if critical failures
    if validator.results["tests_failed"] > validator.results["tests_passed"]:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()