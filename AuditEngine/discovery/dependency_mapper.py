"""
Dependency Mapper Module

This module analyzes project dependencies, creates dependency trees,
and identifies outdated or vulnerable packages.
"""

import json
import logging
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from packaging import version

logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """Represents a single dependency"""

    name: str
    current_version: str
    latest_version: Optional[str]
    is_outdated: bool
    is_vulnerable: bool
    vulnerability_details: List[Dict[str, Any]]
    dependencies: List["Dependency"]
    dev_dependency: bool = False


@dataclass
class DependencyReport:
    """Complete dependency analysis report"""

    total_dependencies: int
    total_dev_dependencies: int
    outdated_count: int
    vulnerable_count: int
    dependency_tree: Dict[str, Any]
    vulnerabilities: List[Dict[str, Any]]
    update_recommendations: List[Dict[str, Any]]


class DependencyMapper:
    """
    Maps and analyzes project dependencies for various package managers
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.dependencies = {}
        self.vulnerability_db = {}

    def analyze(self) -> Dict[str, Any]:
        """
        Perform complete dependency analysis

        Returns:
            Dictionary containing dependency analysis results
        """
        logger.info(f"Starting dependency analysis: {self.repo_path}")

        results = {
            "python": self._analyze_python_dependencies(),
            "javascript": self._analyze_javascript_dependencies(),
            "summary": self._create_summary(),
        }

        logger.info("Dependency analysis completed")
        return results

    def _analyze_python_dependencies(self) -> Dict[str, Any]:
        """Analyze Python dependencies"""
        results = {
            "found": False,
            "package_manager": None,
            "dependencies": {},
            "vulnerabilities": [],
        }

        # Check for various Python dependency files
        if (self.repo_path / "requirements.txt").exists():
            results["found"] = True
            results["package_manager"] = "pip"
            results["dependencies"] = self._parse_requirements_txt()

        elif (self.repo_path / "Pipfile").exists():
            results["found"] = True
            results["package_manager"] = "pipenv"
            results["dependencies"] = self._parse_pipfile()

        elif (self.repo_path / "pyproject.toml").exists():
            results["found"] = True
            results["package_manager"] = "poetry/setuptools"
            results["dependencies"] = self._parse_pyproject_toml()

        elif (self.repo_path / "setup.py").exists():
            results["found"] = True
            results["package_manager"] = "setuptools"
            results["dependencies"] = self._parse_setup_py()

        if results["found"]:
            # Check for vulnerabilities
            results["vulnerabilities"] = self._check_python_vulnerabilities(
                results["dependencies"]
            )

            # Check for outdated packages
            self._check_outdated_python_packages(results["dependencies"])

        return results

    def _analyze_javascript_dependencies(self) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript dependencies"""
        results = {
            "found": False,
            "package_manager": None,
            "dependencies": {},
            "vulnerabilities": [],
        }

        package_json_path = self.repo_path / "package.json"
        if package_json_path.exists():
            results["found"] = True
            results["package_manager"] = "npm/yarn"

            # Parse package.json
            with open(package_json_path, "r") as f:
                package_data = json.load(f)

            dependencies = {}

            # Regular dependencies
            if "dependencies" in package_data:
                for name, version_spec in package_data["dependencies"].items():
                    dependencies[name] = {
                        "current_version": version_spec,
                        "dev_dependency": False,
                    }

            # Dev dependencies
            if "devDependencies" in package_data:
                for name, version_spec in package_data["devDependencies"].items():
                    dependencies[name] = {
                        "current_version": version_spec,
                        "dev_dependency": True,
                    }

            results["dependencies"] = dependencies

            # Check for vulnerabilities using npm audit
            results["vulnerabilities"] = self._run_npm_audit()

            # Check for outdated packages
            self._check_outdated_npm_packages(results["dependencies"])

        return results

    def _parse_requirements_txt(self) -> Dict[str, Any]:
        """Parse requirements.txt file"""
        requirements_path = self.repo_path / "requirements.txt"
        dependencies = {}

        with open(requirements_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse requirement line
                    match = re.match(r"^([^>=<!\s]+)\s*([>=<!\s].*)?$", line)
                    if match:
                        package_name = match.group(1)
                        version_spec = match.group(2) or ""
                        dependencies[package_name] = {
                            "current_version": version_spec.strip(),
                            "dev_dependency": False,
                        }

        return dependencies

    def _parse_pipfile(self) -> Dict[str, Any]:
        """Parse Pipfile"""
        pipfile_path = self.repo_path / "Pipfile"
        dependencies = {}

        try:
            # Try to use pipenv directly
            result = subprocess.run(
                ["pipenv", "lock", "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lock_data = json.loads(result.stdout)

                # Regular dependencies
                for name, info in lock_data.get("default", {}).items():
                    dependencies[name] = {
                        "current_version": info.get("version", ""),
                        "dev_dependency": False,
                    }

                # Dev dependencies
                for name, info in lock_data.get("develop", {}).items():
                    dependencies[name] = {
                        "current_version": info.get("version", ""),
                        "dev_dependency": True,
                    }
        except (subprocess.SubprocessError, json.JSONDecodeError):
            # Fallback to parsing Pipfile directly
            pass

        return dependencies

    def _parse_pyproject_toml(self) -> Dict[str, Any]:
        """Parse pyproject.toml file"""
        pyproject_path = self.repo_path / "pyproject.toml"
        dependencies = {}

        try:
            import toml

            with open(pyproject_path, "r") as f:
                data = toml.load(f)

            # Poetry dependencies
            if "tool" in data and "poetry" in data["tool"]:
                poetry_deps = data["tool"]["poetry"].get("dependencies", {})
                for name, version_spec in poetry_deps.items():
                    if name != "python":  # Skip Python version specification
                        dependencies[name] = {
                            "current_version": str(version_spec),
                            "dev_dependency": False,
                        }

                # Dev dependencies
                dev_deps = data["tool"]["poetry"].get("dev-dependencies", {})
                for name, version_spec in dev_deps.items():
                    dependencies[name] = {
                        "current_version": str(version_spec),
                        "dev_dependency": True,
                    }

            # PEP 517 dependencies
            elif "project" in data:
                project_deps = data["project"].get("dependencies", [])
                for dep in project_deps:
                    match = re.match(r"^([^>=<!\s]+)\s*(.*)$", dep)
                    if match:
                        name = match.group(1)
                        version_spec = match.group(2) or ""
                        dependencies[name] = {
                            "current_version": version_spec,
                            "dev_dependency": False,
                        }
        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {e}")

        return dependencies

    def _parse_setup_py(self) -> Dict[str, Any]:
        """Parse setup.py file"""
        setup_path = self.repo_path / "setup.py"
        dependencies = {}

        try:
            # Read and parse setup.py to extract dependencies
            with open(setup_path, "r") as f:
                content = f.read()

            # Look for install_requires
            install_requires_match = re.search(
                r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL
            )

            if install_requires_match:
                requires_content = install_requires_match.group(1)
                # Extract individual requirements
                for req in re.findall(r'["\']([^"\']+)["\']', requires_content):
                    match = re.match(r"^([^>=<!\s]+)\s*(.*)$", req)
                    if match:
                        name = match.group(1)
                        version_spec = match.group(2) or ""
                        dependencies[name] = {
                            "current_version": version_spec,
                            "dev_dependency": False,
                        }
        except Exception as e:
            logger.error(f"Error parsing setup.py: {e}")

        return dependencies

    def _check_python_vulnerabilities(
        self, dependencies: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check Python packages for known vulnerabilities"""
        vulnerabilities = []

        # Use safety or pyup.io API to check for vulnerabilities
        # This is a simplified implementation
        for package_name, info in dependencies.items():
            # Check against a vulnerability database
            vuln_info = self._query_vulnerability_db(
                package_name, info["current_version"]
            )
            if vuln_info:
                vulnerabilities.append(
                    {
                        "package": package_name,
                        "current_version": info["current_version"],
                        "vulnerabilities": vuln_info,
                    }
                )

        return vulnerabilities

    def _check_outdated_python_packages(self, dependencies: Dict[str, Any]) -> None:
        """Check for outdated Python packages"""
        for package_name, info in dependencies.items():
            try:
                # Query PyPI for latest version
                response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data["info"]["version"]

                    # Compare versions
                    current = info["current_version"]
                    if current and not current.startswith((">=", ">", "~")):
                        # Clean version string
                        current_clean = re.sub(r"[^0-9.]", "", current)
                        if current_clean and version.parse(
                            current_clean
                        ) < version.parse(latest_version):
                            info["latest_version"] = latest_version
                            info["is_outdated"] = True
                        else:
                            info["is_outdated"] = False
                    else:
                        info["latest_version"] = latest_version
                        info["is_outdated"] = None  # Can't determine
            except Exception as e:
                logger.error(f"Error checking updates for {package_name}: {e}")
                info["is_outdated"] = None

    def _run_npm_audit(self) -> List[Dict[str, Any]]:
        """Run npm audit to check for vulnerabilities"""
        vulnerabilities = []

        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.stdout:
                audit_data = json.loads(result.stdout)
                if "vulnerabilities" in audit_data:
                    for name, vuln_info in audit_data["vulnerabilities"].items():
                        vulnerabilities.append(
                            {
                                "package": name,
                                "severity": vuln_info.get("severity"),
                                "vulnerabilities": vuln_info.get("via", []),
                            }
                        )
        except Exception as e:
            logger.error(f"Error running npm audit: {e}")

        return vulnerabilities

    def _check_outdated_npm_packages(self, dependencies: Dict[str, Any]) -> None:
        """Check for outdated npm packages"""
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.stdout:
                outdated_data = json.loads(result.stdout)
                for package_name, info in outdated_data.items():
                    if package_name in dependencies:
                        dependencies[package_name]["latest_version"] = info.get(
                            "latest"
                        )
                        dependencies[package_name]["is_outdated"] = True
        except Exception as e:
            logger.error(f"Error checking npm updates: {e}")

    def _query_vulnerability_db(
        self, package_name: str, version: str
    ) -> List[Dict[str, Any]]:
        """Query vulnerability database (placeholder implementation)"""
        # In a real implementation, this would query services like:
        # - Safety DB
        # - OSV (Open Source Vulnerabilities)
        # - Snyk vulnerability database
        # - GitHub Security Advisory Database

        # This is a placeholder that returns empty list
        return []

    def _create_summary(self) -> Dict[str, Any]:
        """Create summary of dependency analysis"""
        summary = {
            "total_dependencies": 0,
            "total_dev_dependencies": 0,
            "outdated_count": 0,
            "vulnerable_count": 0,
            "update_recommendations": [],
        }

        # Aggregate data from Python and JavaScript analyses
        # This is simplified - in real implementation would be more comprehensive

        return summary

    def generate_dependency_tree(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a visual dependency tree"""
        tree = {}

        for name, info in dependencies.items():
            tree[name] = {
                "version": info.get("current_version"),
                "latest": info.get("latest_version"),
                "dev": info.get("dev_dependency", False),
                "outdated": info.get("is_outdated", False),
                "vulnerable": len(info.get("vulnerabilities", [])) > 0,
            }

        return tree


def main():
    """CLI interface for dependency mapper"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze project dependencies")
    parser.add_argument("path", help="Repository path to analyze")
    parser.add_argument(
        "--output", "-o", help="Output file path", default="dependency_analysis.json"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    mapper = DependencyMapper(args.path)
    results = mapper.analyze()

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Analysis complete. Results saved to: {args.output}")


if __name__ == "__main__":
    main()
