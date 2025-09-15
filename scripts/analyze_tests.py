#!/usr/bin/env python3
"""
Analyze test suite for consolidation opportunities.
"""

import os
import re
import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class TestAnalyzer:
    """Analyze test files for patterns and duplicates."""
    
    def __init__(self, test_dir: str):
        self.test_dir = Path(test_dir)
        self.test_files = []
        self.test_data = defaultdict(dict)
        
    def find_test_files(self) -> List[Path]:
        """Find all test files."""
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(self.test_dir.rglob(pattern))
        return sorted(test_files)
    
    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single test file."""
        with open(filepath, 'r') as f:
            content = f.read()
            
        analysis = {
            'path': str(filepath),
            'category': self._get_category(filepath),
            'imports': self._extract_imports(content),
            'test_functions': self._extract_test_functions(content),
            'mocked_items': self._extract_mocks(content),
            'assertions': self._count_assertions(content),
            'line_count': len(content.splitlines()),
            'has_fixtures': 'pytest.fixture' in content or '@fixture' in content,
            'uses_mock': 'mock' in content.lower() or '@patch' in content,
            'api_calls': self._find_api_calls(content),
            'tested_modules': self._find_tested_modules(content),
        }
        
        return analysis
    
    def _get_category(self, filepath: Path) -> str:
        """Determine test category from path."""
        parts = filepath.parts
        if 'unit' in parts:
            return 'unit'
        elif 'integration' in parts:
            return 'integration'
        elif 'e2e' in parts:
            return 'e2e'
        elif 'live' in parts:
            return 'live'
        elif 'production' in parts:
            return 'production'
        else:
            return 'unknown'
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = []
        for line in content.splitlines():
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        return imports
    
    def _extract_test_functions(self, content: str) -> List[Dict]:
        """Extract test function names and details."""
        test_funcs = []
        pattern = r'(async\s+)?def\s+(test_\w+)\s*\([^)]*\):'
        
        for match in re.finditer(pattern, content):
            is_async = bool(match.group(1))
            func_name = match.group(2)
            
            # Extract docstring if present
            func_start = match.end()
            docstring = self._extract_docstring(content[func_start:])
            
            test_funcs.append({
                'name': func_name,
                'async': is_async,
                'docstring': docstring,
            })
        
        return test_funcs
    
    def _extract_docstring(self, content: str) -> str:
        """Extract docstring from function body."""
        lines = content.strip().splitlines()
        if not lines:
            return ""
            
        first_line = lines[0].strip()
        if first_line.startswith(('"""', "'''")):
            quote = first_line[:3]
            if first_line.endswith(quote) and len(first_line) > 6:
                return first_line[3:-3]
            else:
                for i, line in enumerate(lines[1:], 1):
                    if quote in line:
                        return '\n'.join(lines[0:i+1]).strip(quote)
        return ""
    
    def _extract_mocks(self, content: str) -> List[str]:
        """Extract mocked items."""
        mocks = []
        
        # @patch decorators
        patch_pattern = r'@patch\([\'"]([^\'")]+)[\'"]\)'
        mocks.extend(re.findall(patch_pattern, content))
        
        # Mock assignments
        mock_pattern = r'(\w+)\s*=\s*Mock\('
        mocks.extend(re.findall(mock_pattern, content))
        
        # unittest.mock usage
        mock_pattern2 = r'mock\.Mock\(\)'
        if re.search(mock_pattern2, content):
            mocks.append('generic_mock')
            
        return list(set(mocks))
    
    def _count_assertions(self, content: str) -> Dict[str, int]:
        """Count different types of assertions."""
        assertions = {
            'assertEqual': len(re.findall(r'assertEqual\s*\(', content)),
            'assertTrue': len(re.findall(r'assertTrue\s*\(', content)),
            'assertFalse': len(re.findall(r'assertFalse\s*\(', content)),
            'assertIn': len(re.findall(r'assertIn\s*\(', content)),
            'assertIsNone': len(re.findall(r'assertIsNone\s*\(', content)),
            'assertIsNotNone': len(re.findall(r'assertIsNotNone\s*\(', content)),
            'assert': len(re.findall(r'assert\s+[^=]', content)),
            'pytest_raises': len(re.findall(r'pytest\.raises\s*\(', content)),
            'with_raises': len(re.findall(r'with\s+raises\s*\(', content)),
        }
        
        # Remove overlaps (assert might count assertEqual etc)
        if assertions['assert'] > 0:
            assertions['assert'] -= sum(v for k, v in assertions.items() if k != 'assert')
            
        return assertions
    
    def _find_api_calls(self, content: str) -> List[str]:
        """Find API endpoint calls."""
        endpoints = []
        
        # Common test client patterns
        patterns = [
            r'client\.(get|post|put|delete|patch)\s*\([\'"]([^\'")]+)[\'"]',
            r'test_client\.(get|post|put|delete|patch)\s*\([\'"]([^\'")]+)[\'"]',
            r'self\.client\.(get|post|put|delete|patch)\s*\([\'"]([^\'")]+)[\'"]',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                endpoints.append(f"{match.group(1).upper()} {match.group(2)}")
                
        return list(set(endpoints))
    
    def _find_tested_modules(self, content: str) -> List[str]:
        """Find which modules are being tested."""
        modules = []
        
        # Look for imports from app modules
        import_pattern = r'from\s+app\.(\S+)\s+import'
        modules.extend(re.findall(import_pattern, content))
        
        # Look for direct imports
        import_pattern2 = r'import\s+app\.(\S+)'
        modules.extend(re.findall(import_pattern2, content))
        
        return list(set(modules))
    
    def find_duplicates(self, analyses: List[Dict]) -> Dict[str, List[Dict]]:
        """Find potential duplicate tests."""
        duplicates = defaultdict(list)
        
        # Group by tested modules
        by_module = defaultdict(list)
        for analysis in analyses:
            for module in analysis['tested_modules']:
                by_module[module].append(analysis)
        
        # Find modules tested in multiple files
        for module, tests in by_module.items():
            if len(tests) > 1:
                duplicates[f"module_{module}"] = tests
        
        # Group by API endpoints
        by_endpoint = defaultdict(list)
        for analysis in analyses:
            for endpoint in analysis['api_calls']:
                by_endpoint[endpoint].append(analysis)
        
        # Find endpoints tested in multiple files
        for endpoint, tests in by_endpoint.items():
            if len(tests) > 1:
                duplicates[f"endpoint_{endpoint}"] = tests
                
        return dict(duplicates)
    
    def find_weak_tests(self, analyses: List[Dict]) -> List[Dict]:
        """Find tests with weak or no assertions."""
        weak_tests = []
        
        for analysis in analyses:
            total_assertions = sum(analysis['assertions'].values())
            test_count = len(analysis['test_functions'])
            
            if test_count > 0:
                avg_assertions = total_assertions / test_count
                
                # Flag tests with low assertion count
                if avg_assertions < 1.5:
                    weak_tests.append({
                        'file': analysis['path'],
                        'test_count': test_count,
                        'total_assertions': total_assertions,
                        'avg_assertions': avg_assertions,
                        'reason': 'low_assertions'
                    })
                    
            # Flag tests with no assertions
            if total_assertions == 0 and test_count > 0:
                weak_tests.append({
                    'file': analysis['path'],
                    'test_count': test_count,
                    'reason': 'no_assertions'
                })
                
        return weak_tests
    
    def generate_report(self) -> str:
        """Generate analysis report."""
        test_files = self.find_test_files()
        analyses = []
        
        for filepath in test_files:
            try:
                analysis = self.analyze_file(filepath)
                analyses.append(analysis)
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
                
        # Generate report
        report = ["# Test Suite Analysis Report\n"]
        report.append(f"Total test files: {len(test_files)}\n")
        
        # Category breakdown
        by_category = defaultdict(list)
        for analysis in analyses:
            by_category[analysis['category']].append(analysis)
            
        report.append("## Test Categories\n")
        for category, tests in sorted(by_category.items()):
            report.append(f"- {category}: {len(tests)} files")
            
        # Find duplicates
        duplicates = self.find_duplicates(analyses)
        report.append(f"\n## Potential Duplicates\n")
        report.append(f"Found {len(duplicates)} potential duplicate groups:\n")
        
        for dup_type, tests in list(duplicates.items())[:10]:  # Show top 10
            report.append(f"\n### {dup_type}")
            for test in tests:
                report.append(f"- {test['path']}")
                
        # Find weak tests
        weak_tests = self.find_weak_tests(analyses)
        report.append(f"\n## Weak Tests\n")
        report.append(f"Found {len(weak_tests)} tests with weak assertions:\n")
        
        for weak in weak_tests[:10]:  # Show top 10
            report.append(f"- {weak['file']} ({weak['reason']})")
            
        # Mock usage
        report.append("\n## Mock Usage\n")
        mock_count = sum(1 for a in analyses if a['uses_mock'])
        report.append(f"- {mock_count}/{len(analyses)} files use mocks")
        
        # Heavy mocking
        heavy_mocks = [a for a in analyses if len(a['mocked_items']) > 5]
        if heavy_mocks:
            report.append(f"\n### Heavy Mock Usage ({len(heavy_mocks)} files)")
            for analysis in heavy_mocks[:5]:
                report.append(f"- {analysis['path']}: {len(analysis['mocked_items'])} mocks")
                
        return '\n'.join(report)


if __name__ == "__main__":
    analyzer = TestAnalyzer("/Users/joshuafield/Documents/Ultra/tests")
    report = analyzer.generate_report()
    print(report)
    
    # Save report
    with open("/Users/joshuafield/Documents/Ultra/TEST_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)