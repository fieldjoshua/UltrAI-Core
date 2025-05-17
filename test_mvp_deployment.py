#!/usr/bin/env python3
"""
MVP Deployment Verification Script
Day 4 of MVPProductionAudit
Tests Docker configuration, environment variables, and deployment readiness
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple

import requests
import docker
import psycopg2
from redis import Redis


class DeploymentTester:
    def __init__(self):
        self.client = docker.from_env()
        self.results = {}
        self.issues = []
        
    def run_all_tests(self):
        """Run all deployment verification tests"""
        print("=== Ultra MVP Deployment Verification ===")
        print(f"Started at: {datetime.now()}")
        print()
        
        # Test categories
        self.test_docker_configuration()
        self.test_environment_variables()
        self.test_database_connectivity()
        self.test_redis_connectivity()
        self.test_docker_compose()
        self.test_health_endpoints()
        self.test_monitoring_setup()
        self.test_production_readiness()
        
        # Generate report
        self.generate_report()
        
    def test_docker_configuration(self):
        """Test Docker images and containers"""
        print("\n--- Testing Docker Configuration ---")
        results = []
        
        # Test 1: Check if Docker is running
        print("1. Checking Docker daemon...")
        try:
            version = self.client.version()
            results.append(("Docker Daemon", "PASS", f"Version: {version['Version']}"))
        except Exception as e:
            results.append(("Docker Daemon", "FAIL", str(e)))
            
        # Test 2: Check for Ultra images
        print("2. Checking for Ultra Docker images...")
        try:
            images = self.client.images.list()
            ultra_images = [img for img in images if any('ultra' in tag for tag in img.tags)]
            if ultra_images:
                image_names = ', '.join(img.tags[0] for img in ultra_images if img.tags)
                results.append(("Ultra Images", "PASS", f"Found: {image_names}"))
            else:
                results.append(("Ultra Images", "WARN", "No Ultra images found"))
        except Exception as e:
            results.append(("Ultra Images", "ERROR", str(e)))
            
        # Test 3: Check Dockerfile
        print("3. Checking Dockerfile...")
        dockerfile_path = "Dockerfile"
        if os.path.exists(dockerfile_path):
            with open(dockerfile_path, 'r') as f:
                content = f.read()
                if 'FROM python:' in content and 'WORKDIR' in content:
                    results.append(("Dockerfile", "PASS", "Valid Dockerfile found"))
                else:
                    results.append(("Dockerfile", "WARN", "Dockerfile may be incomplete"))
        else:
            results.append(("Dockerfile", "FAIL", "No Dockerfile found"))
            
        # Test 4: Check docker-compose.yml
        print("4. Checking docker-compose.yml...")
        compose_path = "docker-compose.yml"
        if os.path.exists(compose_path):
            try:
                with open(compose_path, 'r') as f:
                    content = f.read()
                    required_services = ['backend', 'postgres', 'redis']
                    found_services = []
                    for service in required_services:
                        if f'{service}:' in content:
                            found_services.append(service)
                    
                    if len(found_services) == len(required_services):
                        results.append(("Docker Compose", "PASS", f"All services defined: {', '.join(found_services)}"))
                    else:
                        missing = set(required_services) - set(found_services)
                        results.append(("Docker Compose", "WARN", f"Missing services: {', '.join(missing)}"))
            except Exception as e:
                results.append(("Docker Compose", "ERROR", str(e)))
        else:
            results.append(("Docker Compose", "FAIL", "No docker-compose.yml found"))
            
        self.results["Docker Configuration"] = results
        
    def test_environment_variables(self):
        """Test environment variable configuration"""
        print("\n--- Testing Environment Variables ---")
        results = []
        
        # Required environment variables
        required_vars = {
            'DATABASE_URL': 'PostgreSQL connection string',
            'REDIS_URL': 'Redis connection string',
            'JWT_SECRET': 'JWT signing secret',
            'JWT_REFRESH_SECRET': 'JWT refresh secret',
            'OPENAI_API_KEY': 'OpenAI API key',
            'ANTHROPIC_API_KEY': 'Anthropic API key',
            'GOOGLE_API_KEY': 'Google API key'
        }
        
        optional_vars = {
            'SENTRY_DSN': 'Error tracking',
            'LOG_LEVEL': 'Logging configuration',
            'ENABLE_AUTH': 'Authentication toggle',
            'USE_MOCK': 'Mock mode toggle'
        }
        
        # Test 1: Check .env.example
        print("1. Checking .env.example...")
        env_example_path = ".env.example"
        if os.path.exists(env_example_path):
            with open(env_example_path, 'r') as f:
                content = f.read()
                documented_vars = []
                for var in required_vars:
                    if var in content:
                        documented_vars.append(var)
                
                if len(documented_vars) == len(required_vars):
                    results.append((".env.example", "PASS", "All required vars documented"))
                else:
                    missing = set(required_vars.keys()) - set(documented_vars)
                    results.append((".env.example", "WARN", f"Missing: {', '.join(missing)}"))
        else:
            results.append((".env.example", "FAIL", "No .env.example found"))
            
        # Test 2: Check production configuration
        print("2. Checking production environment...")
        prod_env_path = ".env.production"
        if os.path.exists(prod_env_path):
            results.append((".env.production", "PASS", "Production config exists"))
        else:
            results.append((".env.production", "WARN", "No production config file"))
            
        # Test 3: Environment validation
        print("3. Validating current environment...")
        missing_required = []
        for var, desc in required_vars.items():
            if not os.getenv(var):
                missing_required.append(var)
        
        if not missing_required:
            results.append(("Required Variables", "PASS", "All required variables set"))
        else:
            results.append(("Required Variables", "FAIL", f"Missing: {', '.join(missing_required)}"))
            
        # Test 4: Optional variables
        print("4. Checking optional variables...")
        set_optional = []
        for var, desc in optional_vars.items():
            if os.getenv(var):
                set_optional.append(var)
        
        if set_optional:
            results.append(("Optional Variables", "INFO", f"Set: {', '.join(set_optional)}"))
        else:
            results.append(("Optional Variables", "INFO", "No optional variables set"))
            
        self.results["Environment Variables"] = results
        
    def test_database_connectivity(self):
        """Test database connection and migrations"""
        print("\n--- Testing Database Connectivity ---")
        results = []
        
        # Test 1: PostgreSQL connection
        print("1. Testing PostgreSQL connection...")
        db_url = os.getenv('DATABASE_URL', 'postgresql://ultrauser:ultrapass@localhost:5432/ultrallm')
        
        try:
            # Parse connection string
            parts = db_url.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                user_pass = parts[0].split(':')
                host_db = parts[1].split('/')
                
                if len(user_pass) == 2 and len(host_db) == 2:
                    user, password = user_pass
                    host_port = host_db[0].split(':')
                    database = host_db[1]
                    
                    if len(host_port) == 2:
                        host, port = host_port
                        
                        # Attempt connection
                        conn = psycopg2.connect(
                            host=host,
                            port=int(port),
                            user=user,
                            password=password,
                            database=database,
                            connect_timeout=5
                        )
                        conn.close()
                        results.append(("PostgreSQL Connection", "PASS", f"Connected to {database}"))
                    else:
                        results.append(("PostgreSQL Connection", "FAIL", "Invalid host:port format"))
                else:
                    results.append(("PostgreSQL Connection", "FAIL", "Invalid connection string format"))
            else:
                results.append(("PostgreSQL Connection", "FAIL", "Cannot parse DATABASE_URL"))
        except psycopg2.OperationalError as e:
            results.append(("PostgreSQL Connection", "FAIL", f"Connection failed: {str(e)}"))
        except Exception as e:
            results.append(("PostgreSQL Connection", "ERROR", str(e)))
            
        # Test 2: Check migrations directory
        print("2. Checking database migrations...")
        migrations_dir = "backend/database/migrations/versions"
        if os.path.exists(migrations_dir):
            migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and not f.startswith('__')]
            if migration_files:
                results.append(("Database Migrations", "PASS", f"Found {len(migration_files)} migration(s)"))
            else:
                results.append(("Database Migrations", "WARN", "No migration files found"))
        else:
            results.append(("Database Migrations", "FAIL", "No migrations directory"))
            
        # Test 3: Check alembic.ini
        print("3. Checking Alembic configuration...")
        alembic_path = "alembic.ini"
        if os.path.exists(alembic_path):
            results.append(("Alembic Config", "PASS", "alembic.ini exists"))
        else:
            results.append(("Alembic Config", "WARN", "No alembic.ini found"))
            
        self.results["Database Connectivity"] = results
        
    def test_redis_connectivity(self):
        """Test Redis connection"""
        print("\n--- Testing Redis Connectivity ---")
        results = []
        
        # Test 1: Redis connection
        print("1. Testing Redis connection...")
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            r = Redis.from_url(redis_url, socket_connect_timeout=5)
            r.ping()
            results.append(("Redis Connection", "PASS", "Successfully connected"))
            
            # Test 2: Basic operations
            print("2. Testing Redis operations...")
            test_key = "deployment_test"
            test_value = "test_value"
            
            r.set(test_key, test_value)
            retrieved = r.get(test_key)
            r.delete(test_key)
            
            if retrieved and retrieved.decode('utf-8') == test_value:
                results.append(("Redis Operations", "PASS", "Read/write successful"))
            else:
                results.append(("Redis Operations", "FAIL", "Read/write failed"))
                
        except Exception as e:
            results.append(("Redis Connection", "FAIL", f"Connection failed: {str(e)}"))
            results.append(("Redis Operations", "SKIP", "Cannot test without connection"))
            
        self.results["Redis Connectivity"] = results
        
    def test_docker_compose(self):
        """Test docker-compose setup"""
        print("\n--- Testing Docker Compose Setup ---")
        results = []
        
        # Test 1: Validate compose file
        print("1. Validating docker-compose.yml...")
        try:
            result = subprocess.run(
                ["docker-compose", "config"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                results.append(("Compose Validation", "PASS", "Configuration is valid"))
            else:
                results.append(("Compose Validation", "FAIL", f"Invalid: {result.stderr}"))
        except subprocess.TimeoutExpired:
            results.append(("Compose Validation", "ERROR", "Validation timed out"))
        except Exception as e:
            results.append(("Compose Validation", "ERROR", str(e)))
            
        # Test 2: Check service definitions
        print("2. Checking service definitions...")
        services_to_check = ['backend', 'frontend', 'postgres', 'redis']
        if os.path.exists("docker-compose.yml"):
            with open("docker-compose.yml", 'r') as f:
                content = f.read()
                defined_services = []
                for service in services_to_check:
                    if f'  {service}:' in content:
                        defined_services.append(service)
                
                if len(defined_services) >= 3:  # At least backend, postgres, redis
                    results.append(("Service Definitions", "PASS", f"Found: {', '.join(defined_services)}"))
                else:
                    results.append(("Service Definitions", "WARN", f"Limited services: {', '.join(defined_services)}"))
        
        # Test 3: Check volumes
        print("3. Checking volume definitions...")
        if os.path.exists("docker-compose.yml"):
            with open("docker-compose.yml", 'r') as f:
                content = f.read()
                if 'volumes:' in content and ('postgres-data:' in content or 'postgres_data:' in content):
                    results.append(("Volume Definitions", "PASS", "Persistent volumes defined"))
                else:
                    results.append(("Volume Definitions", "WARN", "No persistent volumes defined"))
                    
        self.results["Docker Compose"] = results
        
    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n--- Testing Health Endpoints ---")
        results = []
        
        # Test local deployment
        print("1. Testing local health endpoint...")
        try:
            response = requests.get("http://localhost:8085/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                if status in ['healthy', 'degraded']:
                    results.append(("Local Health Check", "PASS", f"Status: {status}"))
                else:
                    results.append(("Local Health Check", "WARN", f"Unexpected status: {status}"))
                    
                # Check service statuses
                services = data.get('services', {})
                for service, status in services.items():
                    if status == 'healthy':
                        results.append((f"{service.title()} Service", "PASS", "Healthy"))
                    else:
                        results.append((f"{service.title()} Service", "WARN", f"Status: {status}"))
            else:
                results.append(("Local Health Check", "FAIL", f"Status code: {response.status_code}"))
        except requests.exceptions.RequestException as e:
            results.append(("Local Health Check", "FAIL", f"Connection error: {str(e)}"))
            
        self.results["Health Endpoints"] = results
        
    def test_monitoring_setup(self):
        """Test monitoring configuration"""
        print("\n--- Testing Monitoring Setup ---")
        results = []
        
        # Test 1: Check logging configuration
        print("1. Checking logging setup...")
        log_dirs = ['logs', 'backend/logs']
        log_dir_found = False
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                log_dir_found = True
                log_files = os.listdir(log_dir)
                if log_files:
                    results.append(("Log Directory", "PASS", f"Found {len(log_files)} log file(s)"))
                else:
                    results.append(("Log Directory", "WARN", "Log directory exists but no files"))
                break
        
        if not log_dir_found:
            results.append(("Log Directory", "WARN", "No log directory found"))
            
        # Test 2: Check metrics endpoint
        print("2. Checking metrics endpoint...")
        try:
            response = requests.get("http://localhost:8085/api/metrics", timeout=5)
            if response.status_code == 200:
                results.append(("Metrics Endpoint", "PASS", "Metrics available"))
            else:
                results.append(("Metrics Endpoint", "WARN", f"Status: {response.status_code}"))
        except:
            results.append(("Metrics Endpoint", "INFO", "No metrics endpoint available"))
            
        # Test 3: Sentry configuration
        print("3. Checking error tracking setup...")
        sentry_dsn = os.getenv('SENTRY_DSN')
        if sentry_dsn:
            results.append(("Error Tracking", "PASS", "Sentry DSN configured"))
        else:
            results.append(("Error Tracking", "INFO", "No Sentry DSN configured"))
            
        self.results["Monitoring Setup"] = results
        
    def test_production_readiness(self):
        """Test production readiness criteria"""
        print("\n--- Testing Production Readiness ---")
        results = []
        
        # Test 1: Security configuration
        print("1. Checking security configuration...")
        security_checks = {
            'ENABLE_AUTH': os.getenv('ENABLE_AUTH', 'false').lower() == 'true',
            'JWT_SECRET': bool(os.getenv('JWT_SECRET')),
            'USE_MOCK': os.getenv('USE_MOCK', 'true').lower() == 'false'
        }
        
        security_score = sum(1 for check in security_checks.values() if check)
        if security_score == len(security_checks):
            results.append(("Security Config", "PASS", "Production security enabled"))
        else:
            failed_checks = [k for k, v in security_checks.items() if not v]
            results.append(("Security Config", "WARN", f"Failed: {', '.join(failed_checks)}"))
            
        # Test 2: Database readiness
        print("2. Checking database readiness...")
        db_url = os.getenv('DATABASE_URL', '')
        if 'postgresql://' in db_url and 'localhost' not in db_url:
            results.append(("Database Config", "PASS", "Production database configured"))
        else:
            results.append(("Database Config", "WARN", "Using local/development database"))
            
        # Test 3: Redis readiness
        print("3. Checking Redis readiness...")
        redis_url = os.getenv('REDIS_URL', '')
        if 'redis://' in redis_url and 'localhost' not in redis_url:
            results.append(("Redis Config", "PASS", "Production Redis configured"))
        else:
            results.append(("Redis Config", "WARN", "Using local/development Redis"))
            
        # Test 4: API keys
        print("4. Checking API key configuration...")
        api_keys = {
            'OpenAI': bool(os.getenv('OPENAI_API_KEY')),
            'Anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
            'Google': bool(os.getenv('GOOGLE_API_KEY'))
        }
        
        configured_keys = [k for k, v in api_keys.items() if v]
        if configured_keys:
            results.append(("API Keys", "INFO", f"Configured: {', '.join(configured_keys)}"))
        else:
            results.append(("API Keys", "WARN", "No API keys configured"))
            
        self.results["Production Readiness"] = results
        
    def generate_report(self):
        """Generate deployment verification report"""
        print("\n\n=== Deployment Verification Report ===")
        print(f"Completed at: {datetime.now()}\n")
        
        # Summary
        total_tests = 0
        passed = 0
        failed = 0
        warnings = 0
        info = 0
        
        # Critical issues
        critical_issues = []
        
        for category, tests in self.results.items():
            print(f"\n--- {category} ---")
            for test_name, status, details in tests:
                print(f"  {test_name}: {status} - {details}")
                total_tests += 1
                
                if status == "PASS":
                    passed += 1
                elif status == "FAIL":
                    failed += 1
                    critical_issues.append(f"{category}/{test_name}: {details}")
                elif status == "WARN":
                    warnings += 1
                elif status == "INFO":
                    info += 1
                    
        print(f"\n\n=== Summary ===")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        print(f"Info: {info}")
        
        # Critical issues
        if critical_issues:
            print(f"\n\n=== Critical Issues ===")
            for i, issue in enumerate(critical_issues, 1):
                print(f"{i}. {issue}")
                
        # Deployment readiness
        print(f"\n\n=== Deployment Readiness ===")
        readiness_score = (passed / total_tests * 100) if total_tests > 0 else 0
        
        if readiness_score >= 80 and failed == 0:
            print(f"Status: READY FOR DEPLOYMENT ({readiness_score:.1f}% passed)")
        elif readiness_score >= 60 and failed <= 2:
            print(f"Status: CONDITIONAL DEPLOYMENT ({readiness_score:.1f}% passed)")
            print("Recommendation: Fix critical issues before production deployment")
        else:
            print(f"Status: NOT READY FOR DEPLOYMENT ({readiness_score:.1f}% passed)")
            print("Recommendation: Address all critical issues before deployment")
            
        # Save report
        report_file = f"deployment_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "warnings": warnings,
                    "info": info,
                    "readiness_score": readiness_score
                },
                "critical_issues": critical_issues,
                "results": self.results
            }, f, indent=2)
        print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    # Check dependencies
    try:
        import docker
        import psycopg2
        import redis
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install docker psycopg2-binary redis")
        sys.exit(1)
        
    tester = DeploymentTester()
    tester.run_all_tests()