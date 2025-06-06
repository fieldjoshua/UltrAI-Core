#!/usr/bin/env python
"""
Script to fix imports in the Ultra backend.

This script changes imports without the 'backend.' prefix to include it:
- from database.X to from backend.database.X
- from utils.X to from backend.utils.X
"""

import os
import re
import sys
from pathlib import Path

# Regular expressions to match the patterns we want to replace - multiline mode
DB_PATTERN = re.compile(r"^from\s+database(\s+|\.)(?!backend\.)", re.MULTILINE)
UTILS_PATTERN = re.compile(r"^from\s+utils(\s+|\.)(?!backend\.)", re.MULTILINE)
IMPORT_DB_PATTERN = re.compile(r"^import\s+database(?!\.backend)", re.MULTILINE)
IMPORT_UTILS_PATTERN = re.compile(r"^import\s+utils(?!\.backend)", re.MULTILINE)


def fix_imports_in_file(file_path):
    """
    Fix imports in a single file.

    Args:
        file_path: Path to the file to fix.

    Returns:
        True if changes were made, False otherwise.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Replace database imports
    new_content = DB_PATTERN.sub(
        lambda m: m.group(0).replace("database", "backend.database"), content
    )
    new_content = IMPORT_DB_PATTERN.sub("import backend.database", new_content)

    # Replace utils imports
    new_content = UTILS_PATTERN.sub(
        lambda m: m.group(0).replace("utils", "backend.utils"), new_content
    )
    new_content = IMPORT_UTILS_PATTERN.sub("import backend.utils", new_content)

    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        return True

    return False


def find_files_with_incorrect_imports(root_dir):
    """
    Find all Python files under the given root directory that contain incorrect imports.

    Args:
        root_dir: Root directory to start searching from.

    Returns:
        List of file paths with incorrect imports.
    """
    files_with_incorrect_imports = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()

                # Check if the file has any of the patterns we're looking for
                if (
                    DB_PATTERN.search(content)
                    or UTILS_PATTERN.search(content)
                    or IMPORT_DB_PATTERN.search(content)
                    or IMPORT_UTILS_PATTERN.search(content)
                ):
                    files_with_incorrect_imports.append(file_path)

    return files_with_incorrect_imports


def fix_all_imports(root_dir):
    """
    Fix imports in all Python files under the given root directory.

    Args:
        root_dir: Root directory to start searching from.

    Returns:
        Dictionary with information about files fixed.
    """
    files_to_fix = find_files_with_incorrect_imports(root_dir)
    fixed_files = []

    for file_path in files_to_fix:
        if fix_imports_in_file(file_path):
            fixed_files.append(file_path)

    return {
        "total_files_scanned": sum(1 for _ in Path(root_dir).glob("**/*.py")),
        "files_with_incorrect_imports": len(files_to_fix),
        "files_fixed": len(fixed_files),
        "fixed_files": fixed_files,
    }


if __name__ == "__main__":
    root_dir = "."
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]

    result = fix_all_imports(root_dir)

    print(f"Total Python files scanned: {result['total_files_scanned']}")
    print(f"Files with incorrect imports: {result['files_with_incorrect_imports']}")
    print(f"Files fixed: {result['files_fixed']}")

    if result["files_fixed"] > 0:
        print("\nFixed files:")
        for file in result["fixed_files"]:
            print(f"  - {file}")
    else:
        print("\nNo files needed fixing.")
