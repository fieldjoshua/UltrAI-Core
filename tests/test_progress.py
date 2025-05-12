#!/usr/bin/env python3
"""
Test Progress Monitor for Ultra

This script provides a progress bar and status display for Ultra test runs.
It can be used to track test progress and display summary results.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

# Test status icons
PASS_ICON = f"{GREEN}✓{END}"
FAIL_ICON = f"{RED}✗{END}"
SKIP_ICON = f"{YELLOW}⚠{END}"
RUNNING_ICON = f"{BLUE}⟳{END}"

# Test category definitions with expected test counts
TEST_CATEGORIES = {
    "API": {"total": 6, "description": "API Endpoint Tests", "critical": True},
    "AUTH": {"total": 4, "description": "Authentication Tests", "critical": True},
    "RATE": {"total": 2, "description": "Rate Limiting Tests", "critical": True},
    "ORCH": {"total": 4, "description": "Orchestrator Tests", "critical": False},
    "INTEG": {"total": 3, "description": "Integration Tests", "critical": False},
    "DOC": {"total": 2, "description": "Document Analysis Tests", "critical": False},
}


class TestProgressMonitor:
    """Monitor and display progress of Ultra test execution"""
    
    def __init__(self, test_plan: Optional[str] = None):
        """Initialize test progress monitor"""
        self.start_time = time.time()
        self.test_results: Dict[str, Dict] = {}
        self.current_category: Optional[str] = None
        self.terminal_width = self._get_terminal_width()
        
        # Load test plan if provided
        if test_plan and os.path.exists(test_plan):
            with open(test_plan, "r") as f:
                self.test_plan = json.load(f)
        else:
            self.test_plan = {"categories": TEST_CATEGORIES}
        
        # Initialize test results structure
        for category, info in self.test_plan["categories"].items():
            self.test_results[category] = {
                "total": info["total"],
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "running": False,
                "tests": {}
            }
    
    def _get_terminal_width(self) -> int:
        """Get the width of the terminal"""
        try:
            import shutil
            return shutil.get_terminal_size().columns
        except (ImportError, AttributeError):
            return 80
    
    def start_category(self, category: str) -> None:
        """Start testing a category"""
        if category in self.test_results:
            self.current_category = category
            self.test_results[category]["running"] = True
            self._display_progress()
    
    def end_category(self, category: str) -> None:
        """End testing a category"""
        if category in self.test_results:
            self.test_results[category]["running"] = False
            self.current_category = None
            self._display_progress()
    
    def add_test_result(self, category: str, test_name: str, result: str, 
                       duration: float = 0.0, message: str = "") -> None:
        """Add a test result"""
        if category not in self.test_results:
            return
        
        # Add test result
        self.test_results[category]["tests"][test_name] = {
            "result": result,
            "duration": duration,
            "message": message
        }
        
        # Update category counts
        if result == "pass":
            self.test_results[category]["passed"] += 1
        elif result == "fail":
            self.test_results[category]["failed"] += 1
        elif result == "skip":
            self.test_results[category]["skipped"] += 1
        
        # Display updated progress
        self._display_progress()
    
    def _display_progress(self) -> None:
        """Display current test progress"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display header
        print(f"{BOLD}{UNDERLINE}ULTRA TEST PROGRESS{END}")
        print(f"Started: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        elapsed = time.time() - self.start_time
        print(f"Elapsed: {int(elapsed // 60)}m {int(elapsed % 60)}s")
        print()
        
        # Calculate overall stats
        total_tests = sum(cat["total"] for cat in self.test_results.values())
        total_passed = sum(cat["passed"] for cat in self.test_results.values())
        total_failed = sum(cat["failed"] for cat in self.test_results.values())
        total_skipped = sum(cat["skipped"] for cat in self.test_results.values())
        total_executed = total_passed + total_failed + total_skipped
        
        # Display progress bar
        progress = total_executed / total_tests if total_tests > 0 else 0
        bar_width = min(50, self.terminal_width - 20)
        filled_width = int(bar_width * progress)
        bar = '█' * filled_width + '░' * (bar_width - filled_width)
        
        # Color the progress bar based on results
        if total_failed > 0:
            progress_color = RED
        elif total_skipped > 0:
            progress_color = YELLOW
        else:
            progress_color = GREEN
            
        print(f"Progress: {progress_color}{bar}{END} {int(progress * 100)}%")
        print()
        
        # Display category table
        category_format = f"{{:<8}} {{:<25}} {{:>5}} {{:>5}} {{:>5}} {{:>5}} {{:>8}}"
        print(category_format.format("CATEGORY", "DESCRIPTION", "TOTAL", "PASS", "FAIL", "SKIP", "STATUS"))
        print("-" * min(80, self.terminal_width))
        
        for category, info in self.test_plan["categories"].items():
            results = self.test_results[category]
            executed = results["passed"] + results["failed"] + results["skipped"]
            
            # Determine status
            if results["running"]:
                status = f"{RUNNING_ICON} Running"
            elif executed == 0:
                status = "Pending"
            elif results["failed"] > 0:
                status = f"{FAIL_ICON} Failed"
            elif results["passed"] == results["total"]:
                status = f"{PASS_ICON} Complete"
            else:
                status = f"{YELLOW}Partial{END}"
            
            # Critical indicator
            description = info["description"]
            if info.get("critical", False):
                description = f"{BOLD}{description}{END}"
            
            # Print category status
            print(category_format.format(
                category,
                description,
                results["total"],
                f"{GREEN}{results['passed']}{END}" if results["passed"] > 0 else "0",
                f"{RED}{results['failed']}{END}" if results["failed"] > 0 else "0",
                f"{YELLOW}{results['skipped']}{END}" if results["skipped"] > 0 else "0",
                status
            ))
        
        print("-" * min(80, self.terminal_width))
        print(category_format.format(
            "TOTAL",
            "",
            total_tests,
            f"{GREEN}{total_passed}{END}" if total_passed > 0 else "0",
            f"{RED}{total_failed}{END}" if total_failed > 0 else "0",
            f"{YELLOW}{total_skipped}{END}" if total_skipped > 0 else "0",
            f"{GREEN}PASSING{END}" if total_failed == 0 else f"{RED}FAILING{END}"
        ))
        
        # Display recently completed tests
        if self.current_category:
            print("\nRecent test results:")
            category_tests = self.test_results[self.current_category]["tests"]
            for test_name, test_info in list(category_tests.items())[-5:]:
                result_icon = PASS_ICON if test_info["result"] == "pass" else FAIL_ICON if test_info["result"] == "fail" else SKIP_ICON
                print(f"  {result_icon} {test_name} ({test_info['duration']:.2f}s)")
                if test_info["result"] == "fail" and test_info["message"]:
                    print(f"     {RED}{test_info['message']}{END}")
        
        print("\nPress Ctrl+C to abort tests")
    
    def finalize(self) -> Tuple[int, int, int]:
        """Finalize the test run and return results"""
        total_passed = sum(cat["passed"] for cat in self.test_results.values())
        total_failed = sum(cat["failed"] for cat in self.test_results.values())
        total_skipped = sum(cat["skipped"] for cat in self.test_results.values())
        
        elapsed = time.time() - self.start_time
        
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{BOLD}{UNDERLINE}ULTRA TEST RESULTS{END}")
        print(f"Completed in {int(elapsed // 60)}m {int(elapsed % 60)}s")
        print()
        
        # Display summary
        print(f"Passed: {GREEN}{total_passed}{END}")
        print(f"Failed: {RED}{total_failed}{END}")
        print(f"Skipped: {YELLOW}{total_skipped}{END}")
        print()
        
        # Display category results
        category_format = f"{{:<8}} {{:<25}} {{:>5}} {{:>5}} {{:>5}} {{:>5}} {{:>8}}"
        print(category_format.format("CATEGORY", "DESCRIPTION", "TOTAL", "PASS", "FAIL", "SKIP", "STATUS"))
        print("-" * min(80, self.terminal_width))
        
        for category, info in self.test_plan["categories"].items():
            results = self.test_results[category]
            
            # Determine status
            if results["failed"] > 0:
                status = f"{FAIL_ICON} Failed"
            elif results["passed"] == results["total"]:
                status = f"{PASS_ICON} Complete"
            else:
                status = f"{YELLOW}Partial{END}"
            
            # Critical indicator
            description = info["description"]
            if info.get("critical", False):
                description = f"{BOLD}{description}{END}"
            
            # Print category status
            print(category_format.format(
                category,
                description,
                results["total"],
                f"{GREEN}{results['passed']}{END}" if results["passed"] > 0 else "0",
                f"{RED}{results['failed']}{END}" if results["failed"] > 0 else "0",
                f"{YELLOW}{results['skipped']}{END}" if results["skipped"] > 0 else "0",
                status
            ))
        
        print("-" * min(80, self.terminal_width))
        print(category_format.format(
            "TOTAL",
            "",
            sum(cat["total"] for cat in self.test_results.values()),
            f"{GREEN}{total_passed}{END}" if total_passed > 0 else "0",
            f"{RED}{total_failed}{END}" if total_failed > 0 else "0",
            f"{YELLOW}{total_skipped}{END}" if total_skipped > 0 else "0",
            f"{GREEN}PASSING{END}" if total_failed == 0 else f"{RED}FAILING{END}"
        ))
        
        # Display failed tests
        any_failed = False
        for category, results in self.test_results.items():
            category_failed = False
            for test_name, test_info in results["tests"].items():
                if test_info["result"] == "fail":
                    if not any_failed:
                        print(f"\n{BOLD}{RED}FAILED TESTS:{END}")
                        any_failed = True
                    if not category_failed:
                        print(f"\n{BOLD}{category}:{END}")
                        category_failed = True
                    print(f"  {FAIL_ICON} {test_name}")
                    if test_info["message"]:
                        print(f"     {RED}{test_info['message']}{END}")
        
        return total_passed, total_failed, total_skipped
    
    def save_report(self, report_file: str) -> None:
        """Save test results to a JSON report file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration": time.time() - self.start_time,
            "categories": self.test_results
        }
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nTest report saved to: {report_file}")


def demo_mode():
    """Run a demo of the test progress monitor"""
    monitor = TestProgressMonitor()
    
    try:
        # Demonstrate API tests
        monitor.start_category("API")
        time.sleep(1)
        monitor.add_test_result("API", "test_health_endpoint", "pass", 0.5)
        time.sleep(0.5)
        monitor.add_test_result("API", "test_available_models_endpoint", "pass", 0.8)
        time.sleep(0.5)
        monitor.add_test_result("API", "test_analyze_endpoint", "pass", 1.2)
        time.sleep(0.7)
        monitor.add_test_result("API", "test_llm_request_endpoint", "pass", 0.9)
        time.sleep(0.5)
        monitor.add_test_result("API", "test_api_errors", "pass", 0.6)
        time.sleep(0.5)
        monitor.add_test_result("API", "test_api_auth", "pass", 0.7)
        monitor.end_category("API")
        
        # Demonstrate AUTH tests
        monitor.start_category("AUTH")
        time.sleep(1)
        monitor.add_test_result("AUTH", "test_jwt_utils", "pass", 0.5)
        time.sleep(0.7)
        monitor.add_test_result("AUTH", "test_auth_edge_cases", "pass", 0.9)
        time.sleep(0.8)
        monitor.add_test_result("AUTH", "test_auth_endpoints", "pass", 0.4)
        time.sleep(0.6)
        monitor.add_test_result("AUTH", "test_e2e_auth_workflow", "pass", 1.5)
        monitor.end_category("AUTH")
        
        # Demonstrate RATE tests
        monitor.start_category("RATE")
        time.sleep(0.8)
        monitor.add_test_result("RATE", "test_rate_limit_service", "pass", 0.7)
        time.sleep(0.6)
        monitor.add_test_result("RATE", "test_rate_limit_middleware", "pass", 0.9)
        monitor.end_category("RATE")
        
        # Demonstrate ORCH tests with a failure
        monitor.start_category("ORCH")
        time.sleep(0.7)
        monitor.add_test_result("ORCH", "test_basic_orchestrator", "pass", 1.1)
        time.sleep(0.9)
        monitor.add_test_result("ORCH", "test_orchestrator", "pass", 0.8)
        time.sleep(1.2)
        monitor.add_test_result("ORCH", "test_orchestrator_with_real_apis", "fail", 2.3, 
                              "Connection timeout when connecting to API provider")
        time.sleep(0.5)
        monitor.add_test_result("ORCH", "test_real_orchestrator", "skip", 0.1, 
                              "Real orchestrator tests require API keys")
        monitor.end_category("ORCH")
        
        # Demonstrate INTEG tests
        monitor.start_category("INTEG")
        time.sleep(0.9)
        monitor.add_test_result("INTEG", "test_e2e_analysis_flow", "pass", 3.2)
        time.sleep(1.5)
        monitor.add_test_result("INTEG", "test_health_check", "pass", 0.4)
        time.sleep(0.6)
        monitor.add_test_result("INTEG", "test_docker_modelrunner", "skip", 0.1,
                             "Docker ModelRunner not available in test environment")
        monitor.end_category("INTEG")
        
        # Demonstrate DOC tests
        monitor.start_category("DOC")
        time.sleep(1.1)
        monitor.add_test_result("DOC", "test_document_upload", "pass", 0.7)
        time.sleep(0.8)
        monitor.add_test_result("DOC", "test_document_analysis", "fail", 1.4,
                             "Failed to extract text from PDF document")
        monitor.end_category("DOC")
        
        # Finalize and save report
        passed, failed, skipped = monitor.finalize()
        monitor.save_report("test_report_demo.json")
        
        return 1 if failed > 0 else 0
        
    except KeyboardInterrupt:
        print("\nTest run aborted by user")
        monitor.finalize()
        return 130


def main():
    """Main function to run the test progress monitor"""
    parser = argparse.ArgumentParser(description="Ultra Test Progress Monitor")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    parser.add_argument("--plan", type=str, help="Path to test plan JSON file")
    parser.add_argument("--report", type=str, default="test_report.json", 
                      help="Path to save test report")
    args = parser.parse_args()
    
    if args.demo:
        return demo_mode()
    
    # Initialize monitor
    monitor = TestProgressMonitor(args.plan)
    
    # TODO: Integration with pytest or other test runners
    # This would involve hooking into pytest's collection and reporting hooks
    
    # For now, we just run the demo mode
    print("Real test runner integration not implemented yet. Use --demo for a demonstration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())