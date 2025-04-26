import pytest
import os
import re
from pathlib import Path


def test_api_documentation():
    # Test API documentation
    api_docs_path = Path(
        ".aicheck/actions/PROTOTYPE_IMPLEMENTATION/supporting_docs/api_documentation.md"
    )
    assert api_docs_path.exists()

    with open(api_docs_path, "r") as f:
        content = f.read()

        # Verify required sections
        assert "## Overview" in content
        assert "## Base URL" in content
        assert "## Authentication" in content
        assert "## Endpoints" in content
        assert "## Error Responses" in content

        # Verify endpoint documentation
        assert "### Register User" in content
        assert "### Login" in content
        assert "### Get Current User" in content

        # Verify request/response examples
        assert "Request Body:" in content
        assert "Response:" in content

        # Verify error codes
        assert "INVALID_CREDENTIALS" in content
        assert "USER_NOT_FOUND" in content
        assert "EMAIL_ALREADY_EXISTS" in content


def test_setup_instructions():
    # Test setup instructions
    setup_path = Path(
        ".aicheck/actions/PROTOTYPE_IMPLEMENTATION/supporting_docs/setup_instructions.md"
    )
    assert setup_path.exists()

    with open(setup_path, "r") as f:
        content = f.read()

        # Verify required sections
        assert "## Prerequisites" in content
        assert "## Installation Steps" in content
        assert "## Configuration" in content
        assert "## Testing" in content

        # Verify installation steps
        assert "python -m venv .venv" in content
        assert "pip install -r requirements.txt" in content
        assert "uvicorn main:app --reload" in content

        # Verify configuration steps
        assert "cp .env.example .env" in content
        assert "Update the `.env` file" in content


def test_development_guide():
    # Test development guide
    dev_guide_path = Path(
        ".aicheck/actions/PROTOTYPE_IMPLEMENTATION/supporting_docs/development_guide.md"
    )
    assert dev_guide_path.exists()

    with open(dev_guide_path, "r") as f:
        content = f.read()

        # Verify required sections
        assert "## Project Structure" in content
        assert "## Coding Standards" in content
        assert "## Development Workflow" in content
        assert "## Best Practices" in content

        # Verify coding standards
        assert "PEP 8" in content
        assert "type hints" in content
        assert "docstrings" in content

        # Verify workflow steps
        assert "Create a new branch" in content
        assert "Write tests" in content
        assert "Create pull request" in content


def test_configuration_options():
    # Test configuration options
    config_path = Path(
        ".aicheck/actions/PROTOTYPE_IMPLEMENTATION/supporting_docs/configuration_options.md"
    )
    assert config_path.exists()

    with open(config_path, "r") as f:
        content = f.read()

        # Verify required sections
        assert "## Environment Variables" in content
        assert "## API Configuration" in content
        assert "## Security Settings" in content
        assert "## Monitoring Configuration" in content

        # Verify environment variables
        assert "API_KEY" in content
        assert "DATABASE_URL" in content
        assert "LOG_LEVEL" in content

        # Verify security settings
        assert "rate_limit" in content
        assert "max_tokens" in content
        assert "timeout" in content


def test_documentation_links():
    # Test documentation links
    docs_dir = Path(".aicheck/actions/PROTOTYPE_IMPLEMENTATION/supporting_docs")
    assert docs_dir.exists()

    # Get all markdown files
    md_files = list(docs_dir.glob("*.md"))
    assert len(md_files) > 0

    # Check for broken links
    for file in md_files:
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


def test_code_examples():
    # Test code examples
    docs_dir = Path(".aicheck/actions/PROTOTYPE_IMPLEMENTATION/supporting_docs")

    for file in docs_dir.glob("*.md"):
        with open(file, "r") as f:
            content = f.read()

            # Find code blocks
            code_blocks = re.findall(r"```(\w+)?\n(.*?)\n```", content, re.DOTALL)

            for language, code in code_blocks:
                # Verify code blocks have language specified
                assert language, f"Code block without language in {file}"

                # Verify code blocks are not empty
                assert code.strip(), f"Empty code block in {file}"

                # Verify code blocks are properly formatted
                assert not code.startswith(
                    " "
                ), f"Code block with leading spaces in {file}"
                assert not code.endswith(
                    " "
                ), f"Code block with trailing spaces in {file}"
