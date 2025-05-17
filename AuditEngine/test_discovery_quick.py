"""
Quick test script for the discovery phase - analyzes the AuditEngine subdirectory only
"""

import json
import logging
from pathlib import Path

from discovery.orchestrator import DiscoveryOrchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_discovery_on_auditengine():
    """Test the discovery phase on the AuditEngine subdirectory"""

    # Use the AuditEngine directory itself as a smaller test subject
    repo_path = Path("/Users/joshuafield/Documents/Ultra/AuditEngine")
    output_dir = repo_path / "test_results"

    print(f"Testing discovery phase on: {repo_path}")
    print(f"Output directory: {output_dir}")

    try:
        # Create orchestrator
        orchestrator = DiscoveryOrchestrator(str(repo_path), str(output_dir))

        # Run discovery
        results = orchestrator.run_discovery()

        # Print summary
        print("\n=== Discovery Results Summary ===")
        summary = results.get("summary", {})
        overview = summary.get("repository_overview", {})

        print(f"\nRepository Overview:")
        print(f"  Name: {overview.get('name', 'Unknown')}")
        print(f"  Primary Language: {overview.get('primary_language', 'Unknown')}")
        print(f"  Total Files: {overview.get('total_files', 0)}")
        print(f"  Total Commits: {overview.get('total_commits', 0)}")
        print(f"  Contributors: {overview.get('contributors', 0)}")
        print(f"  Has Tests: {overview.get('has_tests', False)}")
        print(f"  Has Docs: {overview.get('has_docs', False)}")
        print(f"  Has CI: {overview.get('has_ci', False)}")

        print(f"\nKey Metrics:")
        metrics = summary.get("key_metrics", {})
        print(f"  Code Lines: {metrics.get('code_lines', 0)}")
        print(
            f"  Active Contributors (30d): {metrics.get('active_contributors_30d', 0)}"
        )
        print(f"  Collaboration Score: {metrics.get('collaboration_score', 0)}")
        print(f"  Commit Quality Score: {metrics.get('commit_message_quality', 0)}")
        print(f"  Activity Score: {metrics.get('activity_score', 0)}")

        print(f"\nRisk Indicators: {len(summary.get('risk_indicators', []))}")
        for risk in summary.get("risk_indicators", []):
            print(f"  - [{risk.get('severity')}] {risk.get('description')}")

        print(f"\nRecommendations: {len(summary.get('recommendations', []))}")
        for rec in summary.get("recommendations", []):
            print(f"  - [{rec.get('priority')}] {rec.get('action')}")

        print(f"\n✅ Discovery phase completed successfully!")
        print(f"Full results saved to: {output_dir}")

        # Let's also create a simple test without git
        test_simple_directory()

    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
        import traceback

        traceback.print_exc()


def test_simple_directory():
    """Test on a simple directory structure without git"""
    print("\n\n=== Testing Simple Directory Structure ===")

    # Create a simple test directory
    test_dir = Path("/Users/joshuafield/Documents/Ultra/AuditEngine/test_simple")
    test_dir.mkdir(exist_ok=True)

    # Create some test files
    (test_dir / "test.py").write_text("def hello():\n    print('Hello')\n")
    (test_dir / "requirements.txt").write_text("requests>=2.28.0\npackaging>=21.0\n")
    (test_dir / "README.md").write_text("# Test Project\n\nThis is a test.")

    try:
        orchestrator = DiscoveryOrchestrator(str(test_dir), str(test_dir / "results"))
        results = orchestrator.run_discovery()

        overview = results.get("summary", {}).get("repository_overview", {})
        print(f"\nSimple Directory Results:")
        print(f"  Total Files: {overview.get('total_files', 0)}")
        print(f"  Primary Language: {overview.get('primary_language', 'Unknown')}")
        print(f"  Has Tests: {overview.get('has_tests', False)}")
        print(f"  Has Docs: {overview.get('has_docs', False)}")

        print("\n✅ Simple directory test completed!")

    except Exception as e:
        print(f"\n❌ Error in simple test: {e}")


if __name__ == "__main__":
    # First test on AuditEngine directory
    test_discovery_on_auditengine()
