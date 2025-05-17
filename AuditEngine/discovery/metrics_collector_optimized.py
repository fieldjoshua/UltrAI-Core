"""
Optimized Metrics Collector Module

Uses NumPy and Numba for performance-critical calculations.
"""

import json
import logging
import re
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from numba import jit, prange

logger = logging.getLogger(__name__)


@dataclass
class CodeMetrics:
    """Code metrics for a repository"""

    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    language_breakdown: Dict[str, Dict[str, int]]
    file_count_by_language: Dict[str, int]


@dataclass
class ContributorMetrics:
    """Contributor activity metrics"""

    total_contributors: int
    active_contributors_30d: int
    active_contributors_90d: int
    contributor_stats: List[Dict[str, Any]]
    commit_distribution: Dict[str, int]
    collaboration_score: float


@dataclass
class CommitMetrics:
    """Commit pattern metrics"""

    total_commits: int
    commits_by_day: Dict[str, int]
    commits_by_hour: Dict[int, int]
    commits_by_month: Dict[str, int]
    average_commits_per_day: float
    busiest_day: str
    busiest_hour: int
    commit_message_quality: Dict[str, Any]


@jit(nopython=True)
def _calculate_complexity_score(values: np.ndarray) -> float:
    """JIT-compiled complexity calculation"""
    if len(values) == 0:
        return 0.0

    # Calculate various metrics
    mean_val = np.mean(values)
    std_val = np.std(values)
    max_val = np.max(values)

    # Simple complexity formula
    complexity = (mean_val + std_val) / (max_val + 1.0)
    return min(complexity * 10, 10.0)


@jit(nopython=True, parallel=True)
def _process_line_counts(lines: np.ndarray, comment_markers: np.ndarray) -> tuple:
    """JIT-compiled line counting with parallel processing"""
    code_count = 0
    comment_count = 0
    blank_count = 0

    for i in prange(len(lines)):
        line_len = lines[i]
        is_comment = comment_markers[i]

        if line_len == 0:
            blank_count += 1
        elif is_comment:
            comment_count += 1
        else:
            code_count += 1

    return code_count, comment_count, blank_count


