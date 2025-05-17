# Discovery Phase - Comprehensive Audit Report

This module implements the discovery phase of the comprehensive audit report system. It provides automated tools for analyzing repository structure, dependencies, and metrics.

## Components

### 1. Repository Scanner

- Analyzes git repository metadata
- Maps file structure and organization
- Detects language composition
- Identifies architectural patterns

### 2. Dependency Mapper

- Parses dependency files (requirements.txt, package.json, etc.)
- Identifies outdated packages
- Checks for security vulnerabilities
- Creates dependency trees

### 3. Metrics Collector

- Collects code metrics (LOC, complexity)
- Analyzes contributor activity
- Tracks commit patterns
- Evaluates project health indicators

### 4. Discovery Orchestrator

- Coordinates all discovery components
- Generates comprehensive reports
- Identifies risks and provides recommendations

## Usage

### Command Line Interface

```bash
# Run complete discovery phase
python -m AuditEngine.discovery.orchestrator /path/to/repository

# Run with verbose output
python -m AuditEngine.discovery.orchestrator /path/to/repository -v

# Specify output directory
python -m AuditEngine.discovery.orchestrator /path/to/repository -o /path/to/output
```

### Individual Components

```bash
# Run repository scanner only
python -m AuditEngine.discovery.repository_scanner /path/to/repository

# Run dependency mapper only
python -m AuditEngine.discovery.dependency_mapper /path/to/repository

# Run metrics collector only
python -m AuditEngine.discovery.metrics_collector /path/to/repository
```

### Python API

```python
from AuditEngine.discovery import DiscoveryOrchestrator

# Run complete discovery
orchestrator = DiscoveryOrchestrator("/path/to/repository")
results = orchestrator.run_discovery()

# Access individual components
from AuditEngine.discovery import RepositoryScanner, DependencyMapper, MetricsCollector

scanner = RepositoryScanner("/path/to/repository")
scan_results = scanner.scan()

mapper = DependencyMapper("/path/to/repository")
dependency_results = mapper.analyze()

collector = MetricsCollector("/path/to/repository")
metrics_results = collector.collect()
```

## Output Format

The discovery phase generates JSON reports with the following structure:

```json
{
  "discovery_metadata": {
    "repository_path": "/path/to/repo",
    "start_time": "2024-01-01T00:00:00",
    "end_time": "2024-01-01T00:05:00",
    "duration_seconds": 300,
    "phase": "discovery",
    "version": "1.0.0"
  },
  "repository_scan": {
    "metadata": { ... },
    "file_structure": { ... },
    "language_composition": { ... },
    "directory_analysis": { ... }
  },
  "dependency_analysis": {
    "python": { ... },
    "javascript": { ... },
    "summary": { ... }
  },
  "metrics_collection": {
    "code_metrics": { ... },
    "contributor_metrics": { ... },
    "commit_metrics": { ... },
    "activity_trends": { ... }
  },
  "summary": {
    "repository_overview": { ... },
    "key_metrics": { ... },
    "risk_indicators": [ ... ],
    "recommendations": [ ... ]
  },
  "errors": []
}
```

## Requirements

- Python 3.8+
- Git (for repository analysis)
- Optional: cloc (for enhanced code metrics)
- Optional: npm (for JavaScript dependency analysis)

## Configuration

No configuration required. The discovery phase automatically detects and analyzes:

- Git repositories
- Python projects (requirements.txt, Pipfile, pyproject.toml)
- JavaScript/TypeScript projects (package.json)
- Multiple programming languages

## Error Handling

The discovery phase is designed to be resilient:

- Continues even if individual components fail
- Collects and reports all errors
- Provides partial results when possible
- Logs detailed error information

## Next Steps

After running the discovery phase, use the results to:

1. Generate the comprehensive audit report
2. Create dependency visualizations
3. Build quality dashboards
4. Plan refactoring initiatives
5. Implement security improvements
