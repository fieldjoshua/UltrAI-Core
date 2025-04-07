#!/usr/bin/env python3
"""
UltraAI Parameter Glossary Generator

This script scans the UltraAI codebase to identify adjustable parameters and constants,
then generates a comprehensive parameter glossary with documentation and default values.
It also creates a simple interface for viewing and adjusting these parameters.
"""

import os
import re
import ast
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parameter_glossary.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('parameter_glossary')

# Set up paths
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
output_dir = script_dir / "parameter_glossary"
output_dir.mkdir(exist_ok=True)

# Files to ignore
IGNORE_DIRS = {
    '.git', '__pycache__', 'venv', '.venv', 'node_modules',
    'build', 'dist', '.pytest_cache', '.cache', '.swc'
}

# Parameter name patterns to identify as configurable
PARAMETER_PATTERNS = [
    r'.*_THRESHOLD',
    r'.*_TIMEOUT',
    r'.*_MAX',
    r'.*_MIN',
    r'.*_LIMIT',
    r'.*_ENABLED',
    r'.*_DISABLED',
    r'.*_URL',
    r'.*_PATH',
    r'.*_DIR',
    r'.*_FILE',
    r'.*_KEY',
    r'.*_SECRET',
    r'.*_TOKEN',
    r'.*_CONFIG',
    r'.*_SETTINGS',
    r'DEFAULT_.*',
    r'MAX_.*',
    r'MIN_.*',
]

class ParameterInfo:
    """Information about a parameter including its location, value, and documentation"""
    def __init__(
        self, 
        name: str, 
        value: Any, 
        file_path: str, 
        line_number: int, 
        doc_string: Optional[str] = None,
        parameter_type: str = "constant"
    ):
        self.name = name
        self.value = value
        self.file_path = file_path
        self.line_number = line_number
        self.doc_string = doc_string
        self.parameter_type = parameter_type  # constant, env_var, config, etc.
        self.editable = True  # Whether this parameter should be editable
        
        # Try to determine the data type
        if isinstance(value, str):
            self.data_type = "string"
        elif isinstance(value, bool):
            self.data_type = "boolean"
        elif isinstance(value, int):
            self.data_type = "integer"
        elif isinstance(value, float):
            self.data_type = "float"
        elif isinstance(value, list):
            self.data_type = "list"
        elif isinstance(value, dict):
            self.data_type = "dictionary"
        else:
            self.data_type = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameter info to a dictionary for JSON serialization"""
        return {
            "name": self.name,
            "value": str(self.value),  # Convert to string for serialization
            "raw_value": self.value if isinstance(self.value, (str, bool, int, float)) else str(self.value),
            "file_path": self.file_path,
            "line_number": self.line_number,
            "doc_string": self.doc_string,
            "parameter_type": self.parameter_type,
            "data_type": self.data_type,
            "editable": self.editable
        }

class ParameterExtractor(ast.NodeVisitor):
    """AST visitor to extract parameters from Python files"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parameters = []
        self.imports = {}
        self.current_class = None
        self.current_function = None
        self.module_docstring = None
    
    def get_doc_string(self, node: ast.AST) -> Optional[str]:
        """Extract docstring for a node if available"""
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            return None
            
        if not node.body:
            return None
            
        first_node = node.body[0]
        if isinstance(first_node, ast.Expr) and isinstance(first_node.value, ast.Str):
            return first_node.value.s
        return None
    
    def visit_Module(self, node: ast.Module) -> None:
        """Visit a module and extract its docstring"""
        self.module_docstring = self.get_doc_string(node)
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Process import statements"""
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from-import statements"""
        module = node.module or ""
        for name in node.names:
            self.imports[name.asname or name.name] = f"{module}.{name.name}"
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition"""
        prev_class = self.current_class
        self.current_class = node.name
        
        class_doc = self.get_doc_string(node)
        
        # Extract class variables (constants)
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name.isupper() or any(re.match(pattern, name) for pattern in PARAMETER_PATTERNS):
                            try:
                                value = ast.literal_eval(item.value)
                                doc_string = class_doc  # Use class docstring for context
                                
                                self.parameters.append(ParameterInfo(
                                    name=f"{self.current_class}.{name}",
                                    value=value,
                                    file_path=self.file_path,
                                    line_number=item.lineno,
                                    doc_string=doc_string,
                                    parameter_type="class_constant"
                                ))
                            except (ValueError, SyntaxError):
                                # Skip if we can't evaluate the literal value
                                pass
        
        self.generic_visit(node)
        self.current_class = prev_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition"""
        prev_function = self.current_function
        self.current_function = node.name
        
        func_doc = self.get_doc_string(node)
        
        # Extract default parameter values
        for arg in node.args.defaults:
            if isinstance(arg, (ast.Str, ast.Num, ast.NameConstant, ast.List, ast.Dict)):
                try:
                    value = ast.literal_eval(arg)
                    # Note: we don't have the parameter name here directly
                    # This would require more complex logic to match defaults with param names
                except (ValueError, SyntaxError):
                    pass
        
        self.generic_visit(node)
        self.current_function = prev_function
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment statements to extract constants"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                if name.isupper() or any(re.match(pattern, name) for pattern in PARAMETER_PATTERNS):
                    try:
                        value = ast.literal_eval(node.value)
                        
                        # Look for a comment on the same line or immediately above
                        doc_string = None
                        
                        # Construct full name including class if applicable
                        full_name = f"{self.current_class + '.' if self.current_class else ''}{name}"
                        
                        self.parameters.append(ParameterInfo(
                            name=full_name,
                            value=value,
                            file_path=self.file_path,
                            line_number=node.lineno,
                            doc_string=doc_string,
                            parameter_type="constant"
                        ))
                    except (ValueError, SyntaxError):
                        # Skip if we can't evaluate the literal value
                        pass
        self.generic_visit(node)

