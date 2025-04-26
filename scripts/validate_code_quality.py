#!/usr/bin/env python3
"""
UltraAI Code Quality Validator

This script validates code quality across the UltraAI project.
It ensures all code meets the project's quality standards.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class CodeQualityValidator:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.python_files = list(self.root_dir.rglob("*.py"))
        self.js_files = list(self.root_dir.rglob("*.js"))
        self.ts_files = list(self.root_dir.rglob("*.ts"))
        self.md_files = list(self.root_dir.rglob("*.md"))

    def run_black(self) -> bool:
        """Run Black code formatter."""
        try:
            subprocess.run(
                ["black", "--check", "."], check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print("Black check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def run_isort(self) -> bool:
        """Run isort import sorter."""
        try:
            subprocess.run(
                ["isort", "--check-only", "."],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print("isort check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def run_flake8(self) -> bool:
        """Run Flake8 linter."""
        try:
            subprocess.run(["flake8", "."], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print("Flake8 check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def run_mypy(self) -> bool:
        """Run MyPy type checker."""
        try:
            subprocess.run(["mypy", "."], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print("MyPy check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def run_pydocstyle(self) -> bool:
        """Run pydocstyle docstring checker."""
        try:
            subprocess.run(
                ["pydocstyle", "."], check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print("pydocstyle check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def run_prettier(self) -> bool:
        """Run Prettier formatter."""
        try:
            subprocess.run(
                ["prettier", "--check", "."], check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print("Prettier check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def run_eslint(self) -> bool:
        """Run ESLint linter."""
        try:
            subprocess.run(["eslint", "."], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print("ESLint check failed:")
            print(e.stdout)
            print(e.stderr)
            return False

    def validate_all(self) -> bool:
        """Run all code quality checks."""
        checks = [
            ("Black", self.run_black),
            ("isort", self.run_isort),
            ("Flake8", self.run_flake8),
            ("MyPy", self.run_mypy),
            ("pydocstyle", self.run_pydocstyle),
            ("Prettier", self.run_prettier),
            ("ESLint", self.run_eslint),
        ]

        all_passed = True
        for name, check in checks:
            print(f"\nRunning {name}...")
            if not check():
                all_passed = False
                print(f"{name} check failed!")
            else:
                print(f"{name} check passed!")

        return all_passed


def main():
    validator = CodeQualityValidator(os.getcwd())
    if not validator.validate_all():
        print("\nCode quality validation failed!")
        sys.exit(1)
    print("\nAll code quality checks passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
