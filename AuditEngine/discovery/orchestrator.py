"""
Discovery Orchestrator

Coordinates all discovery phase components for comprehensive repository analysis.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .dependency_mapper import DependencyMapper
from .metrics_collector import MetricsCollector
from .repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


class DiscoveryOrchestrator:
    """
    Orchestrates the discovery phase of the comprehensive audit
    """

    def __init__(self, repo_path: str, output_dir: Optional[str] = None):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        # Set up output directory
        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        else:
            self.output_dir = self.repo_path / "audit_results"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.scanner = RepositoryScanner(str(self.repo_path))
        self.mapper = DependencyMapper(str(self.repo_path))
        self.collector = MetricsCollector(str(self.repo_path))

    def run_discovery(self) -> Dict[str, Any]:
        """
        Run complete discovery phase

        Returns:
            Dictionary containing all discovery results
        """
        logger.info(f"Starting discovery phase for: {self.repo_path}")
        start_time = datetime.now()

        results = {
            "discovery_metadata": {
                "repository_path": str(self.repo_path),
                "start_time": start_time.isoformat(),
                "phase": "discovery",
                "version": "1.0.0",
            },
            "repository_scan": {},
            "dependency_analysis": {},
            "metrics_collection": {},
            "summary": {},
            "errors": [],
        }

        # Run repository scan
        try:
            logger.info("Running repository scan...")
            results["repository_scan"] = self.scanner.scan()
            self._save_intermediate_results(
                "repository_scan.json", results["repository_scan"]
            )
        except Exception as e:
            logger.error(f"Repository scan failed: {e}")
            results["errors"].append(
                {
                    "component": "repository_scanner",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Run dependency analysis
        try:
            logger.info("Running dependency analysis...")
            results["dependency_analysis"] = self.mapper.analyze()
            self._save_intermediate_results(
                "dependency_analysis.json", results["dependency_analysis"]
            )
        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            results["errors"].append(
                {
                    "component": "dependency_mapper",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Run metrics collection
        try:
            logger.info("Running metrics collection...")
            results["metrics_collection"] = self.collector.collect()
            self._save_intermediate_results(
                "metrics_collection.json", results["metrics_collection"]
            )
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            results["errors"].append(
                {
                    "component": "metrics_collector",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Generate summary
        end_time = datetime.now()
        results["discovery_metadata"]["end_time"] = end_time.isoformat()
        results["discovery_metadata"]["duration_seconds"] = (
            end_time - start_time
        ).total_seconds()

        results["summary"] = self._generate_summary(results)

        # Save complete results
        self._save_complete_results(results)

        logger.info(
            f"Discovery phase completed in {results['discovery_metadata']['duration_seconds']:.2f} seconds"
        )
        return results

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of discovery findings"""
        summary = {
            "repository_overview": {},
            "key_metrics": {},
            "risk_indicators": [],
            "recommendations": [],
        }

        # Repository overview
        if results["repository_scan"]:
            scan = results["repository_scan"]
            summary["repository_overview"] = {
                "name": scan.get("metadata", {}).get("name", "Unknown"),
                "primary_language": scan.get("language_composition", {}).get(
                    "primary_language", "Unknown"
                ),
                "total_files": scan.get("file_structure", {}).get("total_files", 0),
                "total_commits": scan.get("metadata", {}).get("total_commits", 0),
                "contributors": scan.get("metadata", {}).get("total_contributors", 0),
                "has_tests": scan.get("directory_analysis", {}).get("has_tests", False),
                "has_docs": scan.get("directory_analysis", {}).get("has_docs", False),
                "has_ci": scan.get("directory_analysis", {}).get("has_ci", False),
            }

        # Key metrics
        if results["metrics_collection"]:
            metrics = results["metrics_collection"]
            summary["key_metrics"] = {
                "code_lines": metrics.get("code_metrics", {}).get("code_lines", 0),
                "test_coverage": self._estimate_test_coverage(results),
                "active_contributors_30d": metrics.get("contributor_metrics", {}).get(
                    "active_contributors_30d", 0
                ),
                "collaboration_score": metrics.get("contributor_metrics", {}).get(
                    "collaboration_score", 0
                ),
                "commit_message_quality": metrics.get("commit_metrics", {})
                .get("commit_message_quality", {})
                .get("quality_score", 0),
                "activity_score": metrics.get("activity_trends", {}).get(
                    "recent_activity_score", 0
                ),
            }

        # Risk indicators
        summary["risk_indicators"] = self._identify_risks(results)

        # Generate recommendations
        summary["recommendations"] = self._generate_recommendations(
            results, summary["risk_indicators"]
        )

        return summary

    def _identify_risks(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential risks based on discovery findings"""
        risks = []

        # Check for outdated dependencies
        deps = results.get("dependency_analysis", {})
        if deps.get("python", {}).get("dependencies"):
            python_deps = deps["python"]["dependencies"]
            outdated_count = sum(
                1 for dep in python_deps.values() if dep.get("is_outdated")
            )
            if outdated_count > 0:
                risks.append(
                    {
                        "category": "dependencies",
                        "severity": "medium",
                        "description": f"{outdated_count} outdated Python dependencies found",
                        "impact": "potential security vulnerabilities and compatibility issues",
                    }
                )

        # Check for activity decline
        trends = results.get("metrics_collection", {}).get("activity_trends", {})
        if trends.get("commit_frequency_trend") == "declining":
            risks.append(
                {
                    "category": "maintenance",
                    "severity": "high",
                    "description": "Declining commit frequency detected",
                    "impact": "potential project abandonment or reduced maintenance",
                }
            )

        # Check for low contributor diversity
        contrib_metrics = results.get("metrics_collection", {}).get(
            "contributor_metrics", {}
        )
        if contrib_metrics.get("total_contributors", 0) < 3:
            risks.append(
                {
                    "category": "sustainability",
                    "severity": "medium",
                    "description": "Low contributor diversity",
                    "impact": "bus factor risk, sustainability concerns",
                }
            )

        # Check for missing tests
        if (
            not results.get("repository_scan", {})
            .get("directory_analysis", {})
            .get("has_tests")
        ):
            risks.append(
                {
                    "category": "quality",
                    "severity": "high",
                    "description": "No test directory found",
                    "impact": "code quality and reliability concerns",
                }
            )

        # Check for missing documentation
        if (
            not results.get("repository_scan", {})
            .get("directory_analysis", {})
            .get("has_docs")
        ):
            risks.append(
                {
                    "category": "documentation",
                    "severity": "medium",
                    "description": "Limited documentation found",
                    "impact": "difficult onboarding and maintenance",
                }
            )

        return risks

    def _generate_recommendations(
        self, results: Dict[str, Any], risks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings and risks"""
        recommendations = []

        # Recommendations based on risks
        for risk in risks:
            if risk["category"] == "dependencies":
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "dependencies",
                        "action": "Update outdated dependencies",
                        "details": "Run dependency update tools and test thoroughly",
                        "effort": "medium",
                    }
                )
            elif risk["category"] == "maintenance":
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "maintenance",
                        "action": "Review project maintenance status",
                        "details": "Assess if project is still actively maintained or needs transition planning",
                        "effort": "low",
                    }
                )
            elif (
                risk["category"] == "quality" and "test" in risk["description"].lower()
            ):
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "quality",
                        "action": "Implement test suite",
                        "details": "Add unit tests, integration tests, and CI pipeline",
                        "effort": "high",
                    }
                )
            elif risk["category"] == "documentation":
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "documentation",
                        "action": "Improve documentation",
                        "details": "Add README, API documentation, and contribution guidelines",
                        "effort": "medium",
                    }
                )

        # General recommendations
        metrics = results.get("metrics_collection", {})
        if (
            metrics.get("commit_metrics", {})
            .get("commit_message_quality", {})
            .get("quality_score", 10)
            < 7
        ):
            recommendations.append(
                {
                    "priority": "low",
                    "category": "development_practices",
                    "action": "Improve commit message quality",
                    "details": "Adopt conventional commit format and add commit hooks",
                    "effort": "low",
                }
            )

        if (
            not results.get("repository_scan", {})
            .get("directory_analysis", {})
            .get("has_ci")
        ):
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "automation",
                    "action": "Implement CI/CD pipeline",
                    "details": "Add GitHub Actions or similar for automated testing and deployment",
                    "effort": "medium",
                }
            )

        return recommendations

    def _estimate_test_coverage(self, results: Dict[str, Any]) -> float:
        """Estimate test coverage based on available metrics"""
        # This is a simple heuristic - in real implementation would use actual coverage tools
        if (
            not results.get("repository_scan", {})
            .get("directory_analysis", {})
            .get("has_tests")
        ):
            return 0.0

        # Simple estimation based on test file count vs source file count
        # This is very rough and should be replaced with actual coverage metrics
        return 50.0  # Placeholder

    def _save_intermediate_results(self, filename: str, data: Dict[str, Any]) -> None:
        """Save intermediate results to file"""
        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.debug(f"Saved intermediate results to: {output_path}")

    def _save_complete_results(self, results: Dict[str, Any]) -> None:
        """Save complete discovery results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"discovery_complete_{timestamp}.json"

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Also save as latest
        latest_path = self.output_dir / "discovery_latest.json"
        with open(latest_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Complete discovery results saved to: {output_path}")


def main():
    """CLI interface for discovery orchestrator"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run discovery phase of comprehensive audit"
    )
    parser.add_argument("path", help="Repository path to analyze")
    parser.add_argument("--output", "-o", help="Output directory", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    else:
        logging.basicConfig(level=logging.WARNING)

    orchestrator = DiscoveryOrchestrator(args.path, args.output)
    results = orchestrator.run_discovery()

    print(f"\nDiscovery phase complete!")
    print(f"Results saved to: {orchestrator.output_dir}")
    print(f"\nSummary:")
    print(f"- Repository: {results['summary']['repository_overview']['name']}")
    print(
        f"- Primary Language: {results['summary']['repository_overview']['primary_language']}"
    )
    print(f"- Total Files: {results['summary']['repository_overview']['total_files']}")
    print(
        f"- Contributors: {results['summary']['repository_overview']['contributors']}"
    )
    print(f"- Risk Indicators: {len(results['summary']['risk_indicators'])}")
    print(f"- Recommendations: {len(results['summary']['recommendations'])}")


if __name__ == "__main__":
    main()
