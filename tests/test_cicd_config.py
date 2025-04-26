import pytest
import os
import yaml
from pathlib import Path


def test_github_workflow():
    # Test GitHub workflow
    workflow_dir = Path(".github/workflows")
    assert workflow_dir.exists()

    # Test main workflow
    main_workflow = workflow_dir / "main.yml"
    assert main_workflow.exists()

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)

        # Verify workflow configuration
        assert "name" in workflow
        assert "on" in workflow
        assert "jobs" in workflow

        # Verify trigger events
        assert "push" in workflow["on"]
        assert "pull_request" in workflow["on"]

        # Verify jobs
        assert "test" in workflow["jobs"]
        assert "lint" in workflow["jobs"]
        assert "build" in workflow["jobs"]
        assert "deploy" in workflow["jobs"]


def test_test_job():
    # Test test job
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)
        test_job = workflow["jobs"]["test"]

        # Verify test job configuration
        assert test_job["runs-on"] == "ubuntu-latest"
        assert "steps" in test_job

        # Verify test steps
        steps = test_job["steps"]
        assert any("actions/checkout" in step["uses"] for step in steps)
        assert any("actions/setup-python" in step["uses"] for step in steps)
        assert any("pip install -r requirements.txt" in step["run"] for step in steps)
        assert any("pytest" in step["run"] for step in steps)


def test_lint_job():
    # Test lint job
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)
        lint_job = workflow["jobs"]["lint"]

        # Verify lint job configuration
        assert lint_job["runs-on"] == "ubuntu-latest"
        assert "steps" in lint_job

        # Verify lint steps
        steps = lint_job["steps"]
        assert any("actions/checkout" in step["uses"] for step in steps)
        assert any("actions/setup-python" in step["uses"] for step in steps)
        assert any(
            "pip install -r requirements-dev.txt" in step["run"] for step in steps
        )
        assert any("flake8" in step["run"] for step in steps)
        assert any("mypy" in step["run"] for step in steps)
        assert any("black" in step["run"] for step in steps)


def test_build_job():
    # Test build job
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)
        build_job = workflow["jobs"]["build"]

        # Verify build job configuration
        assert build_job["runs-on"] == "ubuntu-latest"
        assert "needs" in build_job
        assert "test" in build_job["needs"]
        assert "lint" in build_job["needs"]
        assert "steps" in build_job

        # Verify build steps
        steps = build_job["steps"]
        assert any("actions/checkout" in step["uses"] for step in steps)
        assert any("actions/setup-python" in step["uses"] for step in steps)
        assert any("docker build" in step["run"] for step in steps)
        assert any("docker push" in step["run"] for step in steps)


def test_deploy_job():
    # Test deploy job
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)
        deploy_job = workflow["jobs"]["deploy"]

        # Verify deploy job configuration
        assert deploy_job["runs-on"] == "ubuntu-latest"
        assert "needs" in deploy_job
        assert "build" in deploy_job["needs"]
        assert "if" in deploy_job
        assert "steps" in deploy_job

        # Verify deploy steps
        steps = deploy_job["steps"]
        assert any("actions/checkout" in step["uses"] for step in steps)
        assert any("actions/setup-python" in step["uses"] for step in steps)
        assert any("kubectl apply" in step["run"] for step in steps)
        assert any("kubectl rollout" in step["run"] for step in steps)


def test_environment_variables():
    # Test environment variables
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)

        # Verify environment variables
        for job in workflow["jobs"].values():
            if "env" in job:
                env = job["env"]
                assert "PYTHONPATH" in env
                assert "DATABASE_URL" in env
                assert "API_KEY" in env
                assert "LOG_LEVEL" in env


def test_artifacts():
    # Test artifacts
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)

        # Verify test artifacts
        test_job = workflow["jobs"]["test"]
        assert "artifacts" in test_job
        assert "coverage" in test_job["artifacts"]

        # Verify build artifacts
        build_job = workflow["jobs"]["build"]
        assert "artifacts" in build_job
        assert "docker-image" in build_job["artifacts"]


def test_notifications():
    # Test notifications
    workflow_dir = Path(".github/workflows")
    main_workflow = workflow_dir / "main.yml"

    with open(main_workflow, "r") as f:
        workflow = yaml.safe_load(f)

        # Verify notification configuration
        assert "notifications" in workflow
        notifications = workflow["notifications"]
        assert "email" in notifications
        assert "slack" in notifications
        assert "on_success" in notifications
        assert "on_failure" in notifications