def extract_inline_comments(file_path: str) -> Dict[int, str]:
    """Extract inline comments from a Python file, indexed by line number"""
    comments = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                comment_pos = line.find('#')
                if comment_pos >= 0:
                    comment = line[comment_pos+1:].strip()
                    if comment:
                        comments[i] = comment
        return comments
    except Exception as e:
        logger.warning(f"Error extracting comments from {file_path}: {e}")
        return {}

def extract_parameters_from_file(file_path: str) -> List[ParameterInfo]:
    """Extract all parameters from a Python file"""
    logger.debug(f"Processing file: {file_path}")
    parameters = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # Parse the AST
        tree = ast.parse(file_content)
        extractor = ParameterExtractor(file_path)
        extractor.visit(tree)
        
        # Get comments to enrich parameter docs
        comments = extract_inline_comments(file_path)
        
        for param in extractor.parameters:
            # If there's a comment on the same line as the parameter, use it as documentation
            if param.line_number in comments:
                param.doc_string = comments[param.line_number]
            
            # If there's a comment on the previous line, it might also be documentation
            if param.line_number - 1 in comments and not param.doc_string:
                param.doc_string = comments[param.line_number - 1]
                
            parameters.append(param)
            
        # Also look for environment variable usage
        env_vars = extract_env_vars_from_content(file_content, file_path)
        parameters.extend(env_vars)
            
        return parameters
    
    except Exception as e:
        logger.warning(f"Error processing file {file_path}: {e}")
        return []

def extract_env_vars_from_content(content: str, file_path: str) -> List[ParameterInfo]:
    """Extract environment variables used in the code"""
    parameters = []
    
    # Find calls to os.environ.get() or os.getenv()
    env_patterns = [
        r"os\.environ\.get\(['\"]([A-Za-z0-9_]+)['\"](?:,\s*['\"]?([^'\")]+)['\"]?)?\)",
        r"os\.getenv\(['\"]([A-Za-z0-9_]+)['\"](?:,\s*['\"]?([^'\")]+)['\"]?)?\)"
    ]
    
    line_number = 1
    for line in content.split("\n"):
        for pattern in env_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                var_name = match[0]
                default_value = match[1] if len(match) > 1 else None
                
                # Extract any comment on this line
                comment_pos = line.find('#')
                doc_string = line[comment_pos+1:].strip() if comment_pos >= 0 else None
                
                # Try to determine the actual type of the default value
                if default_value is not None:
                    try:
                        # Handle common type cases
                        if default_value.lower() == 'true':
                            default_value = True
                        elif default_value.lower() == 'false':
                            default_value = False
                        elif default_value.isdigit():
                            default_value = int(default_value)
                        elif re.match(r"^\d+\.\d+$", default_value):
                            default_value = float(default_value)
                    except:
                        pass
                
                parameters.append(ParameterInfo(
                    name=var_name,
                    value=default_value,
                    file_path=file_path,
                    line_number=line_number,
                    doc_string=doc_string,
                    parameter_type="environment_variable"
                ))
        line_number += 1
    
    return parameters

