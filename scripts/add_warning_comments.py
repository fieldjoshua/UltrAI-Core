#!/usr/bin/env python3
"""
Script to add standard warning comments to route files.
"""

import re
from pathlib import Path

# Standard warning comment to add
WARNING_COMMENT = """
    WARNING: This endpoint is for development/testing only. Do not use in production.
"""


def add_warning_to_file(file_path: str) -> None:
    """Add warning comment to route functions in a file."""
    with open(file_path, "r") as f:
        content = f.read()

    # Pattern to match route function docstrings
    pattern = r'@\w+\.(get|post|put|delete|patch)\([^)]*\)\s*async def \w+\([^)]*\):\s*"""(.*?)"""'

    def replace_docstring(match):
        decorator = match.group(0).split('"""')[0]
        existing_doc = match.group(1).strip()

        # Skip if warning already exists
        if "WARNING:" in existing_doc:
            return match.group(0)

        # Add warning to docstring
        new_doc = f'"""\n    {existing_doc}\n    {WARNING_COMMENT.strip()}\n    """'
        return decorator + new_doc

    # Replace docstrings with warnings
    new_content = re.sub(pattern, replace_docstring, content, flags=re.DOTALL)

    # Write back to file if changes were made
    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Added warnings to {file_path}")


def main():
    """Main function to process all route files."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    # Path to routes directory
    routes_dir = project_root / "app" / "routes"

    # Process all Python files in routes directory
    for file_path in routes_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            add_warning_to_file(str(file_path))


if __name__ == "__main__":
    main()
