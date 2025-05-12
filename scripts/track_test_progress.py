#!/usr/bin/env python3
"""
Test Progress Tracker for CI Pipeline

This script monitors test progress during CI execution and generates readable progress reports.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

# Test categories and their descriptions
TEST_CATEGORIES = {
    "api": {"description": "API Endpoint Tests", "critical": True},
    "auth": {"description": "Authentication Tests", "critical": True},
    "rate-limit": {"description": "Rate Limiting Tests", "critical": True},
    "document": {"description": "Document Analysis Tests", "critical": True},
    "integration": {"description": "Integration Tests", "critical": True},
    "orchestrator": {"description": "Orchestrator Tests", "critical": False},
    "frontend": {"description": "Frontend Tests", "critical": True},
    "e2e": {"description": "End-to-End Tests", "critical": False},
    "lint": {"description": "Linting", "critical": False},
    "security": {"description": "Security Scan", "critical": False},
}


class TestProgressTracker:
    """Track test progress across multiple categories"""
    
    def __init__(self, output_file: Optional[str] = None):
        """Initialize the test progress tracker"""
        self.start_time = time.time()
        self.results = {}
        self.output_file = output_file
        
        # Initialize results structure
        for category in TEST_CATEGORIES:
            self.results[category] = {
                "status": "pending",
                "start_time": None,
                "end_time": None,
                "duration": None,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "total": 0,
                "details": []
            }
    
    def start_category(self, category: str) -> None:
        """Mark a category as started"""
        if category in self.results:
            self.results[category]["status"] = "running"
            self.results[category]["start_time"] = time.time()
            self._save_results()
    
    def complete_category(self, category: str, success: bool, stats: Dict[str, Any] = None) -> None:
        """Mark a category as completed"""
        if category in self.results:
            self.results[category]["status"] = "success" if success else "failed"
            self.results[category]["end_time"] = time.time()
            
            if self.results[category]["start_time"]:
                self.results[category]["duration"] = (
                    self.results[category]["end_time"] - self.results[category]["start_time"]
                )
            
            if stats:
                self.results[category].update(stats)
            
            self._save_results()
    
    def add_test_result(self, category: str, test_name: str, status: str, 
                        duration: float = 0.0, message: Optional[str] = None) -> None:
        """Add an individual test result"""
        if category in self.results:
            detail = {
                "test": test_name,
                "status": status,
                "duration": duration,
            }
            
            if message:
                detail["message"] = message
                
            self.results[category]["details"].append(detail)
            
            if status == "passed":
                self.results[category]["passed"] += 1
            elif status == "failed":
                self.results[category]["failed"] += 1
            elif status == "skipped":
                self.results[category]["skipped"] += 1
                
            self.results[category]["total"] = (
                self.results[category]["passed"] + 
                self.results[category]["failed"] + 
                self.results[category]["skipped"]
            )
            
            self._save_results()
    
    def _save_results(self) -> None:
        """Save results to a file if specified"""
        if not self.output_file:
            return
            
        # Add summary information
        report = {
            "summary": {
                "start_time": self.start_time,
                "elapsed": time.time() - self.start_time,
                "timestamp": datetime.now().isoformat(),
                "categories_completed": sum(1 for c in self.results.values() 
                                            if c["status"] in ["success", "failed"]),
                "categories_pending": sum(1 for c in self.results.values() 
                                         if c["status"] == "pending"),
                "categories_running": sum(1 for c in self.results.values() 
                                         if c["status"] == "running"),
                "total_passed": sum(c["passed"] for c in self.results.values()),
                "total_failed": sum(c["failed"] for c in self.results.values()),
                "total_skipped": sum(c["skipped"] for c in self.results.values()),
                "success": all(c["status"] != "failed" for c in self.results.values() 
                              if TEST_CATEGORIES.get(category, {}).get("critical", False))
            },
            "categories": self.results
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def print_summary(self) -> None:
        """Print a summary of all test results"""
        elapsed = time.time() - self.start_time
        
        print(f"\n{BOLD}=== ULTRA TEST PROGRESS SUMMARY ==={END}")
        print(f"Started: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Elapsed: {int(elapsed // 60)}m {int(elapsed % 60)}s")
        print()
        
        # Calculate overall stats
        total_passed = sum(c["passed"] for c in self.results.values())
        total_failed = sum(c["failed"] for c in self.results.values())
        total_skipped = sum(c["skipped"] for c in self.results.values())
        total_tests = total_passed + total_failed + total_skipped
        
        # Print category table
        print(f"{BOLD}{'CATEGORY':<15} {'DESCRIPTION':<30} {'STATUS':<10} {'PASS':<6} {'FAIL':<6} {'SKIP':<6} {'TIME':<8}{END}")
        print("-" * 85)
        
        for category, results in self.results.items():
            description = TEST_CATEGORIES.get(category, {}).get("description", "")
            critical = TEST_CATEGORIES.get(category, {}).get("critical", False)
            
            if critical:
                description = f"{BOLD}{description}{END}"
            
            status_str = ""
            if results["status"] == "pending":
                status_str = "Pending"
            elif results["status"] == "running":
                status_str = f"{BLUE}Running{END}"
            elif results["status"] == "success":
                status_str = f"{GREEN}Success{END}"
            elif results["status"] == "failed":
                status_str = f"{RED}Failed{END}"
            
            duration_str = (f"{results['duration']:.1f}s" 
                           if results.get("duration") is not None else "")
            
            passed_str = f"{GREEN}{results['passed']}{END}" if results["passed"] > 0 else "0"
            failed_str = f"{RED}{results['failed']}{END}" if results["failed"] > 0 else "0"
            skipped_str = f"{YELLOW}{results['skipped']}{END}" if results["skipped"] > 0 else "0"
            
            print(f"{category:<15} {description:<30} {status_str:<10} {passed_str:<6} {failed_str:<6} {skipped_str:<6} {duration_str:<8}")
        
        print("-" * 85)
        
        # Print totals
        overall_status = f"{GREEN}PASSING{END}" if total_failed == 0 else f"{RED}FAILING{END}"
        print(f"{BOLD}{'TOTAL':<15} {'':<30} {overall_status:<10} {total_passed:<6} {total_failed:<6} {total_skipped:<6}{END}")
        
        # Print failure details if any
        any_failures = False
        for category, results in self.results.items():
            failed_tests = [d for d in results.get("details", []) if d.get("status") == "failed"]
            if failed_tests:
                if not any_failures:
                    print(f"\n{BOLD}{RED}FAILURES:{END}")
                    any_failures = True
                
                print(f"\n{BOLD}Category: {category}{END}")
                for test in failed_tests:
                    print(f"  {RED}✗{END} {test.get('test')}")
                    if test.get("message"):
                        print(f"    {test.get('message')}")


def parse_json_results(file_path: str) -> Dict[str, Any]:
    """Parse JSON test results file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error parsing results file: {str(e)}")
        return {}


