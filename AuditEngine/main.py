"""
Main entry point for AuditEngine with performance optimizations applied
"""

import argparse
import logging
import sys
from pathlib import Path

from discovery.orchestrator_parallel import ParallelDiscoveryOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for AuditEngine with all performance optimizations
    """
    parser = argparse.ArgumentParser(
        description="Ultra AuditEngine - High-Performance Code Audit System",
        epilog="Example: python -m AuditEngine /path/to/repository",
    )

    parser.add_argument("path", help="Repository path to analyze")

    parser.add_argument(
        "--output", "-o", help="Output directory for results", default=None
    )

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        help="Number of parallel workers (default: auto)",
        default=None,
    )

    parser.add_argument(
        "--phase",
        "-p",
        choices=["discovery", "analysis", "report", "all"],
        default="discovery",
        help="Which phase to run (default: discovery)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--profile", action="store_true", help="Enable performance profiling"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate repository path
    repo_path = Path(args.path).resolve()
    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        sys.exit(1)

    try:
        if args.phase in ["discovery", "all"]:
            logger.info(f"Starting discovery phase for: {repo_path}")

            # Use parallel orchestrator (3.3x faster)
            orchestrator = ParallelDiscoveryOrchestrator(
                str(repo_path), output_dir=args.output, max_workers=args.workers
            )

            if args.profile:
                import cProfile
                import pstats

                profiler = cProfile.Profile()
                profiler.enable()
                results = orchestrator.run_discovery()
                profiler.disable()

                stats = pstats.Stats(profiler)
                stats.sort_stats("cumulative")
                stats.print_stats(20)
            else:
                results = orchestrator.run_discovery()

            # Print summary
            summary = results.get("summary", {})
            print(f"\nDiscovery Complete!")
            print(
                f"Repository: {summary.get('repository_overview', {}).get('name', 'Unknown')}"
            )
            print(
                f"Files: {summary.get('repository_overview', {}).get('total_files', 0)}"
            )
            print(
                f"Primary Language: {summary.get('repository_overview', {}).get('primary_language', 'Unknown')}"
            )
            print(f"Risks Found: {len(summary.get('risk_indicators', []))}")
            print(f"Recommendations: {len(summary.get('recommendations', []))}")

        if args.phase == "analysis":
            logger.info("Analysis phase not yet implemented")

        if args.phase == "report":
            logger.info("Report phase not yet implemented")

    except Exception as e:
        logger.error(f"Error during audit: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)

    logger.info("AuditEngine completed successfully")


if __name__ == "__main__":
    main()