class OptimizedMetricsCollector:
    """
    Optimized metrics collector using NumPy and Numba
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def collect(self) -> Dict[str, Any]:
        """
        Collect all metrics with optimizations

        Returns:
            Dictionary containing all collected metrics
        """
        logger.info(f"Starting optimized metrics collection: {self.repo_path}")

        results = {
            "collection_timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "code_metrics": self._collect_code_metrics_optimized(),
            "contributor_metrics": self._collect_contributor_metrics(),
            "commit_metrics": self._collect_commit_metrics_optimized(),
            "activity_trends": self._analyze_activity_trends_optimized(),
        }

        logger.info("Optimized metrics collection completed")
        return results

    def _collect_code_metrics_optimized(self) -> Dict[str, Any]:
        """Collect code metrics using NumPy for better performance"""
        metrics = CodeMetrics(
            total_lines=0,
            code_lines=0,
            comment_lines=0,
            blank_lines=0,
            language_breakdown={},
            file_count_by_language={},
        )

        # Try to use cloc if available
        if self._command_exists("cloc"):
            metrics = self._collect_cloc_metrics()
        else:
            # Use optimized custom implementation
            metrics = self._collect_custom_metrics_optimized()

        return asdict(metrics)

    def _collect_custom_metrics_optimized(self) -> CodeMetrics:
        """Optimized custom implementation using NumPy"""
        metrics = CodeMetrics(
            total_lines=0,
            code_lines=0,
            comment_lines=0,
            blank_lines=0,
            language_breakdown=defaultdict(
                lambda: {"files": 0, "code": 0, "comment": 0, "blank": 0}
            ),
            file_count_by_language=defaultdict(int),
        )

        language_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
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
        }

        # Batch process files
        file_batch = []

        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".") for part in file_path.parts
            ):
                ext = file_path.suffix.lower()
                if ext in language_extensions:
                    file_batch.append((file_path, language_extensions[ext]))

        # Process files in batches
        for file_path, lang in file_batch:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                # Convert to numpy arrays for faster processing
                line_lengths = np.array([len(line.strip()) for line in lines])
                comment_markers = np.array(
                    [
                        self._is_comment_optimized(line.strip(), file_path.suffix)
                        for line in lines
                    ]
                )

                # Use JIT-compiled function
                code_count, comment_count, blank_count = _process_line_counts(
                    line_lengths, comment_markers
                )

                metrics.total_lines += len(lines)
                metrics.code_lines += code_count
                metrics.comment_lines += comment_count
                metrics.blank_lines += blank_count

                metrics.file_count_by_language[lang] += 1
                metrics.language_breakdown[lang]["files"] += 1
                metrics.language_breakdown[lang]["code"] += code_count
                metrics.language_breakdown[lang]["comment"] += comment_count
                metrics.language_breakdown[lang]["blank"] += blank_count

            except Exception as e:
                logger.debug(f"Error reading file {file_path}: {e}")

        # Convert defaultdict to regular dict
        metrics.language_breakdown = dict(metrics.language_breakdown)
        metrics.file_count_by_language = dict(metrics.file_count_by_language)

        return metrics

    def _is_comment_optimized(self, line: str, extension: str) -> bool:
        """Optimized comment detection"""
        if not line:
            return False

        comment_starts = {
            ".py": "#",
            ".rb": "#",
            ".r": "#",
            ".js": ["//", "/*"],
            ".ts": ["//", "/*"],
            ".java": ["//", "/*"],
            ".cpp": ["//", "/*"],
            ".c": ["//", "/*"],
            ".cs": ["//", "/*"],
            ".go": ["//", "/*"],
            ".rs": ["//", "/*"],
            ".php": ["//", "/*", "#"],
            ".swift": ["//", "/*"],
            ".kt": ["//", "/*"],
            ".scala": ["//", "/*"],
        }

        patterns = comment_starts.get(extension, [])
        if isinstance(patterns, str):
            return line.startswith(patterns)
        return any(line.startswith(p) for p in patterns)

    def _collect_commit_metrics_optimized(self) -> Dict[str, Any]:
        """Collect commit metrics with NumPy optimizations"""
        metrics = CommitMetrics(
            total_commits=0,
            commits_by_day={},
            commits_by_hour={},
            commits_by_month={},
            average_commits_per_day=0.0,
            busiest_day="",
            busiest_hour=0,
            commit_message_quality={},
        )

        if not self._is_git_repository():
            logger.warning("Not a git repository, skipping commit metrics")
            return asdict(metrics)

        # Get total commits
        metrics.total_commits = self._count_total_commits()

        # Get commit timestamps more efficiently
        timestamps = self._get_commit_timestamps_optimized()

        if timestamps:
            # Convert to numpy array for faster processing
            ts_array = np.array([ts.timestamp() for ts in timestamps])

            # Calculate distributions using NumPy
            metrics.commits_by_day = self._calculate_day_distribution(timestamps)
            metrics.commits_by_hour = self._calculate_hour_distribution(timestamps)
            metrics.commits_by_month = self._calculate_month_distribution(timestamps)

            # Calculate statistics
            if len(ts_array) > 1:
                date_range_seconds = ts_array[-1] - ts_array[0]
                date_range_days = date_range_seconds / 86400  # seconds in a day
                metrics.average_commits_per_day = metrics.total_commits / max(
                    date_range_days, 1
                )

            # Find busiest periods
            if metrics.commits_by_day:
                metrics.busiest_day = max(
                    metrics.commits_by_day.items(), key=lambda x: x[1]
                )[0]
            if metrics.commits_by_hour:
                metrics.busiest_hour = max(
                    metrics.commits_by_hour.items(), key=lambda x: x[1]
                )[0]

        # Analyze commit message quality
        metrics.commit_message_quality = self._analyze_commit_messages_optimized()

        return asdict(metrics)

    def _get_commit_timestamps_optimized(self) -> List[datetime]:
        """Get commit timestamps more efficiently"""
        output = self._run_git_command(["log", "--all", "--format=%at"])

        if not output:
            return []

        # Parse timestamps in batch
        timestamps = []
        for line in output.split("\n"):
            if line.strip():
                try:
                    timestamps.append(datetime.fromtimestamp(int(line)))
                except ValueError:
                    pass

        return sorted(timestamps)

    def _calculate_day_distribution(self, timestamps: List[datetime]) -> Dict[str, int]:
        """Calculate commit distribution by day of week using NumPy"""
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_counts = np.zeros(7, dtype=int)

        for ts in timestamps:
            day_counts[ts.weekday()] += 1

        return {days[i]: int(count) for i, count in enumerate(day_counts) if count > 0}

    def _calculate_hour_distribution(
        self, timestamps: List[datetime]
    ) -> Dict[int, int]:
        """Calculate commit distribution by hour using NumPy"""
        hour_counts = np.zeros(24, dtype=int)

        for ts in timestamps:
            hour_counts[ts.hour] += 1

        return {i: int(count) for i, count in enumerate(hour_counts) if count > 0}

    def _calculate_month_distribution(
        self, timestamps: List[datetime]
    ) -> Dict[str, int]:
        """Calculate commit distribution by month"""
        month_counts = defaultdict(int)

        for ts in timestamps:
            month_key = ts.strftime("%Y-%m")
            month_counts[month_key] += 1

        return dict(month_counts)

    def _analyze_commit_messages_optimized(self) -> Dict[str, Any]:
        """Analyze commit messages with optimizations"""
        output = self._run_git_command(
            ["log", "--all", "--format=%s", "--max-count=1000"]
        )  # Limit to recent 1000

        if not output:
            return {}

        messages = [msg.strip() for msg in output.split("\n") if msg.strip()]

        quality_metrics = {
            "average_length": 0,
            "has_conventional_commits": 0,
            "has_issue_references": 0,
            "has_emoji": 0,
            "too_short": 0,
            "too_long": 0,
            "quality_score": 0.0,
        }

        if not messages:
            return quality_metrics

        # Vectorized operations where possible
        lengths = np.array([len(msg) for msg in messages])
        quality_metrics["average_length"] = float(np.mean(lengths))

        # Compile patterns once
        conventional_pattern = re.compile(
            r"^(feat|fix|docs|style|refactor|test|chore)(\(.+?\))?:"
        )
        issue_pattern = re.compile(r"#\d+")
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]"
        )

        # Count patterns
        conventional_count = sum(
            1 for msg in messages if conventional_pattern.match(msg)
        )
        issue_count = sum(1 for msg in messages if issue_pattern.search(msg))
        emoji_count = sum(1 for msg in messages if emoji_pattern.search(msg))
        too_short_count = np.sum(lengths < 10)
        too_long_count = np.sum(lengths > 100)

        total = len(messages)
        quality_metrics["has_conventional_commits"] = round(
            (conventional_count / total) * 100, 2
        )
        quality_metrics["has_issue_references"] = round((issue_count / total) * 100, 2)
        quality_metrics["has_emoji"] = round((emoji_count / total) * 100, 2)
        quality_metrics["too_short"] = round((too_short_count / total) * 100, 2)
        quality_metrics["too_long"] = round((too_long_count / total) * 100, 2)

        # Calculate quality score using NumPy
        scores = np.array(
            [
                5.0,
                2.0 if quality_metrics["has_conventional_commits"] > 50 else 0,
                1.0 if quality_metrics["has_issue_references"] > 20 else 0,
                1.0 if quality_metrics["too_short"] < 10 else 0,
                1.0 if quality_metrics["too_long"] < 10 else 0,
            ]
        )

        quality_metrics["quality_score"] = min(float(np.sum(scores)), 10.0)

        return quality_metrics

    def _analyze_activity_trends_optimized(self) -> Dict[str, Any]:
        """Analyze activity trends with optimizations"""
        trends = {
            "commit_frequency_trend": "stable",
            "contributor_growth_trend": "stable",
            "recent_activity_score": 0.0,
            "project_health_indicators": {},
        }

        if not self._is_git_repository():
            return trends

        # Use optimized calculations
        commit_trend = self._analyze_commit_frequency_trend_optimized()
        trends["commit_frequency_trend"] = commit_trend

        trends["contributor_growth_trend"] = self._analyze_contributor_growth()
        trends["recent_activity_score"] = self._calculate_activity_score_optimized()

        # Project health indicators
        trends["project_health_indicators"] = {
            "has_recent_commits": self._has_recent_commits(30),
            "has_multiple_contributors": self._count_active_contributors(90) > 1,
            "has_regular_commits": commit_trend != "declining",
            "has_documentation": self._check_documentation_presence(),
            "has_tests": self._check_test_presence(),
        }

        return trends

    def _analyze_commit_frequency_trend_optimized(self) -> str:
        """Analyze commit frequency trend using NumPy"""
        # Get commits by month for the last 6 months
        six_months_ago = datetime.now() - timedelta(days=180)
        output = self._run_git_command(
            [
                "log",
                "--all",
                f'--since={six_months_ago.strftime("%Y-%m-%d")}',
                "--format=%at",
            ]
        )

        if not output:
            return "no_data"

        # Convert to timestamps
        timestamps = []
        for line in output.split("\n"):
            if line.strip():
                try:
                    timestamps.append(datetime.fromtimestamp(int(line)))
                except ValueError:
                    pass

        if len(timestamps) < 10:  # Need sufficient data
            return "insufficient_data"

        # Group by month
        monthly_commits = defaultdict(int)
        for ts in timestamps:
            month_key = ts.strftime("%Y-%m")
            monthly_commits[month_key] += 1

        # Sort by month and convert to array
        sorted_months = sorted(monthly_commits.items())
        values = np.array([count for _, count in sorted_months])

        if len(values) < 3:
            return "insufficient_data"

        # Calculate trend using linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        # Determine trend based on slope
        if slope > 0.5:
            return "increasing"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"

    def _calculate_activity_score_optimized(self) -> float:
        """Calculate activity score using NumPy"""
        scores = []

        # Recent commits
        recent_commits = self._count_commits_since(30)
        if recent_commits > 30:
            scores.append(3.0)
        elif recent_commits > 10:
            scores.append(2.0)
        elif recent_commits > 0:
            scores.append(1.0)
        else:
            scores.append(0.0)

        # Active contributors
        active_contributors = self._count_active_contributors(30)
        if active_contributors > 5:
            scores.append(3.0)
        elif active_contributors > 2:
            scores.append(2.0)
        elif active_contributors > 0:
            scores.append(1.0)
        else:
            scores.append(0.0)

        # Commit regularity
        days_with_commits = self._count_days_with_commits(30)
        if days_with_commits > 20:
            scores.append(4.0)
        elif days_with_commits > 10:
            scores.append(3.0)
        elif days_with_commits > 5:
            scores.append(2.0)
        elif days_with_commits > 0:
            scores.append(1.0)
        else:
            scores.append(0.0)

        # Use NumPy for calculation
        return min(float(np.sum(scores)), 10.0)

    def _collect_contributor_metrics(self) -> Dict[str, Any]:
        """Collect contributor activity metrics"""
        # Keep the original implementation for now
        metrics = ContributorMetrics(
            total_contributors=0,
            active_contributors_30d=0,
            active_contributors_90d=0,
            contributor_stats=[],
            commit_distribution={},
            collaboration_score=0.0,
        )

        if not self._is_git_repository():
            logger.warning("Not a git repository, skipping contributor metrics")
            return asdict(metrics)

        # Basic implementation
        contributors = self._get_all_contributors()
        metrics.total_contributors = len(contributors)
        metrics.active_contributors_30d = self._count_active_contributors(30)
        metrics.active_contributors_90d = self._count_active_contributors(90)
        metrics.contributor_stats = self._get_contributor_stats()
        metrics.commit_distribution = self._analyze_commit_distribution()
        metrics.collaboration_score = self._calculate_collaboration_score(metrics)

        return asdict(metrics)

    def _collect_cloc_metrics(self) -> CodeMetrics:
        """Use cloc tool to collect metrics"""
        try:
            result = subprocess.run(
                ["cloc", "--json", "--quiet", str(self.repo_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            data = json.loads(result.stdout)

            # Extract overall metrics
            total = data.get("SUM", {})
            metrics = CodeMetrics(
                total_lines=total.get("code", 0)
                + total.get("comment", 0)
                + total.get("blank", 0),
                code_lines=total.get("code", 0),
                comment_lines=total.get("comment", 0),
                blank_lines=total.get("blank", 0),
                language_breakdown={},
                file_count_by_language={},
            )

            # Extract per-language metrics
            for lang, stats in data.items():
                if lang not in ["header", "SUM"]:
                    metrics.language_breakdown[lang] = {
                        "files": stats.get("nFiles", 0),
                        "code": stats.get("code", 0),
                        "comment": stats.get("comment", 0),
                        "blank": stats.get("blank", 0),
                    }
                    metrics.file_count_by_language[lang] = stats.get("nFiles", 0)

            return metrics

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to use cloc: {e}")
            return self._collect_custom_metrics_optimized()

    # Keep original helper methods unchanged
    def _is_git_repository(self) -> bool:
        """Check if directory is a git repository"""
        return (self.repo_path / ".git").exists()

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        try:
            subprocess.run(["which", command], capture_output=True, check=True)
            return True
        except subprocess.SubprocessError:
            return False

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

    def _get_all_contributors(self) -> List[str]:
        """Get list of all contributors"""
        output = self._run_git_command(["log", "--all", "--format=%ae"])
        return list(set(email.strip() for email in output.split("\n") if email.strip()))

    def _count_active_contributors(self, days: int) -> int:
        """Count contributors active in the last N days"""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        output = self._run_git_command(
            ["log", "--all", f"--since={since_date}", "--format=%ae"]
        )
        return len(set(email.strip() for email in output.split("\n") if email.strip()))

    def _get_contributor_stats(self) -> List[Dict[str, Any]]:
        """Get detailed contributor statistics"""
        output = self._run_git_command(["shortlog", "-sne", "--all"])
        stats = []

        for line in output.split("\n"):
            if line.strip():
                match = re.match(r"\s*(\d+)\s+(.+?)\s+<(.+?)>", line)
                if match:
                    commits, name, email = match.groups()
                    stats.append(
                        {
                            "name": name,
                            "email": email,
                            "commits": int(commits),
                            "percentage": 0,  # Will be calculated later
                        }
                    )

        # Calculate percentages
        total_commits = sum(s["commits"] for s in stats)
        for stat in stats:
            stat["percentage"] = (
                round((stat["commits"] / total_commits) * 100, 2)
                if total_commits > 0
                else 0
            )

        return sorted(stats, key=lambda x: x["commits"], reverse=True)[:20]  # Top 20

    def _analyze_commit_distribution(self) -> Dict[str, int]:
        """Analyze how commits are distributed among contributors"""
        stats = self._get_contributor_stats()
        distribution = {
            "top_1_percent": 0,
            "top_5_percent": 0,
            "top_10_percent": 0,
            "top_25_percent": 0,
            "bottom_50_percent": 0,
        }

        if not stats:
            return distribution

        total_commits = sum(s["commits"] for s in stats)
        cumulative = 0

        for i, stat in enumerate(stats):
            cumulative += stat["commits"]
            percentage_of_contributors = ((i + 1) / len(stats)) * 100
            percentage_of_commits = (cumulative / total_commits) * 100

            if percentage_of_contributors <= 1:
                distribution["top_1_percent"] = round(percentage_of_commits, 2)
            if percentage_of_contributors <= 5:
                distribution["top_5_percent"] = round(percentage_of_commits, 2)
            if percentage_of_contributors <= 10:
                distribution["top_10_percent"] = round(percentage_of_commits, 2)
            if percentage_of_contributors <= 25:
                distribution["top_25_percent"] = round(percentage_of_commits, 2)
            if percentage_of_contributors >= 50:
                distribution["bottom_50_percent"] = round(
                    100 - percentage_of_commits, 2
                )
                break

        return distribution

    def _calculate_collaboration_score(self, metrics: ContributorMetrics) -> float:
        """Calculate a collaboration score based on contributor metrics"""
        scores = []

        # Factor in number of contributors
        if metrics.total_contributors > 1:
            scores.append(min(metrics.total_contributors / 10, 3.0))  # Max 3 points

        # Factor in active contributors
        if metrics.active_contributors_30d > 1:
            scores.append(min(metrics.active_contributors_30d / 5, 2.0))  # Max 2 points

        # Factor in commit distribution (lower concentration is better)
        if metrics.commit_distribution:
            concentration = metrics.commit_distribution.get("top_10_percent", 100)
            if concentration < 50:
                scores.append(3.0)
            elif concentration < 70:
                scores.append(2.0)
            elif concentration < 90:
                scores.append(1.0)

        # Factor in recent activity
        if metrics.active_contributors_30d > 0:
            scores.append(2.0)

        return min(float(np.sum(scores)), 10.0) if scores else 0.0

    def _count_total_commits(self) -> int:
        """Count total commits in repository"""
        output = self._run_git_command(["rev-list", "--all", "--count"])
        return int(output) if output.isdigit() else 0

    def _has_recent_commits(self, days: int) -> bool:
        """Check if repository has commits in the last N days"""
        return self._count_commits_since(days) > 0

    def _count_commits_since(self, days: int) -> int:
        """Count commits since N days ago"""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        output = self._run_git_command(
            ["rev-list", "--all", f"--since={since_date}", "--count"]
        )
        return int(output) if output.isdigit() else 0

    def _count_days_with_commits(self, days: int) -> int:
        """Count number of days with at least one commit in the last N days"""
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        output = self._run_git_command(
            ["log", "--all", f"--since={since_date}", "--format=%ad", "--date=short"]
        )

        unique_days = set(line.strip() for line in output.split("\n") if line.strip())
        return len(unique_days)

    def _check_documentation_presence(self) -> bool:
        """Check if repository has documentation"""
        doc_indicators = [
            "README.md",
            "README.rst",
            "README.txt",
            "docs/",
            "documentation/",
        ]
        for indicator in doc_indicators:
            if (self.repo_path / indicator).exists():
                return True
        return False

    def _check_test_presence(self) -> bool:
        """Check if repository has tests"""
        test_indicators = [
            "tests/",
            "test/",
            "__tests__/",
            "spec/",
            "test.py",
            "test_*.py",
        ]
        for indicator in test_indicators:
            if "*" in indicator:
                if list(self.repo_path.glob(indicator)):
                    return True
            elif (self.repo_path / indicator).exists():
                return True
        return False

    def _analyze_contributor_growth(self) -> str:
        """Analyze contributor growth trend"""
        # Simplified implementation
        return "stable"


def main():
    """CLI interface for optimized metrics collector"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect repository metrics with optimizations"
    )
    parser.add_argument("path", help="Repository path to analyze")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path",
        default="metrics_report_optimized.json",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    collector = OptimizedMetricsCollector(args.path)
    results = collector.collect()

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Optimized metrics collection complete. Results saved to: {args.output}")


if __name__ == "__main__":
    main()
