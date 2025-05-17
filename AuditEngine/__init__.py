"""
AuditEngine - Comprehensive Code Audit and Analysis System

This package provides automated tools for conducting comprehensive code audits,
including repository analysis, dependency mapping, metrics collection, and
report generation.
"""

__version__ = "1.0.0"
__author__ = "Ultra AI Team"

from .discovery.dependency_mapper import DependencyMapper
from .discovery.metrics_collector import MetricsCollector
from .discovery.orchestrator import DiscoveryOrchestrator
from .discovery.repository_scanner import RepositoryScanner

__all__ = [
    "DiscoveryOrchestrator",
    "RepositoryScanner",
    "DependencyMapper",
    "MetricsCollector",
]
