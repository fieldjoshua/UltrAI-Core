#!/usr/bin/env python3

import json
import os
import re
import shlex
import subprocess
import sys

# Configuration
documentation_dir = "documentation"
patterns_file = os.path.join(documentation_dir, "instructions", "PATTERNS.md")
core_readme = os.path.join(documentation_dir, "CORE_README.md")
contributing_file = os.path.join(documentation_dir, "guidelines", "CONTRIBUTING.md")
issues = []


def run_command(cmd):
    """Run a shell command and return its output in a more secure way"""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return (
        stdout.decode("utf-8").strip(),
        stderr.decode("utf-8").strip(),
        process.returncode,
    )


def get_changed_files():
    """Get list of files changed in the PR"""
    if "GITHUB_EVENT_PATH" in os.environ:
        with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
            event = json.load(f)

        # Get the base and head SHAs for the PR
        base_sha = event["pull_request"]["base"]["sha"]
        head_sha = event["pull_request"]["head"]["sha"]

        # Get the list of changed files between the base and head
        stdout, _, _ = run_command(["git", "diff", "--name-only", base_sha, head_sha])
    else:
        # For local testing, just get the changed files in the working directory
        stdout, _, _ = run_command(["git", "diff", "--name-only", "HEAD"])

    return [f for f in stdout.split("\n") if f.strip()]


def check_patterns_compliance(changed_files):
    """Check if any changes to pattern-related files comply with the patterns documentation"""
    if not os.path.exists(patterns_file):
        issues.append(f"WARNING: Patterns documentation file {patterns_file} not found")
        return

    # Read patterns from documentation
    with open(patterns_file, "r") as f:
        content = f.read()

    # Extract pattern keys from the documentation
    pattern_keys = []
    pattern_table_match = re.search(
        r"\| Pattern Key \| Name \| Description \|(.*?)\n\n", content, re.DOTALL
    )
    if pattern_table_match:
        pattern_table = pattern_table_match.group(1)
        pattern_rows = pattern_table.strip().split("\n")
        for row in pattern_rows:
            if "|" in row:
                cols = [col.strip() for col in row.split("|")]
                if len(cols) >= 4 and cols[1] and cols[1] != "-------------":
                    pattern_keys.append(cols[1].strip("`"))

    # Check for files related to pattern implementation
    pattern_related_files = [
        f
        for f in changed_files
        if "pattern" in f.lower()
        or "analysis" in f.lower()
        or any(pattern in f.lower() for pattern in pattern_keys)
    ]

    for file in pattern_related_files:
        if file.endswith((".tsx", ".ts", ".js", ".jsx", ".py")):
            with open(file, "r") as f:
                file_content = f.read()

            # Check for pattern keys not documented
            for match in re.finditer(r'[\'"]([a-z_]+)[\'"]', file_content):
                potential_key = match.group(1)
                if (
                    ("pattern" in file.lower() or "analysis" in file.lower())
                    and len(potential_key) > 3
                    and potential_key not in pattern_keys
                    and not potential_key.startswith("is_")
                    and not potential_key.startswith("has_")
                    and not potential_key.startswith("get_")
                    and not potential_key.startswith("set_")
                    and not potential_key.startswith("on_")
                ):
                    issues.append(
                        f"COMPLIANCE ISSUE: Potential undocumented pattern key '{potential_key}' in {file}"
                    )


def check_duplicate_functionality(changed_files):
    """Check for potential duplicate functionality"""
    component_files = [f for f in changed_files if f.endswith((".tsx", ".jsx"))]

    # Check for files with similar names
    basename_map = {}
    for file in component_files:
        basename = os.path.basename(file)
        if basename in basename_map:
            issues.append(
                f"DUPLICATE FILE: {file} has same name as {basename_map[basename]}"
            )
        else:
            basename_map[basename] = file

    # Check for similar component definitions
    component_definitions = {}
    for file in component_files:
        with open(file, "r") as f:
            content = f.read()

        # Extract component names
        for match in re.finditer(
            r"function\s+([A-Z][a-zA-Z0-9]+)|class\s+([A-Z][a-zA-Z0-9]+)", content
        ):
            component_name = match.group(1) or match.group(2)
            if component_name in component_definitions:
                issues.append(
                    f"DUPLICATE COMPONENT: '{component_name}' defined in both {file} and {component_definitions[component_name]}"
                )
            else:
                component_definitions[component_name] = file


def check_documentation_references(changed_files):
    """Check if changed files reference documentation properly"""
    code_files = [
        f for f in changed_files if f.endswith((".tsx", ".ts", ".jsx", ".js", ".py"))
    ]

    for file in code_files:
        with open(file, "r") as f:
            content = f.read()

        # Check for code that should reference documentation
        if re.search(
            r"(pattern|feather|intelligence multiplication|analysis type)",
            content,
            re.IGNORECASE,
        ):
            if not re.search(
                r"(documentation|PATTERNS.md|INTELLIGENCE_MULTIPLICATION.md)",
                content,
                re.IGNORECASE,
            ):
                issues.append(
                    f"DOCUMENTATION REFERENCE MISSING: {file} contains pattern-related code but doesn't reference documentation"
                )


def check_hook_usage(changed_files):
    """Check if components are using hooks properly"""
    component_files = [f for f in changed_files if f.endswith((".tsx", ".jsx"))]
    hook_files = [
        f for f in changed_files if "hook" in f.lower() and f.endswith((".ts", ".tsx"))
    ]

    # Extract hook exports
    available_hooks = set()
    for hook_file in hook_files:
        with open(hook_file, "r") as f:
            content = f.read()

        for match in re.finditer(r"export const\s+([a-zA-Z0-9_]+)", content):
            hook_name = match.group(1)
            if hook_name.startswith("use"):
                available_hooks.add(hook_name)

    # Check if components reimplement hook functionality
    for component_file in component_files:
        with open(component_file, "r") as f:
            content = f.read()

        # Look for hook imports
        imported_hooks = set()
        for match in re.finditer(r"import.*\{([^}]+)\}.*from", content):
            imports = match.group(1)
            for imp in imports.split(","):
                hook_name = imp.strip()
                if hook_name.startswith("use"):
                    imported_hooks.add(hook_name)

        # Check for hooks that should be used but aren't imported
        for hook in available_hooks:
            hook_purpose = hook.replace("use", "").lower()
            pattern = rf"function\s+[A-Z][a-zA-Z0-9]*.*\{{.*{hook_purpose}.*\}}"
            if (
                re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                and hook not in imported_hooks
            ):
                issues.append(
                    f"HOOK USAGE ISSUE: {component_file} appears to reimplement functionality available in {hook}"
                )


def main():
    """Main function to run all checks"""
    changed_files = get_changed_files()

    if not changed_files:
        print("No changed files detected")
        return

    print(
        f"Running documentation compliance checks on {len(changed_files)} changed files"
    )

    check_patterns_compliance(changed_files)
    check_duplicate_functionality(changed_files)
    check_documentation_references(changed_files)
    check_hook_usage(changed_files)

    if issues:
        print("\n".join(issues))
        # Set output for GitHub Actions
        with open(os.environ.get("GITHUB_OUTPUT", "compliance_output.txt"), "a") as f:
            f.write("COMPLIANCE_RESULT<<EOF\n")
            f.write("\n".join(issues))
            f.write("\nEOF\n")
        sys.exit(1)
    else:
        print("All checks passed!")
        # Set output for GitHub Actions
        with open(os.environ.get("GITHUB_OUTPUT", "compliance_output.txt"), "a") as f:
            f.write("COMPLIANCE_RESULT=All documentation compliance checks passed\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