def scan_python_files(directory: Path) -> List[Path]:
    """Recursively scan for Python files in a directory"""
    python_files = []
    
    for item in directory.iterdir():
        # Skip ignored directories
        if item.is_dir() and item.name in IGNORE_DIRS:
            continue
            
        if item.is_file() and item.suffix == '.py':
            python_files.append(item)
        elif item.is_dir():
            python_files.extend(scan_python_files(item))
    
    return python_files

def extract_all_parameters(python_files: List[Path]) -> Dict[str, List[ParameterInfo]]:
    """Extract parameters from all Python files and group by file"""
    parameters_by_file = {}
    
    for file_path in python_files:
        rel_path = str(file_path.relative_to(project_root))
        parameters = extract_parameters_from_file(str(file_path))
        if parameters:
            parameters_by_file[rel_path] = parameters
    
    return parameters_by_file

def generate_parameter_glossary(parameters_by_file: Dict[str, List[ParameterInfo]]) -> Dict[str, Any]:
    """Generate a parameter glossary from extracted parameters"""
    glossary = {
        "timestamp": "",  # Will be filled in by the web UI
        "files": {},
        "categories": {
            "constants": [],
            "environment_variables": [],
            "class_constants": []
        }
    }
    
    # Group by file
    for file_path, parameters in parameters_by_file.items():
        file_entry = {
            "path": file_path,
            "parameters": [param.to_dict() for param in parameters]
        }
        glossary["files"][file_path] = file_entry
        
        # Also add to categories
        for param in parameters:
            param_dict = param.to_dict()
            if param.parameter_type == "environment_variable":
                glossary["categories"]["environment_variables"].append(param_dict)
            elif param.parameter_type == "class_constant":
                glossary["categories"]["class_constants"].append(param_dict)
            else:
                glossary["categories"]["constants"].append(param_dict)
    
    return glossary

