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
from typing import Any, Dict, List, Optional

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


def main():
    """Main function to refactor all route files."""
    routes_dir = Path("app/routes")
    route_files = [
        "oauth_routes.py",
        "available_models_routes.py",
        "debug_routes.py",
        "document_analysis_routes.py",
        "metrics.py",
    ]

    for file_name in route_files:
        file_path = routes_dir / file_name
        if file_path.exists():
            try:
                refactorer = RouteRefactorer(str(file_path))
                refactorer.refactor()
            except Exception as e:
                logger.error(f"Error refactoring {file_name}: {e}")
        else:
            logger.warning(f"File not found: {file_name}")


if __name__ == "__main__":
    main()
