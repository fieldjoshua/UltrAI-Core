#!/usr/bin/env python3
"""
Script to automatically fix imports in the Ultra backend codebase by adding 'backend.' prefix.
No external dependencies required.
"""

import os
import re
import sys

# Modules that need to be prefixed with 'backend.'
MODULES = [
    "config",
    "database",
    "models",
    "routes",
    "services",
    "utils",
    "middleware",
    "decorators",
    "repositories",
]


def fix_imports_in_file(file_path):
    """Fix imports in a single file by adding 'backend.' prefix."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        new_content = content
        replacements = 0

        # Fix 'from module import ...' patterns
        for module in MODULES:
            pattern = re.compile(rf"from\s+{module}([\.\w]+)?\s+import", re.MULTILINE)

            def replace_match(match):
                nonlocal replacements
                original = match.group(0)
                # Only replace if not already prefixed with 'backend.'
                if not re.search(rf"from\s+backend\.{module}", original):
                    replacements += 1
                    suffix = match.group(1) or ""
                    return f"from backend.{module}{suffix} import"
                return original

            new_content = pattern.sub(replace_match, new_content)

        # Fix 'import module' patterns
        for module in MODULES:
            pattern = re.compile(rf"import\s+{module}([\.\w]+)?(?!\s+as)", re.MULTILINE)

            def replace_match(match):
                nonlocal replacements
                original = match.group(0)
                # Only replace if not already prefixed with 'backend.'
                if not re.search(rf"import\s+backend\.{module}", original):
                    replacements += 1
                    suffix = match.group(1) or ""
                    return f"import backend.{module}{suffix}"
                return original

            new_content = pattern.sub(replace_match, new_content)

        # Write changes back to file if any replacements were made
        if replacements > 0:
            with open(file_path, "w") as f:
                f.write(new_content)
            return replacements

        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    # Directory to process
    backend_dir = os.path.join(os.getcwd(), "backend")

    if not os.path.exists(backend_dir):
        print(f"Error: Directory '{backend_dir}' not found.")
        sys.exit(1)

    # Find all Python files in the backend directory
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    print(f"Found {len(python_files)} Python files in the backend directory")

    # Process each file
    total_replacements = 0
    files_modified = 0

    for file_path in python_files:
        replacements = fix_imports_in_file(file_path)
        if replacements > 0:
            rel_path = os.path.relpath(file_path, os.getcwd())
            print(f"Fixed {replacements} imports in {rel_path}")
            total_replacements += replacements
            files_modified += 1

    print(
        f"Import fixing complete! Fixed {total_replacements} imports in {files_modified} files."
    )


if __name__ == "__main__":
    main()