def save_glossary(glossary: Dict[str, Any], output_path: Path) -> None:
    """Save the glossary to a JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(glossary, f, indent=2)
    logger.info(f"Parameter glossary saved to {output_path}")

def main():
    """Main function to generate the parameter glossary"""
    parser = argparse.ArgumentParser(description="Generate a parameter glossary for UltraAI")
    parser.add_argument("--output", "-o", default="parameters.json", help="Output JSON file")
    args = parser.parse_args()
    
    output_path = output_dir / args.output
    
    logger.info("Scanning for Python files...")
    python_files = scan_python_files(project_root)
    logger.info(f"Found {len(python_files)} Python files")
    
    logger.info("Extracting parameters...")
    parameters_by_file = extract_all_parameters(python_files)
    
    logger.info("Generating parameter glossary...")
    glossary = generate_parameter_glossary(parameters_by_file)
    
    logger.info("Saving parameter glossary...")
    save_glossary(glossary, output_path)
    
    logger.info(f"Parameter glossary generated successfully. Check {output_path}")
    
    # Also generate the HTML interface
    html_path = output_dir / "parameters.html"
    generate_html_interface(html_path)
    logger.info(f"HTML interface generated at {html_path}")

def generate_html_interface(output_path: Path) -> None:
    """Generate a simple HTML interface for viewing and modifying parameters"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UltraAI Parameter Glossary</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .nav {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .nav-item {
            padding: 8px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-weight: 500;
        }
        .nav-item.active {
            border-color: #3498db;
            color: #3498db;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .file-section {
            margin-bottom: 30px;
            border: 1px solid #eee;
            border-radius: 5px;
            padding: 15px;
        }
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .file-path {
            font-weight: 500;
            color: #2c3e50;
        }
        .parameter-count {
            background: #f1f1f1;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .parameter-table {
            width: 100%;
            border-collapse: collapse;
        }
        .parameter-table th, .parameter-table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .parameter-table th {
            background-color: #f8f9fa;
        }
        .parameter-name {
            font-family: monospace;
            font-weight: 500;
            color: #0366d6;
        }
        .parameter-value {
            font-family: monospace;
        }
        .parameter-value input {
            width: 100%;
            padding: 4px 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        .parameter-docs {
            color: #666;
            max-width: 300px;
        }
        .parameter-type {
            font-size: 0.85em;
            padding: 2px 6px;
            border-radius: 3px;
            background: #e1e4e8;
        }
        .search-container {
            margin-bottom: 20px;
        }
        .search-input {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1em;
        }
        .toggle-all {
            margin-bottom: 10px;
            font-weight: 500;
            cursor: pointer;
            color: #3498db;
        }
        .save-button {
            padding: 8px 16px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
        }
        .save-button:hover {
            background: #2980b9;
        }
        .no-results {
            padding: 20px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>UltraAI Parameter Glossary</h1>
    <div class="search-container">
        <input type="text" id="search-input" class="search-input" placeholder="Search parameters..." oninput="filterParameters()">
    </div>
    
    <div class="nav">
        <div class="nav-item active" data-tab="by-file">By File</div>
        <div class="nav-item" data-tab="by-category">By Category</div>
    </div>
    
    <div id="by-file" class="tab-content active">
        <div class="toggle-all" onclick="toggleAllSections()">Expand/Collapse All</div>
        <div id="file-container"></div>
    </div>
    
    <div id="by-category" class="tab-content">
        <div id="category-container"></div>
    </div>
    
    <div style="margin-top: 20px; text-align: right;">
        <button id="save-button" class="save-button" onclick="saveParameters()">Save Changes</button>
    </div>

    <script>
        let glossaryData = {};
        let expandedSections = new Set();
        
        // Fetch the parameter data
        async function loadParameterData() {
            try {
                const response = await fetch('parameters.json');
                glossaryData = await response.json();
                renderFileView();
                renderCategoryView();
            } catch (error) {
                console.error("Error loading parameter data:", error);
                document.getElementById('file-container').innerHTML = 
                    '<div class="no-results">Error loading parameter data. Make sure parameters.json exists.</div>';
            }
        }
        
        // Render the file-based view
        function renderFileView() {
            const container = document.getElementById('file-container');
            container.innerHTML = '';
            
            const files = Object.entries(glossaryData.files);
            if (files.length === 0) {
                container.innerHTML = '<div class="no-results">No parameters found</div>';
                return;
            }
            
            files.sort((a, b) => a[0].localeCompare(b[0])).forEach(([filePath, fileData]) => {
                const parameters = fileData.parameters;
                if (parameters.length === 0) return;
                
                const fileSection = document.createElement('div');
                fileSection.className = 'file-section';
                fileSection.id = `file-${encodeURIComponent(filePath)}`;
                
                const fileHeader = document.createElement('div');
                fileHeader.className = 'file-header';
                fileHeader.innerHTML = `
                    <div class="file-path" onclick="toggleSection('${encodeURIComponent(filePath)}')">${filePath}</div>
                    <div class="parameter-count">${parameters.length} parameters</div>
                `;
                fileSection.appendChild(fileHeader);
                
                const tableContainer = document.createElement('div');
                tableContainer.id = `section-${encodeURIComponent(filePath)}`;
                tableContainer.style.display = expandedSections.has(filePath) ? 'block' : 'none';
                
                const table = document.createElement('table');
                table.className = 'parameter-table';
                table.innerHTML = `
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Type</th>
                            <th>Documentation</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${parameters.map(param => createParameterRow(param)).join('')}
                    </tbody>
                `;
                
                tableContainer.appendChild(table);
                fileSection.appendChild(tableContainer);
                container.appendChild(fileSection);
            });
        }
        
        // Render the category-based view
        function renderCategoryView() {
            const container = document.getElementById('category-container');
            container.innerHTML = '';
            
            const categories = {
                'Environment Variables': glossaryData.categories.environment_variables,
                'Constants': glossaryData.categories.constants,
                'Class Constants': glossaryData.categories.class_constants
            };
            
            Object.entries(categories).forEach(([categoryName, parameters]) => {
                if (parameters.length === 0) return;
                
                const categorySection = document.createElement('div');
                categorySection.className = 'file-section';
                
                const categoryHeader = document.createElement('div');
                categoryHeader.className = 'file-header';
                categoryHeader.innerHTML = `
                    <div class="file-path">${categoryName}</div>
                    <div class="parameter-count">${parameters.length} parameters</div>
                `;
                categorySection.appendChild(categoryHeader);
                
                const table = document.createElement('table');
                table.className = 'parameter-table';
                table.innerHTML = `
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Type</th>
                            <th>File Path</th>
                            <th>Documentation</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${parameters.map(param => createCategoryParameterRow(param)).join('')}
                    </tbody>
                `;
                
                categorySection.appendChild(table);
                container.appendChild(categorySection);
            });
        }
        
        // Create a table row for a parameter in file view
        function createParameterRow(param) {
            const valueInput = param.editable 
                ? `<input type="text" id="input-${param.name}" class="parameter-value-input" value="${param.raw_value}" data-original="${param.raw_value}" data-param-name="${param.name}" data-file-path="${param.file_path}">`
                : param.value;
                
            return `
                <tr class="parameter-row" data-name="${param.name.toLowerCase()}" data-doc="${(param.doc_string || '').toLowerCase()}">
                    <td class="parameter-name">${param.name}</td>
                    <td class="parameter-value">${valueInput}</td>
                    <td><span class="parameter-type">${param.data_type}</span></td>
                    <td class="parameter-docs">${param.doc_string || ''}</td>
                </tr>
            `;
        }
        
        // Create a table row for a parameter in category view
        function createCategoryParameterRow(param) {
            const valueInput = param.editable 
                ? `<input type="text" id="cat-input-${param.name}" class="parameter-value-input" value="${param.raw_value}" data-original="${param.raw_value}" data-param-name="${param.name}" data-file-path="${param.file_path}">`
                : param.value;
                
            return `
                <tr class="parameter-row" data-name="${param.name.toLowerCase()}" data-doc="${(param.doc_string || '').toLowerCase()}">
                    <td class="parameter-name">${param.name}</td>
                    <td class="parameter-value">${valueInput}</td>
                    <td><span class="parameter-type">${param.data_type}</span></td>
                    <td>${param.file_path}</td>
                    <td class="parameter-docs">${param.doc_string || ''}</td>
                </tr>
            `;
        }
        
        // Filter parameters based on search input
        function filterParameters() {
            const searchText = document.getElementById('search-input').value.toLowerCase();
            const rows = document.querySelectorAll('.parameter-row');
            let visibleFiles = new Set();
            
            rows.forEach(row => {
                const name = row.getAttribute('data-name');
                const doc = row.getAttribute('data-doc');
                const visible = name.includes(searchText) || doc.includes(searchText);
                row.style.display = visible ? '' : 'none';
                
                if (visible) {
                    // Find the parent file section
                    const fileSection = row.closest('.file-section');
                    if (fileSection) {
                        visibleFiles.add(fileSection.id);
                        // Make sure the section is expanded
                        const filePath = fileSection.id.replace('file-', '');
                        const tableContainer = document.getElementById(`section-${filePath}`);
                        if (tableContainer) {
                            tableContainer.style.display = 'block';
                        }
                    }
                }
            });
            
            // Hide file sections with no visible parameters
            const fileSections = document.querySelectorAll('.file-section');
            fileSections.forEach(section => {
                section.style.display = visibleFiles.has(section.id) || searchText === '' ? '' : 'none';
            });
        }
        
        // Toggle a file section
        function toggleSection(filePath) {
            const section = document.getElementById(`section-${filePath}`);
            if (section) {
                const isVisible = section.style.display !== 'none';
                section.style.display = isVisible ? 'none' : 'block';
                
                if (isVisible) {
                    expandedSections.delete(decodeURIComponent(filePath));
                } else {
                    expandedSections.add(decodeURIComponent(filePath));
                }
            }
        }
        
        // Toggle all file sections
        function toggleAllSections() {
            const allSections = document.querySelectorAll('[id^="section-"]');
            const allExpanded = Array.from(allSections).every(s => s.style.display !== 'none');
            
            allSections.forEach(section => {
                section.style.display = allExpanded ? 'none' : 'block';
                const filePath = section.id.replace('section-', '');
                if (allExpanded) {
                    expandedSections.delete(decodeURIComponent(filePath));
                } else {
                    expandedSections.add(decodeURIComponent(filePath));
                }
            });
        }
        
        // Tab navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                // Update active tab
                document.querySelectorAll('.nav-item').forEach(navItem => {
                    navItem.classList.remove('active');
                });
                item.classList.add('active');
                
                // Show associated content
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(item.getAttribute('data-tab')).classList.add('active');
            });
        });
        
        // Save parameter changes
        function saveParameters() {
            const changedInputs = document.querySelectorAll('.parameter-value-input');
            const changes = [];
            
            changedInputs.forEach(input => {
                const originalValue = input.getAttribute('data-original');
                const currentValue = input.value;
                
                if (originalValue !== currentValue) {
                    changes.push({
                        name: input.getAttribute('data-param-name'),
                        file_path: input.getAttribute('data-file-path'),
                        old_value: originalValue,
                        new_value: currentValue
                    });
                }
            });
            
            if (changes.length === 0) {
                alert("No changes to save.");
                return;
            }
            
            // In a real application, this would send the changes to a backend
            // For this demo, we'll just show what would be saved
            console.log("Changes to save:", changes);
            alert(`Would save ${changes.length} parameter changes. Check the console for details.`);
            
            // Here you would typically send these changes to a server endpoint
            // that would update the actual files in the codebase
        }
        
        // Load data when page loads
        window.addEventListener('DOMContentLoaded', loadParameterData);
    </script>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == "__main__":
    main() 