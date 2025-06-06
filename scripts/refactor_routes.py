#!/usr/bin/env python3
"""
Route Refactoring Automation Script

This script automates the refactoring of FastAPI route files to use the create_router pattern
and apply consistent coding standards.
"""

import ast
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common imports that should be present in all route files
COMMON_IMPORTS = [
    "import logging",
    "from typing import Any, Dict, Optional",
    "from fastapi import APIRouter, HTTPException",
    "from fastapi.responses import JSONResponse",
]

# Template for create_router function
CREATE_ROUTER_TEMPLATE = '''
def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["{tag}"])
'''

# Template for endpoint function
ENDPOINT_TEMPLATE = '''
    @router.{method}("{path}"{response_model})
    async def {name}({params}):
        """
        {docstring}
        """
        {body}
'''


class RouteRefactorer:
    """Class to handle route file refactoring."""

    def __init__(self, file_path: str):
        """Initialize the refactorer with a file path."""
        self.file_path = file_path
        self.content = ""
        self.ast_tree = None
        self.router_name = ""
        self.tag = ""
        self.endpoints = []

    def read_file(self) -> None:
        """Read and parse the route file."""
        try:
            with open(self.file_path, "r") as f:
                self.content = f.read()
            self.ast_tree = ast.parse(self.content)
        except SyntaxError as e:
            logger.error(f"Syntax error in {self.file_path}: {e}")
            # Try to fix common syntax errors
            self._fix_syntax_errors()
            self.ast_tree = ast.parse(self.content)

    def _fix_syntax_errors(self) -> None:
        """Fix common syntax errors in route files."""
        # Fix response model syntax
        self.content = re.sub(
            r"response_model=([^,)]+)(?=[,)])", r", response_model=\1", self.content
        )

        # Fix Union type syntax
        self.content = re.sub(
            r"class Union\(BaseModel\):",
            r"class UnionResponse(BaseModel):",
            self.content,
        )

    def extract_router_info(self) -> None:
        """Extract router name and tag from the file."""
        if not self.ast_tree:
            return

        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and "router" in target.id.lower():
                        self.router_name = target.id
                        if isinstance(node.value, ast.Call):
                            for keyword in node.value.keywords:
                                if keyword.arg == "tags":
                                    if isinstance(keyword.value, ast.List):
                                        self.tag = keyword.value.elts[0].value
                                    elif isinstance(keyword.value, ast.Constant):
                                        self.tag = keyword.value.value

    def extract_endpoints(self) -> None:
        """Extract endpoint information from the file."""
        if not self.ast_tree:
            return

        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, "attr") and decorator.func.attr in [
                            "get",
                            "post",
                            "put",
                            "delete",
                        ]:
                            method = decorator.func.attr
                            path = decorator.args[0].value

                            # Extract response model if present
                            response_model = ""
                            for keyword in decorator.keywords:
                                if keyword.arg == "response_model":
                                    response_model = (
                                        f", response_model={ast.unparse(keyword.value)}"
                                    )

                            self.endpoints.append(
                                {
                                    "name": node.name,
                                    "method": method,
                                    "path": path,
                                    "params": self._get_function_params(node),
                                    "docstring": ast.get_docstring(node) or "",
                                    "body": self._get_function_body(node),
                                    "response_model": response_model,
                                }
                            )

    def _get_function_params(self, node: ast.FunctionDef) -> str:
        """Extract function parameters."""
        params = []
        for arg in node.args.args:
            if arg.arg != "self":
                params.append(arg.arg)
        return ", ".join(params)

    def _get_function_body(self, node: ast.FunctionDef) -> str:
        """Extract function body."""
        body_lines = []
        for item in node.body:
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Str):
                continue  # Skip docstring
            body_lines.append(ast.unparse(item))
        return "\n        ".join(body_lines)

    def generate_new_content(self) -> str:
        """Generate the refactored file content."""
        # Add module docstring
        content = [f'"""\n{self._get_module_docstring()}\n"""\n']

        # Add imports
        content.extend(COMMON_IMPORTS)
        content.append("")

        # Add create_router function
        content.append(CREATE_ROUTER_TEMPLATE.format(tag=self.tag))

        # Add endpoints
        for endpoint in self.endpoints:
            content.append(
                ENDPOINT_TEMPLATE.format(
                    method=endpoint["method"],
                    path=endpoint["path"],
                    name=endpoint["name"],
                    params=endpoint["params"],
                    docstring=endpoint["docstring"],
                    body=endpoint["body"],
                    response_model=endpoint["response_model"],
                )
            )

        # Add return statement
        content.append("    return router\n")

        return "\n".join(content)

    def _get_module_docstring(self) -> str:
        """Extract module docstring."""
        if (
            self.ast_tree
            and self.ast_tree.body
            and isinstance(self.ast_tree.body[0], ast.Expr)
        ):
            if isinstance(self.ast_tree.body[0].value, ast.Str):
                return self.ast_tree.body[0].value.s
        return "Route handlers for the Ultra backend."

    def refactor(self) -> None:
        """Refactor the route file."""
        self.read_file()
        self.extract_router_info()
        self.extract_endpoints()
        new_content = self.generate_new_content()

        # Create backup
        backup_path = f"{self.file_path}.bak"
        os.rename(self.file_path, backup_path)

        # Write new content
        with open(self.file_path, "w") as f:
            f.write(new_content)

        logger.info(f"Refactored {self.file_path}")


