"""
Example usage of the prompt templates system with UltrAI improvement actions.
"""

from .session_manager import SessionManager
from .actions import create_action


def main():
    """Run the example."""
    # Initialize session manager
    session_manager = SessionManager()

    # Create a new session
    session = session_manager.create_session(branch="main")
    print(f"Created session: {session.session_id}")

    # Prioritized Timeline Plan
    timeline_plan = create_action(
        "analysis",
        analysis_type="Prioritized Timeline",
        description="Sequential implementation timeline for all improvement plans",
        metadata={
            "total_duration": "32 weeks",
            "timeline": [
                {
                    "phase": "1. System Architecture Enhancement",
                    "duration": "8 weeks",
                    "priority": "Critical",
                    "rationale": "Foundation for all other improvements",
                    "key_deliverables": [
                        "Error handling system",
                        "Performance monitoring",
                        "Security enhancements",
                        "Architecture documentation",
                    ],
                    "dependencies": "None",
                    "estimated_start": "Week 1",
                    "estimated_end": "Week 8",
                },
                {
                    "phase": "2. Security Enhancement",
                    "duration": "6 weeks",
                    "priority": "High",
                    "rationale": "Critical for system reliability and trust",
                    "key_deliverables": [
                        "Rate limiting implementation",
                        "Security headers",
                        "Input validation",
                        "Security documentation",
                    ],
                    "dependencies": "System Architecture Phase 3",
                    "estimated_start": "Week 9",
                    "estimated_end": "Week 14",
                },
                {
                    "phase": "3. Performance Optimization",
                    "duration": "6 weeks",
                    "priority": "High",
                    "rationale": "Builds on monitoring to improve system efficiency",
                    "key_deliverables": [
                        "Caching implementation",
                        "Database optimization",
                        "Performance monitoring",
                        "Performance documentation",
                    ],
                    "dependencies": "System Architecture Phase 2",
                    "estimated_start": "Week 15",
                    "estimated_end": "Week 20",
                },
                {
                    "phase": "4. Testing Enhancement",
                    "duration": "4 weeks",
                    "priority": "High",
                    "rationale": "Ensures reliability of previous improvements",
                    "key_deliverables": [
                        "Increased test coverage",
                        "Integration tests",
                        "Performance tests",
                        "Security tests",
                    ],
                    "dependencies": "All previous phases",
                    "estimated_start": "Week 21",
                    "estimated_end": "Week 24",
                },
                {
                    "phase": "5. Documentation Completion",
                    "duration": "4 weeks",
                    "priority": "Medium",
                    "rationale": "Documents all improvements for future reference",
                    "key_deliverables": [
                        "API documentation",
                        "Architecture documentation",
                        "Development guide",
                        "Deployment guide",
                    ],
                    "dependencies": "All previous phases",
                    "estimated_start": "Week 25",
                    "estimated_end": "Week 28",
                },
                {
                    "phase": "6. Deployment Enhancement",
                    "duration": "4 weeks",
                    "priority": "Medium",
                    "rationale": "Final phase to ensure smooth deployment",
                    "key_deliverables": [
                        "Staging environment",
                        "Monitoring improvements",
                        "Rollback process",
                        "Deployment documentation",
                    ],
                    "dependencies": "All previous phases",
                    "estimated_start": "Week 29",
                    "estimated_end": "Week 32",
                },
            ],
            "critical_path": [
                "System Architecture → Security → Performance → Testing → Documentation → Deployment"
            ],
            "resource_allocation": {
                "development_team": "Full-time",
                "qa_team": "Part-time during testing phase",
                "documentation_team": "Part-time throughout, full-time during documentation phase",
            },
            "risk_mitigation": {
                "early_phases": "Focus on core functionality first",
                "middle_phases": "Regular testing and validation",
                "late_phases": "Comprehensive documentation and review",
            },
            "success_metrics": [
                "All critical and high-priority improvements completed",
                "Test coverage above 80%",
                "Documentation complete and reviewed",
                "Deployment process verified",
            ],
        },
    )
    session.add_action(timeline_plan)
    print("Added prioritized timeline plan")

    # 1. System Architecture Implementation Plan
    system_plan = create_action(
        "analysis",
        analysis_type="Implementation Plan",
        description="Detailed implementation plan for system architecture improvements",
        metadata={
            "plan_name": "System Architecture Enhancement",
            "duration": "8 weeks",
            "phases": [
                {
                    "name": "Phase 1: Error Handling Enhancement",
                    "duration": "2 weeks",
                    "tasks": [
                        {
                            "name": "Implement Global Error Handler",
                            "description": "Create centralized error handling system",
                            "components": ["core", "api", "frontend"],
                            "priority": "High",
                            "estimated_hours": 16,
                        },
                        {
                            "name": "Add Error Logging",
                            "description": "Implement structured error logging",
                            "components": ["core", "monitoring"],
                            "priority": "High",
                            "estimated_hours": 12,
                        },
                        {
                            "name": "Create Error Recovery System",
                            "description": "Implement automatic error recovery mechanisms",
                            "components": ["core", "api"],
                            "priority": "Medium",
                            "estimated_hours": 20,
                        },
                    ],
                },
                {
                    "name": "Phase 2: Performance Monitoring",
                    "duration": "2 weeks",
                    "tasks": [
                        {
                            "name": "Implement Metrics Collection",
                            "description": "Add system-wide metrics collection",
                            "components": ["monitoring", "core"],
                            "priority": "High",
                            "estimated_hours": 24,
                        },
                        {
                            "name": "Create Performance Dashboard",
                            "description": "Build real-time performance monitoring dashboard",
                            "components": ["frontend", "monitoring"],
                            "priority": "Medium",
                            "estimated_hours": 16,
                        },
                        {
                            "name": "Add Alerting System",
                            "description": "Implement performance-based alerting",
                            "components": ["monitoring", "api"],
                            "priority": "Medium",
                            "estimated_hours": 12,
                        },
                    ],
                },
                {
                    "name": "Phase 3: Security Enhancement",
                    "duration": "2 weeks",
                    "tasks": [
                        {
                            "name": "Implement Rate Limiting",
                            "description": "Add rate limiting to all API endpoints",
                            "components": ["api", "security"],
                            "priority": "High",
                            "estimated_hours": 16,
                        },
                        {
                            "name": "Add Security Headers",
                            "description": "Implement security headers and CORS policies",
                            "components": ["api", "frontend"],
                            "priority": "High",
                            "estimated_hours": 8,
                        },
                        {
                            "name": "Enhance Input Validation",
                            "description": "Implement comprehensive input validation",
                            "components": ["api", "core"],
                            "priority": "High",
                            "estimated_hours": 20,
                        },
                    ],
                },
                {
                    "name": "Phase 4: Documentation",
                    "duration": "2 weeks",
                    "tasks": [
                        {
                            "name": "Create Architecture Documentation",
                            "description": "Document system architecture and components",
                            "components": ["documentation"],
                            "priority": "High",
                            "estimated_hours": 24,
                        },
                        {
                            "name": "Add API Documentation",
                            "description": "Create comprehensive API documentation",
                            "components": ["documentation", "api"],
                            "priority": "High",
                            "estimated_hours": 20,
                        },
                        {
                            "name": "Create Development Guide",
                            "description": "Write development and contribution guidelines",
                            "components": ["documentation"],
                            "priority": "Medium",
                            "estimated_hours": 16,
                        },
                    ],
                },
            ],
            "dependencies": [
                "Error handling must be implemented before performance monitoring",
                "Security enhancements can be done in parallel with documentation",
                "All phases require testing and review",
            ],
            "success_criteria": [
                "All error handling improvements implemented and tested",
                "Performance monitoring system operational",
                "Security enhancements completed and verified",
                "Documentation complete and reviewed",
            ],
            "risks": [
                "Potential performance impact during monitoring implementation",
                "Security changes may affect existing functionality",
                "Documentation may need updates as system evolves",
            ],
            "mitigation_strategies": [
                "Implement changes in staging environment first",
                "Create comprehensive test suite",
                "Regular review and update of documentation",
            ],
        },
    )
    session.add_action(system_plan)
    print("Added system architecture implementation plan")

    # 2. Code Quality Actions
    code_quality = create_action(
        "analysis",
        analysis_type="Code Quality",
        description="Reviewed code quality and standards",
        metadata={
            "tools_used": ["flake8", "pylint", "pre-commit", "eslint", "prettier"],
            "findings": [
                "Good linting configuration",
                "Consistent code style",
                "Type hints used",
                "Comprehensive test coverage",
            ],
            "improvements": [
                "Add more type hints",
                "Increase test coverage",
                "Standardize error handling",
                "Improve documentation",
            ],
        },
    )
    session.add_action(code_quality)
    print("Added code quality action")

    # 3. Documentation Actions
    doc_improvement = create_action(
        "analysis",
        analysis_type="Documentation",
        description="Reviewed and planned documentation improvements",
        metadata={
            "current_docs": [
                "README.md",
                "documentation/cloud_deployment.md",
                "documentation/archive/NEWArchive/README.md",
            ],
            "needed_docs": [
                "API Documentation",
                "Architecture Overview",
                "Development Guide",
                "Deployment Guide",
                "Security Guidelines",
            ],
            "priority": "High",
        },
    )
    session.add_action(doc_improvement)
    print("Added documentation action")

    # 4. Security Actions
    security_audit = create_action(
        "analysis",
        analysis_type="Security",
        description="Conducted security audit",
        metadata={
            "areas_checked": [
                "Authentication",
                "Authorization",
                "Data Protection",
                "API Security",
                "Dependency Management",
            ],
            "findings": [
                "Good basic security measures",
                "Proper dependency management",
                "Secure API design",
            ],
            "improvements": [
                "Implement rate limiting",
                "Add security headers",
                "Enhance input validation",
                "Improve error handling",
            ],
        },
    )
    session.add_action(security_audit)
    print("Added security audit action")

    # 5. Performance Actions
    performance_analysis = create_action(
        "analysis",
        analysis_type="Performance",
        description="Analyzed system performance",
        metadata={
            "metrics": [
                "Response Time",
                "Memory Usage",
                "CPU Utilization",
                "Database Performance",
            ],
            "findings": [
                "Good overall performance",
                "Efficient resource usage",
                "Scalable architecture",
            ],
            "optimizations": [
                "Implement caching",
                "Optimize database queries",
                "Add performance monitoring",
                "Improve error handling",
            ],
        },
    )
    session.add_action(performance_analysis)
    print("Added performance analysis action")

    # 6. Testing Actions
    testing_improvement = create_action(
        "analysis",
        analysis_type="Testing",
        description="Reviewed testing strategy",
        metadata={
            "test_types": [
                "Unit Tests",
                "Integration Tests",
                "End-to-End Tests",
                "Performance Tests",
            ],
            "coverage": {"unit": "80%", "integration": "60%", "e2e": "40%"},
            "improvements": [
                "Increase test coverage",
                "Add more integration tests",
                "Implement performance tests",
                "Add security tests",
            ],
        },
    )
    session.add_action(testing_improvement)
    print("Added testing improvement action")

    # 7. Deployment Actions
    deployment_analysis = create_action(
        "analysis",
        analysis_type="Deployment",
        description="Analyzed deployment process",
        metadata={
            "current_setup": ["Docker", "Vercel", "GitHub Actions"],
            "findings": [
                "Good containerization",
                "Automated CI/CD",
                "Cloud deployment ready",
            ],
            "improvements": [
                "Add staging environment",
                "Improve monitoring",
                "Enhance rollback process",
                "Add deployment documentation",
            ],
        },
    )
    session.add_action(deployment_analysis)
    print("Added deployment analysis action")

    # Update the session
    session_manager.update_session(session)
    print("Updated session with actions")

    # Display session information
    print("\nSession Information:")
    print(f"Session ID: {session.session_id}")
    print(f"Branch: {session.branch}")
    print(f"Current Action: {session.current_action}")
    print(f"Created: {session.created_at}")
    print(f"Updated: {session.updated_at}")

    print("\nAction History:")
    for action in session.action_history:
        print(f"\nAction: {action.name}")
        print(f"Description: {action.description}")
        print(f"Timestamp: {action.timestamp}")
        print(f"Metadata: {action.metadata}")


if __name__ == "__main__":
    main()
