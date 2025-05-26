#!/usr/bin/env python3
"""
MVP Security Audit Testing Script
Day 3 of MVPProductionAudit
Tests JWT implementation, API keys, CORS, rate limiting, and security headers
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List

import requests

# Configuration
BASE_URL = "http://localhost:8085"
TEST_USER = {
    "email": "test@ultrai.com",
    "password": "Test123!@#",
    "name": "Test User"
}


class SecurityTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {}
        self.jwt_token = None
        self.api_key = None
        
    def run_all_tests(self):
        """Run all security tests"""
        print("=== Ultra MVP Security Audit ===")
        print(f"Started at: {datetime.now()}")
        print(f"Base URL: {BASE_URL}\n")
        
        # Test categories
        self.test_auth_security()
        self.test_jwt_security()
        self.test_api_key_security()
        self.test_cors_security()
        self.test_rate_limiting()
        self.test_security_headers()
        self.test_injection_protection()
        self.test_error_handling()
        
        # Generate report
        self.generate_report()
        
    def test_auth_security(self):
        """Test authentication security features"""
        print("\n--- Testing Authentication Security ---")
        results = []
        
        # Test 1: Register new user
        print("1. Testing user registration...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/register",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                results.append(("User Registration", "PASS", "User created successfully"))
            else:
                results.append(("User Registration", "FAIL", f"Status: {response.status_code}, Response: {response.text}"))
        except Exception as e:
            results.append(("User Registration", "ERROR", str(e)))
            
        # Test 2: Login
        print("2. Testing user login...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                results.append(("User Login", "PASS", "JWT token received"))
            else:
                results.append(("User Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}"))
        except Exception as e:
            results.append(("User Login", "ERROR", str(e)))
            
        # Test 3: Access protected endpoint without token
        print("3. Testing protected endpoint without token...")
        try:
            response = self.session.get(f"{BASE_URL}/api/analyze")
            if response.status_code == 401:
                results.append(("Protected Endpoint Auth", "PASS", "Correctly rejected unauthorized request"))
            else:
                results.append(("Protected Endpoint Auth", "FAIL", f"Expected 401, got {response.status_code}"))
        except Exception as e:
            results.append(("Protected Endpoint Auth", "ERROR", str(e)))
            
        # Test 4: Access with token
        print("4. Testing protected endpoint with token...")
        if self.jwt_token:
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/analyze",
                    headers={"Authorization": f"Bearer {self.jwt_token}",
                             "Content-Type": "application/json"},
                    json={"prompt": "Test auth"}
                )
                if response.status_code != 401:
                    results.append(("Token Authentication", "PASS", "Token accepted"))
                else:
                    results.append(("Token Authentication", "FAIL", "Token rejected"))
            except Exception as e:
                results.append(("Token Authentication", "ERROR", str(e)))
                
        self.results["Authentication Security"] = results
        
    def test_jwt_security(self):
        """Test JWT implementation security"""
        print("\n--- Testing JWT Security ---")
        results = []
        
        # Test 1: Invalid token format
        print("1. Testing invalid token format...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/analyze",
                headers={"Authorization": "Bearer invalid.token.format",
                        "Content-Type": "application/json"},
                json={"prompt": "Test invalid"}
            )
            if response.status_code == 401:
                results.append(("Invalid JWT Format", "PASS", "Correctly rejected invalid token"))
            else:
                results.append(("Invalid JWT Format", "FAIL", f"Expected 401, got {response.status_code}"))
        except Exception as e:
            results.append(("Invalid JWT Format", "ERROR", str(e)))
            
        # Test 2: Expired token
        print("2. Testing expired token handling...")
        # Note: This would require waiting for token expiration or mocking
        results.append(("Expired Token", "SKIP", "Requires time delay for expiration"))
        
        # Test 3: Token with wrong algorithm
        print("3. Testing token algorithm validation...")
        # Create token with different algorithm (requires JWT library)
        results.append(("Algorithm Validation", "SKIP", "Requires JWT library for testing"))
        
        self.results["JWT Security"] = results
        
    def test_api_key_security(self):
        """Test API key security"""
        print("\n--- Testing API Key Security ---")
        results = []
        
        # Test 1: Generate API key
        print("1. Testing API key generation...")
        if self.jwt_token:
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/users/me/api-keys",
                    json={"name": "Test API Key"},
                    headers={
                        "Authorization": f"Bearer {self.jwt_token}",
                        "Content-Type": "application/json"
                    }
                )
                if response.status_code == 201:
                    data = response.json()
                    self.api_key = data.get("key")
                    results.append(("API Key Generation", "PASS", "API key created"))
                else:
                    results.append(("API Key Generation", "FAIL", f"Status: {response.status_code}"))
            except Exception as e:
                results.append(("API Key Generation", "ERROR", str(e)))
        
        # Test 2: Use API key
        print("2. Testing API key authentication...")
        if self.api_key:
            try:
                response = self.session.get(
                    f"{BASE_URL}/api/analyze",
                    headers={"X-API-Key": self.api_key}
                )
                if response.status_code != 401:
                    results.append(("API Key Auth", "PASS", "API key accepted"))
                else:
                    results.append(("API Key Auth", "FAIL", "API key rejected"))
            except Exception as e:
                results.append(("API Key Auth", "ERROR", str(e)))
                
        # Test 3: Invalid API key
        print("3. Testing invalid API key...")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/analyze",
                headers={"X-API-Key": "invalid_api_key",
                        "Content-Type": "application/json"},
                json={"prompt": "Test invalid api"}
            )
            if response.status_code == 401:
                results.append(("Invalid API Key", "PASS", "Correctly rejected invalid key"))
            else:
                results.append(("Invalid API Key", "FAIL", f"Expected 401, got {response.status_code}"))
        except Exception as e:
            results.append(("Invalid API Key", "ERROR", str(e)))
            
        self.results["API Key Security"] = results
        
    def test_cors_security(self):
        """Test CORS configuration"""
        print("\n--- Testing CORS Security ---")
        results = []
        
        # Test 1: Allowed origin
        print("1. Testing allowed origin...")
        try:
            response = self.session.options(
                f"{BASE_URL}/api/health",
                headers={
                    "Origin": "http://localhost:3009",
                    "Access-Control-Request-Method": "GET"
                }
            )
            headers = response.headers
            if "Access-Control-Allow-Origin" in headers:
                allowed_origin = headers["Access-Control-Allow-Origin"]
                if allowed_origin == "http://localhost:3009":
                    results.append(("Allowed Origin", "PASS", f"Origin allowed: {allowed_origin}"))
                else:
                    results.append(("Allowed Origin", "WARN", f"Different origin: {allowed_origin}"))
            else:
                results.append(("Allowed Origin", "FAIL", "No CORS headers found"))
        except Exception as e:
            results.append(("Allowed Origin", "ERROR", str(e)))
            
        # Test 2: Disallowed origin
        print("2. Testing disallowed origin...")
        try:
            response = self.session.options(
                f"{BASE_URL}/api/health",
                headers={
                    "Origin": "http://evil.com",
                    "Access-Control-Request-Method": "GET"
                }
            )
            headers = response.headers
            if "Access-Control-Allow-Origin" in headers:
                allowed_origin = headers["Access-Control-Allow-Origin"]
                if allowed_origin != "http://evil.com":
                    results.append(("Disallowed Origin", "PASS", "Evil origin correctly blocked"))
                else:
                    results.append(("Disallowed Origin", "FAIL", "Evil origin was allowed"))
            else:
                results.append(("Disallowed Origin", "PASS", "No CORS headers for evil origin"))
        except Exception as e:
            results.append(("Disallowed Origin", "ERROR", str(e)))
            
        self.results["CORS Security"] = results
        
    def test_rate_limiting(self):
        """Test rate limiting"""
        print("\n--- Testing Rate Limiting ---")
        results = []
        
        # Test 1: Burst requests
        print("1. Testing rate limiting with burst requests...")
        try:
            # Send 10 rapid requests
            for i in range(10):
                response = self.session.get(f"{BASE_URL}/api/health")
                print(f"Request {i+1}: Status {response.status_code}")
                if response.status_code == 429:
                    results.append(("Rate Limiting", "PASS", f"Rate limited after {i+1} requests"))
                    break
                time.sleep(0.1)  # Small delay between requests
            else:
                results.append(("Rate Limiting", "WARN", "No rate limiting detected in 10 requests"))
        except Exception as e:
            results.append(("Rate Limiting", "ERROR", str(e)))
            
        self.results["Rate Limiting"] = results
        
    def test_security_headers(self):
        """Test security headers"""
        print("\n--- Testing Security Headers ---")
        results = []
        
        try:
            response = self.session.get(f"{BASE_URL}/api/health")
            headers = response.headers
            
            # Check required security headers
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": ["max-age=", "includeSubDomains"]
            }
            
            for header, expected in security_headers.items():
                if header in headers:
                    value = headers[header]
                    if isinstance(expected, list):
                        if any(exp in value for exp in expected):
                            results.append((header, "PASS", f"Value: {value}"))
                        else:
                            results.append((header, "FAIL", f"Expected one of {expected}, got {value}"))
                    else:
                        if value == expected:
                            results.append((header, "PASS", f"Value: {value}"))
                        else:
                            results.append((header, "FAIL", f"Expected {expected}, got {value}"))
                else:
                    results.append((header, "FAIL", "Header not present"))
                    
        except Exception as e:
            results.append(("Security Headers", "ERROR", str(e)))
            
        self.results["Security Headers"] = results
        
    def test_injection_protection(self):
        """Test SQL/NoSQL injection protection"""
        print("\n--- Testing Injection Protection ---")
        results = []
        
        # Test 1: SQL injection attempt
        print("1. Testing SQL injection protection...")
        injection_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1 UNION SELECT * FROM users"
        ]
        
        for payload in injection_payloads:
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/analyze",
                    json={"prompt": payload, "selected_models": ["gpt4o"]},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code in [400, 422]:
                    results.append((f"SQL Injection ({payload[:20]}...)", "PASS", "Payload rejected"))
                else:
                    results.append((f"SQL Injection ({payload[:20]}...)", "WARN", f"Status: {response.status_code}"))
            except Exception as e:
                results.append((f"SQL Injection ({payload[:20]}...)", "ERROR", str(e)))
                
        self.results["Injection Protection"] = results
        
    def test_error_handling(self):
        """Test error handling and information disclosure"""
        print("\n--- Testing Error Handling ---")
        results = []
        
        # Test 1: Stack trace exposure
        print("1. Testing stack trace exposure...")
        try:
            response = self.session.get(f"{BASE_URL}/api/nonexistent")
            if response.status_code == 404:
                content = response.text
                if "Traceback" not in content and "stack" not in content.lower():
                    results.append(("Stack Trace Exposure", "PASS", "No stack trace in error response"))
                else:
                    results.append(("Stack Trace Exposure", "FAIL", "Stack trace exposed in error"))
            else:
                results.append(("Stack Trace Exposure", "WARN", f"Unexpected status: {response.status_code}"))
        except Exception as e:
            results.append(("Stack Trace Exposure", "ERROR", str(e)))
            
        # Test 2: Internal error exposure
        print("2. Testing internal error handling...")
        try:
            # Send malformed request to trigger error
            response = self.session.post(
                f"{BASE_URL}/api/analyze",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in [400, 422]:
                content = response.text
                if "internal" not in content.lower() and "server error" not in content.lower():
                    results.append(("Internal Error Exposure", "PASS", "No internal details exposed"))
                else:
                    results.append(("Internal Error Exposure", "WARN", "Possible internal details exposed"))
            else:
                results.append(("Internal Error Exposure", "WARN", f"Unexpected status: {response.status_code}"))
        except Exception as e:
            results.append(("Internal Error Exposure", "ERROR", str(e)))
            
        self.results["Error Handling"] = results
        
    def generate_report(self):
        """Generate security audit report"""
        print("\n\n=== Security Audit Report ===")
        print(f"Completed at: {datetime.now()}\n")
        
        # Summary
        total_tests = 0
        passed = 0
        failed = 0
        errors = 0
        warnings = 0
        skipped = 0
        
        for category, tests in self.results.items():
            print(f"\n--- {category} ---")
            for test_name, status, details in tests:
                print(f"  {test_name}: {status} - {details}")
                total_tests += 1
                if status == "PASS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                elif status == "ERROR":
                    errors += 1
                elif status == "WARN":
                    warnings += 1
                elif status == "SKIP":
                    skipped += 1
                    
        print(f"\n\n=== Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Warnings: {warnings}")
        print(f"Skipped: {skipped}")
        
        # Save report to file
        report_file = f"security_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "warnings": warnings,
                    "skipped": skipped
                },
                "results": self.results
            }, f, indent=2)
        print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    tester = SecurityTester()
    tester.run_all_tests()