def update_from_test_run(tracker: TestProgressTracker, category: str, results_file: str) -> None:
    """Update tracker from a test run results file"""
    results = parse_json_results(results_file)
    
    # Extract test results
    tests = results.get("tests", [])
    passed = sum(1 for t in tests if t.get("outcome") == "passed")
    failed = sum(1 for t in tests if t.get("outcome") == "failed")
    skipped = sum(1 for t in tests if t.get("outcome") == "skipped")
    success = failed == 0
    
    # Record individual test results
    for test in tests:
        test_name = test.get("nodeid", "unknown")
        outcome = test.get("outcome", "unknown")
        duration = test.get("duration", 0.0)
        
        status = {
            "passed": "passed",
            "failed": "failed",
            "skipped": "skipped"
        }.get(outcome, "unknown")
        
        message = test.get("call", {}).get("longrepr", "") if outcome == "failed" else None
        
        tracker.add_test_result(category, test_name, status, duration, message)
    
    # Complete the category
    stats = {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": passed + failed + skipped
    }
    tracker.complete_category(category, success, stats)


def main():
    """Main function to run the test progress tracker"""
    parser = argparse.ArgumentParser(description="Ultra Test Progress Tracker")
    parser.add_argument("--output", type=str, help="Path to output JSON results file")
    parser.add_argument("--import-results", type=str, help="Import test results from a JSON file")
    parser.add_argument("--category", type=str, help="Test category when importing results")
    args = parser.parse_args()
    
    tracker = TestProgressTracker(args.output)
    
    if args.import_results and args.category:
        tracker.start_category(args.category)
        update_from_test_run(tracker, args.category, args.import_results)
    
    tracker.print_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())