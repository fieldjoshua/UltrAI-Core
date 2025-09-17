#!/usr/bin/env python3
"""
Master test runner for UltraAI
Run various test suites with options
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime


class TestRunner:
    """Manages test execution"""
    
    def __init__(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = []
    
    def run_command(self, cmd, description):
        """Run a command and track results"""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
        
        start = datetime.now()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        duration = (datetime.now() - start).total_seconds()
        
        success = result.returncode == 0
        self.results.append({
            'description': description,
            'success': success,
            'duration': duration
        })
        
        if success:
            print(f"✅ PASSED ({duration:.2f}s)")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ FAILED ({duration:.2f}s)")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
        
        return success
    
    def run_quick_health_check(self):
        """Quick health check of orchestration"""
        cmd = f"cd {self.test_dir} && python3 -m pytest production/test_orchestration_comprehensive.py::TestOrchestrationHealth -v"
        return self.run_command(cmd, "Quick Health Check")
    
    def run_orchestration_test(self):
        """Test orchestration functionality"""
        cmd = f"cd {self.test_dir} && python3 -m pytest production/test_orchestration_comprehensive.py::TestOrchestrationFunctionality::test_simple_orchestration -v -s"
        return self.run_command(cmd, "Orchestration Functionality Test")
    
    def run_all_production_tests(self):
        """Run all production tests"""
        cmd = f"cd {self.test_dir} && python3 -m pytest integration/ --cov=app --cov-report=term-missing"
        return self.run_command(cmd, "All Production Tests")
    
    def run_specific_test(self, test_path):
        """Run a specific test file or test"""
        cmd = f"cd {self.test_dir} && python3 -m pytest {test_path} -v --cov=app --cov-report=term-missing"
        return self.run_command(cmd, f"Specific Test: {test_path}")

    def run_frontend_tests(self):
        """Run frontend Jest tests"""
        cmd = "cd frontend && npm test"
        return self.run_command(cmd, "Frontend Jest Tests")

    def run_frontend_lint(self):
        """Run frontend ESLint checks"""
        cmd = "cd frontend && npm run lint"
        return self.run_command(cmd, "Frontend ESLint")

    def run_frontend_format_check(self):
        """Run frontend Prettier format check"""
        cmd = "cd frontend && npm run format:check"
        return self.run_command(cmd, "Frontend Format Check")

    def print_summary(self):
        """Print test run summary"""
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        
        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} | {result['duration']:6.2f}s | {result['description']}")
        
        print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n❌ {failed} test(s) failed!")
        
        return failed == 0


def main():
    parser = argparse.ArgumentParser(description='Run UltraAI tests')
    parser.add_argument('--quick', action='store_true', help='Run quick health check only')
    parser.add_argument('--orchestration', action='store_true', help='Run orchestration tests')
    parser.add_argument('--all', action='store_true', help='Run all production tests')
    parser.add_argument('--test', type=str, help='Run specific test file or path')
    parser.add_argument('--install', action='store_true', help='Install test requirements')
    parser.add_argument('--frontend', action='store_true', help='Run all frontend checks (Jest, Lint, Format)')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Install requirements if requested
    if args.install:
        print("📦 Installing test requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      cwd=runner.test_dir)
        print("✅ Requirements installed")
        return
    
    # Run requested tests
    if args.quick:
        runner.run_quick_health_check()
    elif args.orchestration:
        runner.run_orchestration_test()
    elif args.all:
        runner.run_all_production_tests()
    elif args.test:
        runner.run_specific_test(args.test)
    else:
        # Default: run backend integration tests and all frontend checks
        runner.run_all_production_tests()
        runner.run_frontend_tests()
        runner.run_frontend_lint()
        runner.run_frontend_format_check()
    
    # Print summary
    success = runner.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()