def get_route_files() -> List[Path]:
    """Get all route files that need refactoring."""
    routes_dir = Path("app/routes")
    return [f for f in routes_dir.glob("*.py") if not f.name.startswith("__")]


def extract_dependencies(content: str) -> Dict[str, Set[str]]:
    """Extract dependencies from route file content."""
    imports = set()
    services = set()

    # Extract imports
    import_pattern = r"from\s+([\w\.]+)\s+import"
    imports.update(re.findall(import_pattern, content))

    # Extract service dependencies
    service_pattern = r"from\s+app\.services\.(\w+)\s+import"
    services.update(re.findall(service_pattern, content))

    return {"imports": imports, "services": services}


def extract_endpoints(content: str) -> List[Tuple[str, str, str, str]]:
    """Extract endpoint definitions from route file content."""
    endpoints = []

    # Match route decorators and their functions
    route_pattern = r"@\w+\.(get|post|put|delete|patch)\s*\(\s*[\"']([^\"']+)[\"']\s*\)\s*\n\s*async\s+def\s+(\w+)\s*\(([^)]*)\)\s*:"
    matches = re.finditer(route_pattern, content)

    for match in matches:
        method, path, func_name, params = match.groups()
        # Extract the function body
        func_start = match.end()
        func_end = content.find("\n\n", func_start)
        if func_end == -1:
            func_end = len(content)
        func_body = content[func_start:func_end].strip()

        # Extract imports needed for this endpoint
        imports = set()
        for line in func_body.split("\n"):
            if "import" in line:
                imports.add(line.strip())

        endpoints.append((method, path, func_name, params, func_body, imports))

    return endpoints


def create_dependency_injection(services: Set[str]) -> str:
    """Create dependency injection functions for services."""
    deps = []
    for service in services:
        deps.append(
            f"""
def get_{service}() -> {service.title()}:
    \"\"\"Dependency provider for {service.title()}.\"\"\"
    return {service}()
"""
        )
    return "\n".join(deps)


def refactor_route_file(file_path: Path) -> None:
    """Refactor a single route file to use create_router pattern."""
    with open(file_path, "r") as f:
        content = f.read()

    # Extract dependencies and endpoints
    deps = extract_dependencies(content)
    endpoints = extract_endpoints(content)

    # Collect all imports needed
    all_imports = set()
    for _, _, _, _, _, imports in endpoints:
        all_imports.update(imports)

    # Create new content with create_router pattern
    new_content = f'''"""
Route handlers for the Ultra backend.
"""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

{create_dependency_injection(deps["services"])}

def create_router() -> APIRouter:
    """
    Create the router with all endpoints.

    Returns:
        APIRouter: The configured router
    """
    router = APIRouter(tags=["{file_path.stem.replace('_routes', '').title()}"])

'''

    # Add endpoints to router
    for method, path, func_name, params, func_body, _ in endpoints:
        new_content += f"""
    @router.{method}("{path}")
    async def {func_name}({params}):
{func_body}

"""

    new_content += "    return router"

    # Create backup
    backup_path = file_path.with_suffix(".py.bak")
    if not backup_path.exists():
        with open(backup_path, "w") as f:
            f.write(content)

    # Write new content
    with open(file_path, "w") as f:
        f.write(new_content)


def main():
    """Main function to refactor all route files."""
    route_files = get_route_files()
    for file_path in route_files:
        print(f"Refactoring {file_path.name}...")
        refactor_route_file(file_path)
        print(f"✓ {file_path.name} refactored")


if __name__ == "__main__":
    main()
