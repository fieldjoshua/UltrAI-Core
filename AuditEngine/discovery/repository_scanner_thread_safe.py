"""
Thread-safe Repository Scanner Module

Modified version with thread-safe file system operations for parallel processing.
"""

import json
import logging
import os
import subprocess
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Global lock for file system operations
fs_lock = threading.Lock()


@dataclass
class RepositoryMetadata:
    """Repository metadata and statistics"""

    path: str
    name: str
    remote_url: Optional[str]
    default_branch: str
    total_commits: int
    active_branches: List[str]
    contributors: List[Dict[str, Any]]
    creation_date: datetime
    last_commit_date: datetime


@dataclass
class FileStructure:
    """File structure analysis results"""

    total_files: int
    total_directories: int
    file_types: Dict[str, int]
    largest_files: List[Dict[str, Any]]
    directory_tree: Dict[str, Any]
    ignored_patterns: List[str]


class ThreadSafeRepositoryScanner:
    """
    Thread-safe version of RepositoryScanner for parallel processing
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        self.metadata = None
        self.file_structure = None

    def scan(self) -> Dict[str, Any]:
        """
        Perform complete repository scan with thread safety

        Returns:
            Dictionary containing repository metadata and structure analysis
        """
        logger.info(f"Starting repository scan: {self.repo_path}")

        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "metadata": self._scan_git_metadata(),
            "file_structure": self._analyze_file_structure(),
            "language_composition": self._analyze_language_composition(),
            "directory_analysis": self._analyze_directory_patterns(),
        }

        logger.info("Repository scan completed")
        return results

    def _scan_git_metadata(self) -> Dict[str, Any]:
        """Extract git repository metadata"""
        if not self._is_git_repository():
            logger.warning("Not a git repository, skipping metadata scan")
            return {}

        metadata = RepositoryMetadata(
            path=str(self.repo_path),
            name=self.repo_path.name,
            remote_url=self._get_remote_url(),
            default_branch=self._get_default_branch(),
            total_commits=self._count_commits(),
            active_branches=self._list_branches(),
            contributors=self._analyze_contributors(),
            creation_date=self._get_creation_date(),
            last_commit_date=self._get_last_commit_date(),
        )

        self.metadata = metadata
        return asdict(metadata)

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze repository file structure with thread safety"""
        file_types = {}
        total_files = 0
        total_dirs = 0
        largest_files = []

        # Use lock for file system operations
        with fs_lock:
            for root, dirs, files in os.walk(self.repo_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ["node_modules", "__pycache__", "venv"]
                ]
                total_dirs += len(dirs)

                for file in files:
                    if file.startswith("."):
                        continue

                    file_path = Path(root) / file
                    total_files += 1

                    # Track file types
                    ext = file_path.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1

                    # Track largest files
                    try:
                        size = file_path.stat().st_size
                        largest_files.append(
                            {
                                "path": str(file_path.relative_to(self.repo_path)),
                                "size": size,
                            }
                        )
                    except OSError:
                        pass

        # Sort and limit largest files
        largest_files.sort(key=lambda x: x["size"], reverse=True)
        largest_files = largest_files[:10]

        structure = FileStructure(
            total_files=total_files,
            total_directories=total_dirs,
            file_types=file_types,
            largest_files=largest_files,
            directory_tree=self._build_directory_tree(),
            ignored_patterns=self._get_ignored_patterns(),
        )

        self.file_structure = structure
        return asdict(structure)

    def _analyze_language_composition(self) -> Dict[str, Any]:
        """Analyze programming language composition"""
        language_stats = {}
        language_mapping = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React",
            ".tsx": "React TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".r": "R",
            ".m": "MATLAB",
            ".jl": "Julia",
            ".sh": "Shell",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".json": "JSON",
            ".xml": "XML",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "Sass",
            ".less": "Less",
            ".sql": "SQL",
            ".md": "Markdown",
            ".rst": "reStructuredText",
            ".tex": "LaTeX",
        }

        if self.file_structure:
            for ext, count in self.file_structure.file_types.items():
                language = language_mapping.get(ext, "Other")
                language_stats[language] = language_stats.get(language, 0) + count

        # Calculate percentages
        total = sum(language_stats.values())
        language_percentages = {}
        if total > 0:
            for lang, count in language_stats.items():
                language_percentages[lang] = {
                    "count": count,
                    "percentage": round((count / total) * 100, 2),
                }

        return {
            "languages": language_percentages,
            "primary_language": (
                max(language_stats.items(), key=lambda x: x[1])[0]
                if language_stats
                else None
            ),
            "total_files_analyzed": total,
        }

    def _analyze_directory_patterns(self) -> Dict[str, Any]:
        """Analyze directory structure patterns with thread safety"""
        patterns = {
            "has_tests": False,
            "has_docs": False,
            "has_ci": False,
            "has_docker": False,
            "has_frontend": False,
            "has_backend": False,
            "package_managers": [],
            "build_tools": [],
            "architecture_style": "unknown",
        }

        # Use lock for file system operations
        with fs_lock:
            for root, dirs, files in os.walk(self.repo_path):
                rel_root = Path(root).relative_to(self.repo_path)

                # Test directories
                if any(d in dirs for d in ["tests", "test", "__tests__", "spec"]):
                    patterns["has_tests"] = True

                # Documentation
                if any(d in dirs for d in ["docs", "documentation", "doc"]):
                    patterns["has_docs"] = True

                # CI/CD
                if ".github" in dirs or ".gitlab-ci.yml" in files:
                    patterns["has_ci"] = True

                # Docker
                if "Dockerfile" in files or "docker-compose.yml" in files:
                    patterns["has_docker"] = True

                # Frontend/Backend
                if any(d in dirs for d in ["frontend", "client", "ui", "web"]):
                    patterns["has_frontend"] = True
                if any(d in dirs for d in ["backend", "server", "api"]):
                    patterns["has_backend"] = True

                # Package managers
                if "package.json" in files:
                    patterns["package_managers"].append("npm/yarn")
                if "requirements.txt" in files or "Pipfile" in files:
                    patterns["package_managers"].append("pip")
                if "pom.xml" in files:
                    patterns["package_managers"].append("maven")
                if "build.gradle" in files:
                    patterns["package_managers"].append("gradle")
                if "Cargo.toml" in files:
                    patterns["package_managers"].append("cargo")
                if "go.mod" in files:
                    patterns["package_managers"].append("go modules")

                # Build tools
                if "Makefile" in files:
                    patterns["build_tools"].append("make")
                if "webpack.config.js" in files:
                    patterns["build_tools"].append("webpack")
                if "vite.config.js" in files or "vite.config.ts" in files:
                    patterns["build_tools"].append("vite")

        # Determine architecture style
        if patterns["has_frontend"] and patterns["has_backend"]:
            patterns["architecture_style"] = "full-stack"
        elif patterns["has_frontend"]:
            patterns["architecture_style"] = "frontend-only"
        elif patterns["has_backend"]:
            patterns["architecture_style"] = "backend-only"
        elif any("lib" in d or "src" in d for _, d, _ in os.walk(self.repo_path)):
            patterns["architecture_style"] = "library"

        return patterns

    def _is_git_repository(self) -> bool:
        """Check if directory is a git repository"""
        return (self.repo_path / ".git").exists()

    def _run_git_command(self, command: List[str]) -> str:
        """Run git command and return output"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e}")
            return ""

    def _get_remote_url(self) -> Optional[str]:
        """Get remote repository URL"""
        return self._run_git_command(["config", "--get", "remote.origin.url"]) or None

    def _get_default_branch(self) -> str:
        """Get default branch name"""
        branch = self._run_git_command(["symbolic-ref", "refs/remotes/origin/HEAD"])
        return branch.split("/")[-1] if branch else "main"

    def _count_commits(self) -> int:
        """Count total commits"""
        count = self._run_git_command(["rev-list", "--all", "--count"])
        return int(count) if count.isdigit() else 0

    def _list_branches(self) -> List[str]:
        """List all branches"""
        branches = self._run_git_command(["branch", "-r"])
        return [b.strip() for b in branches.split("\n") if b.strip()]

    def _analyze_contributors(self) -> List[Dict[str, Any]]:
        """Analyze repository contributors"""
        # Get contributor stats
        stats = self._run_git_command(["shortlog", "-sn", "--all"])
        contributors = []

        for line in stats.split("\n"):
            if line.strip():
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    commits, name = parts
                    contributors.append({"name": name, "commits": int(commits.strip())})

        return contributors[:10]  # Top 10 contributors

    def _get_creation_date(self) -> datetime:
        """Get repository creation date (first commit)"""
        date_str = self._run_git_command(["log", "--reverse", "--format=%aI", "-1"])
        try:
            return datetime.fromisoformat(date_str.replace("T", " ").split("+")[0])
        except:
            return datetime.now()

    def _get_last_commit_date(self) -> datetime:
        """Get last commit date"""
        date_str = self._run_git_command(["log", "-1", "--format=%aI"])
        try:
            return datetime.fromisoformat(date_str.replace("T", " ").split("+")[0])
        except:
            return datetime.now()

    def _build_directory_tree(self, max_depth: int = 3) -> Dict[str, Any]:
        """Build directory tree representation with thread safety"""

        def build_tree(path: Path, current_depth: int = 0):
            if current_depth > max_depth:
                return None

            tree = {"name": path.name, "type": "directory", "children": []}

            try:
                with fs_lock:
                    for item in sorted(path.iterdir()):
                        if item.name.startswith("."):
                            continue
                        if item.is_dir() and item.name not in [
                            "node_modules",
                            "__pycache__",
                            "venv",
                        ]:
                            subtree = build_tree(item, current_depth + 1)
                            if subtree:
                                tree["children"].append(subtree)
                        elif item.is_file():
                            tree["children"].append(
                                {
                                    "name": item.name,
                                    "type": "file",
                                    "size": item.stat().st_size,
                                }
                            )
            except PermissionError:
                pass

            return tree

        return build_tree(self.repo_path)

    def _get_ignored_patterns(self) -> List[str]:
        """Get gitignore patterns"""
        gitignore_path = self.repo_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                return [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        return []
