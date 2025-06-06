#!/usr/bin/env python3
"""
Script to batch fix common issues in route files.
"""

import re
from pathlib import Path

# Common imports that should be present
REQUIRED_IMPORTS = {
    "fastapi": {"APIRouter", "Depends", "HTTPException", "Request", "Response"},
    "pydantic": {"BaseModel"},
    "typing": {"Any", "Dict", "List", "Optional", "Union"},
}

# Common imports that should be removed
UNUSED_IMPORTS = {
    "JSONResponse",
    "Query",
    "Path",
    "Body",
    "Header",
    "Cookie",
    "Form",
    "File",
    "UploadFile",
}


def fix_imports(content: str) -> str:
    """Fix imports in the file."""
    # Remove duplicate imports
    lines = content.split("\n")
    seen_imports = set()
    filtered_lines = []

    for line in lines:
        if line.startswith("from ") or line.startswith("import "):
            if line not in seen_imports:
                seen_imports.add(line)
                filtered_lines.append(line)
        else:
            filtered_lines.append(line)

    content = "\n".join(filtered_lines)

    # Add missing imports
    for module, names in REQUIRED_IMPORTS.items():
        if not any(f"{module}." in imp for imp in names):
            content = f"from {module} import {', '.join(sorted(names))}\n{content}"

    # Remove unused imports
    for imp in UNUSED_IMPORTS:
        content = re.sub(rf"from \w+ import .*{imp}.*\n", "", content)
        content = re.sub(rf"import {imp}\n", "", content)

    return content


def fix_docstrings(content: str) -> str:
    """Fix docstrings in the file."""
    # Remove duplicate module docstrings
    content = re.sub(
        r'""".*?"""\s*""".*?"""',
        '"""\nRoute handlers for the Ultra backend.\n\nThis module provides API routes for various endpoints.\n"""',
        content,
        flags=re.DOTALL,
    )

    # Fix function docstrings
    def replace_docstring(match):
        func_name = match.group(1)
        warning = "WARNING: This endpoint is for development/testing only. Do not use in production."

        if "get" in match.group(2).lower():
            return f'    """\n    Get {func_name.replace("_", " ")}.\n    {warning}\n    """'
        elif "post" in match.group(2).lower():
            return f'    """\n    Create {func_name.replace("_", " ")}.\n    {warning}\n    """'
        elif "put" in match.group(2).lower():
            return f'    """\n    Update {func_name.replace("_", " ")}.\n    {warning}\n    """'
        elif "delete" in match.group(2).lower():
            return f'    """\n    Delete {func_name.replace("_", " ")}.\n    {warning}\n    """'
        return match.group(0)

    content = re.sub(
        r'async def (\w+)\([^)]*\):\s*"""(.*?)"""',
        replace_docstring,
        content,
        flags=re.DOTALL,
    )

    return content


def fix_route_decorators(content: str) -> str:
    """Fix malformed route decorators."""
    # Fix route decorators with duplicate response models
    content = re.sub(
        r"@\w+\.\w+\([^)]*\)class \w+\(BaseModel\):.*?response_model=\w+\)",
        lambda m: re.sub(
            r"class \w+\(BaseModel\):.*?response_model=\w+", "", m.group(0)
        ),
        content,
        flags=re.DOTALL,
    )

    # Fix route decorators with malformed response_model
    content = re.sub(
        r"@\w+\.\w+\([^)]*\)class \w+\(BaseModel\):.*?response_model=\w+\)",
        lambda m: re.sub(
            r"class \w+\(BaseModel\):.*?response_model=\w+", "", m.group(0)
        ),
        content,
        flags=re.DOTALL,
    )

    return content


def fix_type_hints(content: str) -> str:
    """Fix type hints in the file."""

    # Add return type hints
    def add_return_type(match):
        func_name = match.group(1)
        params = match.group(2)
        model_match = re.search(r"response_model=(\w+)", params)
        if model_match:
            model = model_match.group(1)
            return f"async def {func_name}({params}) -> {model}:"
        return match.group(0)

    content = re.sub(r"async def (\w+)\((.*?)\):", add_return_type, content)

    return content


def fix_response_models(content: str) -> str:
    """Fix response models in the file."""
    # Remove duplicate response model definitions
    seen_models = set()
    lines = content.split("\n")
    filtered_lines = []

    for line in lines:
        if line.startswith("class ") and line.endswith("(BaseModel):"):
            model_name = line.split()[1]
            if model_name not in seen_models:
                seen_models.add(model_name)
                filtered_lines.append(line)
        else:
            filtered_lines.append(line)

    content = "\n".join(filtered_lines)

    return content


def process_file(file_path: Path) -> None:
    """Process a single file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Apply fixes
        content = fix_imports(content)
        content = fix_docstrings(content)
        content = fix_route_decorators(content)
        content = fix_type_hints(content)
        content = fix_response_models(content)

        # Write back to file
        with open(file_path, "w") as f:
            f.write(content)

        print(f"Fixed {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")


def main():
    """Main function to process all route files."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent

    # Path to routes directory
    routes_dir = project_root / "app" / "routes"

    # Process all Python files in routes directory
    for file_path in routes_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            process_file(file_path)


if __name__ == "__main__":
    main()
