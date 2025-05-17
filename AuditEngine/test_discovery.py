"""
Test script for the discovery phase of AuditEngine
"""

import json
import logging
from pathlib import Path

from discovery.orchestrator import DiscoveryOrchestrator

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_discovery_on_ultra():
    """Test the discovery phase on the Ultra repository itself"""

    # Use the Ultra repository as our test subject
    repo_path = Path("/Users/joshuafield/Documents/Ultra")
    output_dir = repo_path / "AuditEngine" / "test_results"

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

    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_discovery_on_ultra()
