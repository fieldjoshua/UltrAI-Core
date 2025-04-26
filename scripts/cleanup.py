#!/usr/bin/env python3
"""
Cleanup script for Ultra project
This script removes unnecessary files and organizes the codebase
"""

import glob
import os
import re
import shutil
from pathlib import Path

# List of unnecessary file/directory patterns to clean up
UNNECESSARY_FILES = [
    # Test and debug files
    "test_*.py",
    "debug*.py",
    "minimal_test.py",
    "search_pypi.py",
    # Backup files
    "*_backup.py",
    "*_backup*.py",
    # Generated files
    "*.log",
    "stdout.txt",
    "stderr.txt",
    "trace.log",
    "test_output.txt",
    # Old versions/experiments
    "ultra_hyper_m2.py",
    # In general, try to keep files that begin with "ultra_" as they are part of the main codebase
    # But clean up any that are clearly duplicates or development files
]


# Create archive directory for old files if not exists
def create_archive_dir():
    archive_dir = Path("./archive")
    if not archive_dir.exists():
        archive_dir.mkdir()
    return archive_dir


def clean_responses_dir():
    """Archive old response files to save disk space"""
    responses_dir = Path("./responses")
    if not responses_dir.exists():
        return

    archive_dir = create_archive_dir() / "responses"
    if not archive_dir.exists():
        archive_dir.mkdir(parents=True)

    # Move entire responses directory to archive
    shutil.move(str(responses_dir), str(archive_dir))


def clean_runs_dir():
    """Archive run logs to save disk space"""
    runs_dir = Path("./runs")
    if not runs_dir.exists():
        return

    archive_dir = create_archive_dir() / "runs"
    if not archive_dir.exists():
        archive_dir.mkdir(parents=True)

    # Move entire runs directory to archive
    shutil.move(str(runs_dir), str(archive_dir))


def clean_duplicate_ultrai_dirs():
    """Clean duplicate UltrAI directories"""
    ultrai_dir = Path("./UltrAI")
    if ultrai_dir.exists() and ultrai_dir.is_dir():
        archive_dir = create_archive_dir() / "UltrAI"
        if not archive_dir.exists():
            archive_dir.mkdir(parents=True)

        # Move entire UltrAI directory to archive
        shutil.move(str(ultrai_dir), str(archive_dir))


def clean_unnecessary_files():
    """Clean unnecessary files based on patterns"""
    archive_dir = create_archive_dir() / "misc"
    if not archive_dir.exists():
        archive_dir.mkdir(parents=True)

    for pattern in UNNECESSARY_FILES:
        for file_path in glob.glob(pattern):
            if os.path.isfile(file_path):
                # Move to archive instead of deleting
                try:
                    shutil.move(
                        file_path, str(archive_dir / os.path.basename(file_path))
                    )
                    print(f"Moved {file_path} to archive")
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")


def clean_analysis_results():
    """Clean up analysis result files"""
    archive_dir = create_archive_dir() / "results"
    if not archive_dir.exists():
        archive_dir.mkdir(parents=True)

    # Look for analysis result JSON files
    for file_path in glob.glob("llm_analysis_results_*.json"):
        if os.path.isfile(file_path):
            try:
                shutil.move(file_path, str(archive_dir / os.path.basename(file_path)))
                print(f"Moved {file_path} to archive")
            except Exception as e:
                print(f"Error moving {file_path}: {e}")


def clean_node_modules():
    """Clean node_modules directory"""
    node_modules_dir = Path("./node_modules")
    if node_modules_dir.exists() and node_modules_dir.is_dir():
        try:
            shutil.rmtree(str(node_modules_dir))
            print(f"Removed node_modules directory")
        except Exception as e:
            print(f"Error removing node_modules: {e}")


def main():
    """Main cleanup function"""
    print("Starting Ultra project cleanup...")

    # Create archive directory
    archive_dir = create_archive_dir()
    print(f"Created archive directory at {archive_dir}")

    # Clean responses directory
    clean_responses_dir()

    # Clean runs directory
    clean_runs_dir()

    # Clean duplicate UltrAI directory
    clean_duplicate_ultrai_dirs()

    # Clean unnecessary files
    clean_unnecessary_files()

    # Clean analysis results
    clean_analysis_results()

    # Clean node_modules
    clean_node_modules()

    print("Cleanup complete. Files have been moved to the archive directory.")


if __name__ == "__main__":
    main()
