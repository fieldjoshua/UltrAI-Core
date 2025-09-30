#!/usr/bin/env python3
"""
Generate comprehensive test inventory with descriptions and categories.

Usage:
    python scripts/generate_test_inventory.py
"""

import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class TestInventoryGenerator:
    def __init__(self, test_root: Path):
        self.test_root = test_root
        self.inventory = []
        
    def extract_test_info(self, file_path: Path) -> List[Dict]:
        """Extract test functions and their docstrings from a Python file."""
        tests = []
        
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Handle test functions
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    description = ast.get_docstring(node) or self._infer_description(node.name)
                    params = self._extract_parameters(node)
                    tests.append({
                        'name': node.name,
                        'description': description.split('\n')[0][:100],  # First line, max 100 chars
                        'parameters': params,
                        'is_async': any(isinstance(d, ast.Name) and d.id == 'asyncio' 
                                      for d in node.decorator_list),
                        'markers': self._extract_markers(node)
                    })
                
                # Handle test classes
                elif isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                            description = ast.get_docstring(item) or self._infer_description(item.name)
                            params = self._extract_parameters(item)
                            tests.append({
                                'name': f"{node.name}::{item.name}",
                                'description': description.split('\n')[0][:100],
                                'parameters': params,
                                'is_async': any(isinstance(d, ast.Name) and d.id == 'asyncio' 
                                              for d in item.decorator_list),
                                'markers': self._extract_markers(item)
                            })
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
        
        return tests
    
    def _infer_description(self, test_name: str) -> str:
        """Infer description from test name."""
        # Remove 'test_' prefix
        name = test_name.replace('test_', '')
        # Replace underscores with spaces
        name = name.replace('_', ' ')
        # Capitalize first letter
        return name.capitalize()
    
    def _extract_markers(self, node: ast.FunctionDef) -> List[str]:
        """Extract pytest markers from decorators."""
        markers = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if isinstance(decorator.value, ast.Attribute):
                    # Handle pytest.mark.asyncio
                    if (isinstance(decorator.value.value, ast.Name) and 
                        decorator.value.value.id == 'pytest' and 
                        decorator.value.attr == 'mark'):
                        markers.append(decorator.attr)
        return markers
    
    def _extract_parameters(self, node: ast.FunctionDef) -> str:
        """Extract and describe test parameters/fixtures."""
        params = []
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            # Infer purpose from fixture name
            param_desc = self._infer_parameter_purpose(arg.arg)
            if param_desc:
                params.append(param_desc)
        
        return ', '.join(params) if params else 'None'
    
    def _infer_parameter_purpose(self, param_name: str) -> str:
        """Infer parameter purpose from common fixture names."""
        param_map = {
            'client': 'HTTP client',
            'async_client': 'Async HTTP client',
            'db': 'Database connection',
            'session': 'Database session',
            'mock_llm': 'Mocked LLM',
            'mock_': 'Mocked ',
            'orchestrator': 'Orchestrator service',
            'cache': 'Cache service',
            'redis': 'Redis connection',
            'user': 'Test user',
            'auth': 'Auth service',
            'rate_limiter': 'Rate limiter',
            'api_key': 'API key',
            'token': 'Auth token',
            'monkeypatch': 'Monkeypatch fixture',
            'capsys': 'Stdout capture',
            'tmpdir': 'Temp directory',
            'tmp_path': 'Temp path',
            'env': 'Environment vars',
        }
        
        # Check for exact matches first
        if param_name in param_map:
            return param_map[param_name]
        
        # Check for prefix matches
        for prefix, desc in param_map.items():
            if param_name.startswith(prefix):
                return desc + param_name[len(prefix):].replace('_', ' ')
        
        # Return cleaned parameter name
        return param_name.replace('_', ' ')
    
    def categorize_test(self, file_path: Path) -> str:
        """Determine test category from file path."""
        parts = file_path.relative_to(self.test_root).parts
        
        if 'unit' in parts:
            return 'Unit'
        elif 'integration' in parts:
            return 'Integration'
        elif 'e2e' in parts:
            return 'E2E'
        elif 'live' in parts:
            return 'Live'
        elif 'production' in parts:
            return 'Production'
        else:
            return 'Core'
    
    def get_module_focus(self, file_path: Path) -> str:
        """Determine module focus from file path and name."""
        name = file_path.stem.lower()
        path_str = str(file_path).lower()
        
        # Core synthesis functionality
        if 'orchestrat' in name or 'synthesis' in name or 'pipeline' in name:
            return '1. Core Synthesis'
        
        # LLM provider integrations
        elif 'llm' in name or 'adapter' in name or 'provider' in name:
            return '2. LLM Providers'
        
        # Authentication & authorization
        elif 'auth' in name or 'oauth' in name or 'jwt' in name:
            return '3. Authentication'
        
        # Financial & billing
        elif any(x in name for x in ['transaction', 'billing', 'budget', 'payment', 'financial']):
            return '4. Financial'
        
        # Rate limiting & throttling
        elif 'rate' in name and 'limit' in name:
            return '5. Rate Limiting'
        
        # Caching layer
        elif 'cache' in name or 'redis' in name:
            return '6. Caching'
        
        # Health monitoring
        elif 'health' in name or 'monitoring' in name:
            return '7. Health & Monitoring'
        
        # Prompt engineering
        elif 'prompt' in name or 'template' in name:
            return '8. Prompts & Templates'
        
        # Quality & evaluation
        elif 'quality' in name or 'evaluation' in name or 'rating' in name:
            return '9. Quality Evaluation'
        
        # Token & usage tracking
        elif 'token' in name and 'management' in name:
            return '10. Token Management'
        
        # Model registry & configuration
        elif 'model' in name and ('registry' in name or 'config' in name):
            return '11. Model Registry'
        
        # Document & content management
        elif 'document' in name or 'content' in name or 'file' in name:
            return '12. Documents'
        
        # Analysis features
        elif 'analysis' in name or 'pattern' in name:
            return '13. Analysis'
        
        # API endpoints & routes
        elif 'endpoint' in name or 'route' in name or 'api' in name:
            return '14. API Endpoints'
        
        # Streaming & SSE
        elif 'stream' in name or 'sse' in name:
            return '15. Streaming'
        
        # Configuration & system
        elif 'config' in name or 'system' in name or 'service' in name:
            return '16. Configuration'
        
        # Database operations
        elif 'database' in name or 'db' in name or 'repository' in name:
            return '17. Database'
        
        # UI & frontend tests
        elif 'ui' in name or 'web' in name or 'playwright' in name or 'browser' in name:
            return '18. UI/Frontend'
        
        # Network & connectivity
        elif 'network' in name or 'connection' in name:
            return '19. Network'
        
        # Fallback & error handling
        elif 'fallback' in name or 'failure' in name or 'error' in name:
            return '20. Error Handling'
        
        else:
            return '21. Miscellaneous'
    
    def generate_inventory(self) -> List[Dict]:
        """Generate complete test inventory."""
        test_files = sorted(self.test_root.rglob('test_*.py'))
        
        for test_file in test_files:
            tests = self.extract_test_info(test_file)
            category = self.categorize_test(test_file)
            module = self.get_module_focus(test_file)
            
            relative_path = test_file.relative_to(self.test_root)
            
            for test in tests:
                self.inventory.append({
                    'file': str(relative_path),
                    'category': category,
                    'module': module,
                    'test_name': test['name'],
                    'description': test['description'],
                    'parameters': test['parameters'],
                    'markers': ', '.join(test['markers']) if test['markers'] else 'none',
                    'async': 'Yes' if test['is_async'] else 'No'
                })
        
        return self.inventory
    
    def generate_markdown_table(self, output_file: Path):
        """Generate markdown table from inventory."""
        inventory = self.generate_inventory()
        
        with output_file.open('w') as f:
            f.write('# UltraAI Test Suite Inventory\n\n')
            f.write(f'**Total Tests:** {len(inventory)}\n\n')
            f.write(f'**Generated:** {subprocess.run(["date"], capture_output=True, text=True).stdout.strip()}\n\n')
            
            # Summary statistics
            category_counts = defaultdict(int)
            module_counts = defaultdict(int)
            for item in inventory:
                category_counts[item['category']] += 1
                module_counts[item['module']] += 1
            
            f.write('## Summary\n\n')
            f.write(f'| Category | Count |\n')
            f.write(f'|----------|-------|\n')
            for category in sorted(category_counts.keys()):
                f.write(f'| {category} | {category_counts[category]} |\n')
            f.write('\n')
            
            f.write(f'| Module | Count |\n')
            f.write(f'|--------|-------|\n')
            for module in sorted(module_counts.keys()):
                f.write(f'| {module} | {module_counts[module]} |\n')
            f.write('\n')
            
            # Single comprehensive table with all tests
            f.write('## Complete Test Inventory\n\n')
            f.write('| # | Category | Module | File | Test Name | Description | Parameters/Fixtures | Markers |\n')
            f.write('|---|----------|--------|------|-----------|-------------|---------------------|----------|\n')
            
            for idx, test in enumerate(inventory, 1):
                file_short = test['file'].split('/')[-1]
                test_name = test['test_name'][:45] + '...' if len(test['test_name']) > 45 else test['test_name']
                description = test['description'][:55] + '...' if len(test['description']) > 55 else test['description']
                description = description.replace('|', '\\|')
                parameters = test['parameters'][:40] + '...' if len(test['parameters']) > 40 else test['parameters']
                parameters = parameters.replace('|', '\\|')
                markers = test['markers'].replace('|', '\\|')
                category = test['category']
                module = test['module']
                
                f.write(f'| {idx} | {category} | {module} | `{file_short}` | `{test_name}` | {description} | {parameters} | {markers} |\n')
        
        print(f'✅ Test inventory written to {output_file}')
        print(f'📊 Total tests cataloged: {len(inventory)}')


def main():
    project_root = Path(__file__).parent.parent
    test_root = project_root / 'tests'
    output_file = project_root / 'TEST_INVENTORY.md'
    
    generator = TestInventoryGenerator(test_root)
    generator.generate_markdown_table(output_file)
    
    return 0


if __name__ == '__main__':
    exit(main())