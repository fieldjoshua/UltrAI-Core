import pytest
import os
import yaml
from pathlib import Path
import re


def test_documentation_structure():
    # Test documentation structure
    docs_dir = Path("docs")
    assert docs_dir.exists()

    # Verify main documentation files
    assert (docs_dir / "README.md").exists()
    assert (docs_dir / "CONTRIBUTING.md").exists()
    assert (docs_dir / "CHANGELOG.md").exists()
    assert (docs_dir / "LICENSE").exists()


def test_api_documentation():
    # Test API documentation
    api_dir = docs_dir / "api"
    assert api_dir.exists()

    # Verify API documentation files
    assert (api_dir / "overview.md").exists()
    assert (api_dir / "authentication.md").exists()
    assert (api_dir / "endpoints.md").exists()
    assert (api_dir / "errors.md").exists()

    # Test API documentation content
    with open(api_dir / "overview.md", "r") as f:
        content = f.read()
        assert "## Overview" in content
        assert "## Base URL" in content
        assert "## Authentication" in content


def test_development_documentation():
    # Test development documentation
    dev_dir = docs_dir / "development"
    assert dev_dir.exists()

    # Verify development documentation files
    assert (dev_dir / "setup.md").exists()
    assert (dev_dir / "testing.md").exists()
    assert (dev_dir / "deployment.md").exists()
    assert (dev_dir / "contributing.md").exists()

    # Test development documentation content
    with open(dev_dir / "setup.md", "r") as f:
        content = f.read()
        assert "## Prerequisites" in content
        assert "## Installation" in content
        assert "## Configuration" in content


def test_user_documentation():
    # Test user documentation
    user_dir = docs_dir / "user"
    assert user_dir.exists()

    # Verify user documentation files
    assert (user_dir / "getting-started.md").exists()
    assert (user_dir / "features.md").exists()
    assert (user_dir / "troubleshooting.md").exists()
    assert (user_dir / "faq.md").exists()

    # Test user documentation content
    with open(user_dir / "getting-started.md", "r") as f:
        content = f.read()
        assert "## Installation" in content
        assert "## Quick Start" in content
        assert "## Basic Usage" in content


def test_architecture_documentation():
    # Test architecture documentation
    arch_dir = docs_dir / "architecture"
    assert arch_dir.exists()

    # Verify architecture documentation files
    assert (arch_dir / "overview.md").exists()
    assert (arch_dir / "components.md").exists()
    assert (arch_dir / "data-flow.md").exists()
    assert (arch_dir / "security.md").exists()

    # Test architecture documentation content
    with open(arch_dir / "overview.md", "r") as f:
        content = f.read()
        assert "## System Architecture" in content
        assert "## Components" in content
        assert "## Data Flow" in content


def test_operations_documentation():
    # Test operations documentation
    ops_dir = docs_dir / "operations"
    assert ops_dir.exists()

    # Verify operations documentation files
    assert (ops_dir / "monitoring.md").exists()
    assert (ops_dir / "logging.md").exists()
    assert (ops_dir / "backup.md").exists()
    assert (ops_dir / "maintenance.md").exists()

    # Test operations documentation content
    with open(ops_dir / "monitoring.md", "r") as f:
        content = f.read()
        assert "## Monitoring Setup" in content
        assert "## Alerts" in content
        assert "## Dashboards" in content


def test_security_documentation():
    # Test security documentation
    security_dir = docs_dir / "security"
    assert security_dir.exists()

    # Verify security documentation files
    assert (security_dir / "overview.md").exists()
    assert (security_dir / "authentication.md").exists()
    assert (security_dir / "authorization.md").exists()
    assert (security_dir / "encryption.md").exists()

    # Test security documentation content
    with open(security_dir / "overview.md", "r") as f:
        content = f.read()
        assert "## Security Overview" in content
        assert "## Best Practices" in content
        assert "## Compliance" in content


def test_documentation_links():
    # Test documentation links
    for file in docs_dir.rglob("*.md"):
        with open(file, "r") as f:
            content = f.read()

            # Find all markdown links
            links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith("http"):
                    continue

                # Check internal links
                link_path = docs_dir / link_url
                assert link_path.exists(), f"Broken link in {file}: {link_url}"
