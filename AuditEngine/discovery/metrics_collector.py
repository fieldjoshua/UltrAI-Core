"""
Metrics Collector Module

This module collects various code metrics including line counts,
contributor statistics, and commit patterns.
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


class MetricsCollector:
    """
    Collects comprehensive metrics about repository code, contributors, and commits
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def collect(self) -> Dict[str, Any]:
        """
        Collect all metrics

        Returns:
            Dictionary containing all collected metrics
        """
        logger.info(f"Starting metrics collection: {self.repo_path}")

        results = {
            "collection_timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "code_metrics": self._collect_code_metrics(),
            "contributor_metrics": self._collect_contributor_metrics(),
            "commit_metrics": self._collect_commit_metrics(),
            "activity_trends": self._analyze_activity_trends(),
        }

        logger.info("Metrics collection completed")
        return results

    def _collect_code_metrics(self) -> Dict[str, Any]:
        """Collect code line counts and language statistics"""
        metrics = CodeMetrics(
            total_lines=0,
            code_lines=0,
            comment_lines=0,
            blank_lines=0,
            language_breakdown={},
            file_count_by_language={},
        )

        # Try to use cloc (Count Lines of Code) if available
        if self._command_exists("cloc"):
            metrics = self._collect_cloc_metrics()
        else:
            # Fallback to custom implementation
            metrics = self._collect_custom_metrics()

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
            return self._collect_custom_metrics()

    def _collect_custom_metrics(self) -> CodeMetrics:
        """Custom implementation for collecting code metrics"""
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

        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".") for part in file_path.parts
            ):
                ext = file_path.suffix.lower()
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    metrics.file_count_by_language[lang] += 1

                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            for line in f:
                                metrics.total_lines += 1
                                line = line.strip()

                                if not line:
                                    metrics.blank_lines += 1
                                    metrics.language_breakdown[lang]["blank"] += 1
                                elif self._is_comment(line, ext):
                                    metrics.comment_lines += 1
                                    metrics.language_breakdown[lang]["comment"] += 1
                                else:
                                    metrics.code_lines += 1
                                    metrics.language_breakdown[lang]["code"] += 1

                            metrics.language_breakdown[lang]["files"] += 1

                    except Exception as e:
                        logger.debug(f"Error reading file {file_path}: {e}")

        # Convert defaultdict to regular dict
        metrics.language_breakdown = dict(metrics.language_breakdown)
        metrics.file_count_by_language = dict(metrics.file_count_by_language)

        return metrics

    def _is_comment(self, line: str, extension: str) -> bool:
        """Simple heuristic to detect comment lines"""
        comment_patterns = {
            ".py": ["#"],
            ".js": ["//", "/*", "*/"],
            ".ts": ["//", "/*", "*/"],
            ".java": ["//", "/*", "*/"],
            ".cpp": ["//", "/*", "*/"],
            ".c": ["//", "/*", "*/"],
            ".go": ["//", "/*", "*/"],
            ".rs": ["//", "/*", "*/"],
            ".rb": ["#"],
            ".php": ["//", "/*", "*/", "#"],
            ".cs": ["//", "/*", "*/"],
            ".swift": ["//", "/*", "*/"],
            ".kt": ["//", "/*", "*/"],
            ".scala": ["//", "/*", "*/"],
            ".r": ["#"],
        }

        patterns = comment_patterns.get(extension, [])
        return any(line.startswith(pattern) for pattern in patterns)

    def _collect_contributor_metrics(self) -> Dict[str, Any]:
        """Collect contributor activity metrics"""
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

        # Get all contributors
        contributors = self._get_all_contributors()
        metrics.total_contributors = len(contributors)

        # Get active contributors
        metrics.active_contributors_30d = self._count_active_contributors(30)
        metrics.active_contributors_90d = self._count_active_contributors(90)

        # Get detailed contributor stats
        metrics.contributor_stats = self._get_contributor_stats()

        # Analyze commit distribution
        metrics.commit_distribution = self._analyze_commit_distribution()

        # Calculate collaboration score
        metrics.collaboration_score = self._calculate_collaboration_score(metrics)

        return asdict(metrics)

    def _collect_commit_metrics(self) -> Dict[str, Any]:
        """Collect commit pattern metrics"""
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

        # Analyze commit patterns
        commits_data = self._get_commit_timestamps()

        # Group by day of week
        day_counts = defaultdict(int)
        hour_counts = defaultdict(int)
        month_counts = defaultdict(int)

        for timestamp in commits_data:
            day_counts[timestamp.strftime("%A")] += 1
            hour_counts[timestamp.hour] += 1
            month_counts[timestamp.strftime("%Y-%m")] += 1

        metrics.commits_by_day = dict(day_counts)
        metrics.commits_by_hour = dict(hour_counts)
        metrics.commits_by_month = dict(month_counts)

        # Calculate averages
        if commits_data:
            date_range = (commits_data[-1] - commits_data[0]).days + 1
            metrics.average_commits_per_day = (
                metrics.total_commits / date_range if date_range > 0 else 0
            )

            # Find busiest periods
            if day_counts:
                metrics.busiest_day = max(day_counts.items(), key=lambda x: x[1])[0]
            if hour_counts:
                metrics.busiest_hour = max(hour_counts.items(), key=lambda x: x[1])[0]

        # Analyze commit message quality
        metrics.commit_message_quality = self._analyze_commit_messages()

        return asdict(metrics)

    def _analyze_activity_trends(self) -> Dict[str, Any]:
        """Analyze repository activity trends"""
        trends = {
            "commit_frequency_trend": "stable",
            "contributor_growth_trend": "stable",
            "recent_activity_score": 0.0,
            "project_health_indicators": {},
        }

        if not self._is_git_repository():
            return trends

        # Analyze commit frequency trends
        commit_trend = self._analyze_commit_frequency_trend()
        trends["commit_frequency_trend"] = commit_trend

        # Analyze contributor growth
        contributor_trend = self._analyze_contributor_growth()
        trends["contributor_growth_trend"] = contributor_trend

        # Calculate recent activity score
        trends["recent_activity_score"] = self._calculate_activity_score()

        # Project health indicators
        trends["project_health_indicators"] = {
            "has_recent_commits": self._has_recent_commits(30),
            "has_multiple_contributors": self._count_active_contributors(90) > 1,
            "has_regular_commits": commit_trend != "declining",
            "has_documentation": self._check_documentation_presence(),
            "has_tests": self._check_test_presence(),
        }

        return trends

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
        score = 0.0

        # Factor in number of contributors
        if metrics.total_contributors > 1:
            score += min(metrics.total_contributors / 10, 3.0)  # Max 3 points

        # Factor in active contributors
        if metrics.active_contributors_30d > 1:
            score += min(metrics.active_contributors_30d / 5, 2.0)  # Max 2 points

        # Factor in commit distribution (lower concentration is better)
        if metrics.commit_distribution:
            concentration = metrics.commit_distribution.get("top_10_percent", 100)
            if concentration < 50:
                score += 3.0
            elif concentration < 70:
                score += 2.0
            elif concentration < 90:
                score += 1.0

        # Factor in recent activity
        if metrics.active_contributors_30d > 0:
            score += 2.0

        return min(round(score, 2), 10.0)  # Max score of 10

    def _count_total_commits(self) -> int:
        """Count total commits in repository"""
        output = self._run_git_command(["rev-list", "--all", "--count"])
        return int(output) if output.isdigit() else 0

    def _get_commit_timestamps(self) -> List[datetime]:
        """Get all commit timestamps"""
        output = self._run_git_command(["log", "--all", "--format=%at"])
        timestamps = []

        for line in output.split("\n"):
            if line.strip():
                try:
                    timestamp = datetime.fromtimestamp(int(line))
                    timestamps.append(timestamp)
                except ValueError:
                    pass

        return sorted(timestamps)

    def _analyze_commit_messages(self) -> Dict[str, Any]:
        """Analyze commit message quality"""
        output = self._run_git_command(["log", "--all", "--format=%s"])
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

        total_length = 0
        conventional_pattern = re.compile(
            r"^(feat|fix|docs|style|refactor|test|chore)(\(.+?\))?:"
        )
        issue_pattern = re.compile(r"#\d+")
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]"
        )

        for msg in messages:
            total_length += len(msg)

            if conventional_pattern.match(msg):
                quality_metrics["has_conventional_commits"] += 1
            if issue_pattern.search(msg):
                quality_metrics["has_issue_references"] += 1
            if emoji_pattern.search(msg):
                quality_metrics["has_emoji"] += 1
            if len(msg) < 10:
                quality_metrics["too_short"] += 1
            if len(msg) > 100:
                quality_metrics["too_long"] += 1

        quality_metrics["average_length"] = round(total_length / len(messages), 2)

        # Calculate percentages
        for key in [
            "has_conventional_commits",
            "has_issue_references",
            "has_emoji",
            "too_short",
            "too_long",
        ]:
            quality_metrics[key] = round(
                (quality_metrics[key] / len(messages)) * 100, 2
            )

        # Calculate quality score
        score = 5.0
        if quality_metrics["has_conventional_commits"] > 50:
            score += 2.0
        if quality_metrics["has_issue_references"] > 20:
            score += 1.0
        if quality_metrics["too_short"] < 10:
            score += 1.0
        if quality_metrics["too_long"] < 10:
            score += 1.0

        quality_metrics["quality_score"] = min(round(score, 2), 10.0)

        return quality_metrics

    def _analyze_commit_frequency_trend(self) -> str:
        """Analyze commit frequency trend (increasing, stable, declining)"""
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

        # Group by month
        monthly_commits = defaultdict(int)
        for line in output.split("\n"):
            if line.strip():
                try:
                    timestamp = datetime.fromtimestamp(int(line))
                    month_key = timestamp.strftime("%Y-%m")
                    monthly_commits[month_key] += 1
                except ValueError:
                    pass

        # Sort by month
        sorted_months = sorted(monthly_commits.items())

        if len(sorted_months) < 3:
            return "insufficient_data"

        # Calculate trend
        values = [count for _, count in sorted_months]
        first_half_avg = sum(values[: len(values) // 2]) / (len(values) // 2)
        second_half_avg = sum(values[len(values) // 2 :]) / (
            len(values) - len(values) // 2
        )

        if second_half_avg > first_half_avg * 1.2:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.8:
            return "declining"
        else:
            return "stable"

    def _analyze_contributor_growth(self) -> str:
        """Analyze contributor growth trend"""
        # Similar logic to commit frequency but for new contributors
        return "stable"  # Simplified implementation

    def _calculate_activity_score(self) -> float:
        """Calculate recent activity score (0-10)"""
        score = 0.0

        # Recent commits
        recent_commits = self._count_commits_since(30)
        if recent_commits > 30:
            score += 3.0
        elif recent_commits > 10:
            score += 2.0
        elif recent_commits > 0:
            score += 1.0

        # Active contributors
        active_contributors = self._count_active_contributors(30)
        if active_contributors > 5:
            score += 3.0
        elif active_contributors > 2:
            score += 2.0
        elif active_contributors > 0:
            score += 1.0

        # Commit regularity
        days_with_commits = self._count_days_with_commits(30)
        if days_with_commits > 20:
            score += 4.0
        elif days_with_commits > 10:
            score += 3.0
        elif days_with_commits > 5:
            score += 2.0
        elif days_with_commits > 0:
            score += 1.0

        return min(round(score, 2), 10.0)

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


def main():
    """CLI interface for metrics collector"""
    import argparse

    parser = argparse.ArgumentParser(description="Collect repository metrics")
    parser.add_argument("path", help="Repository path to analyze")
    parser.add_argument(
        "--output", "-o", help="Output file path", default="metrics_report.json"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    collector = MetricsCollector(args.path)
    results = collector.collect()

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Metrics collection complete. Results saved to: {args.output}")


if __name__ == "__main__":
    main()
