"""
Tests for the prompt templates module.
"""

import os
import shutil
import tempfile

import pytest

from ..models import PromptTemplate, Session
from ..template_manager import PromptTemplateManager
from ..session_manager import SessionManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def template_manager(temp_dir):
    """Create a template manager with a temporary directory."""
    return PromptTemplateManager(templates_dir=os.path.join(temp_dir, "templates"))


@pytest.fixture
def session_manager(temp_dir):
    """Create a session manager with a temporary directory."""
    return SessionManager(sessions_dir=os.path.join(temp_dir, "sessions"))


def test_create_template(template_manager):
    """Test creating a prompt template."""
    template = template_manager.create_template(
        title="Test Template",
        current_action="Initial",
        context="Test context",
        task="Test task",
        requirements=["Requirement 1", "Requirement 2"],
        expected_output="Test output",
    )

    # Verify template properties
    assert isinstance(
        template, PromptTemplate
    ), "Template should be a PromptTemplate instance"
    assert template.title == "Test Template", "Template title should match"
    assert template.current_action == "Initial", "Current action should be Initial"
    assert template.context == "Test context", "Context should match"
    assert template.task == "Test task", "Task should match"
    assert template.requirements == [
        "Requirement 1",
        "Requirement 2",
    ], "Requirements should match"
    assert template.expected_output == "Test output", "Expected output should match"

    # Check that template was saved to file
    templates = template_manager.list_templates()
    assert len(templates) == 1, "Should have one template"
    assert templates[0].startswith("prompt_"), "Template ID should start with 'prompt_'"


def test_get_template(template_manager):
    """Test retrieving a prompt template."""
    # Create a template
    template = template_manager.create_template(
        title="Test Template",
        current_action="Initial",
        context="Test context",
        task="Test task",
        requirements=["Requirement 1"],
        expected_output="Test output",
    )

    # Get the template ID
    template_id = template_manager.list_templates()[0]

    # Retrieve the template
    retrieved = template_manager.get_template(template_id)

    # Verify retrieved template
    assert retrieved is not None, "Retrieved template should not be None"
    assert retrieved.title == template.title, "Title should match"
    assert (
        retrieved.current_action == template.current_action
    ), "Current action should match"
    assert retrieved.context == template.context, "Context should match"
    assert retrieved.task == template.task, "Task should match"
    assert retrieved.requirements == template.requirements, "Requirements should match"
    assert (
        retrieved.expected_output == template.expected_output
    ), "Expected output should match"


def test_create_session(session_manager):
    """Test creating a session."""
    session = session_manager.create_session(branch="test-branch")

    # Verify session properties
    assert isinstance(session, Session), "Session should be a Session instance"
    assert session.branch == "test-branch", "Branch should match"
    assert session.current_action == "Initial", "Current action should be Initial"
    assert len(session.active_files) == 0, "Should have no active files"
    assert len(session.action_history) == 0, "Should have no action history"

    # Check that session was created
    sessions = session_manager.list_sessions()
    assert len(sessions) == 1, "Should have one session"
    assert sessions[0] == session.session_id, "Session ID should match"


def test_update_session(session_manager):
    """Test updating a session."""
    # Create a session
    session = session_manager.create_session(branch="test-branch")

    # Add an action
    session.add_action({"name": "Test Action", "description": "Test description"})

    # Update the session
    session_manager.update_session(session)

    # Retrieve the session
    retrieved = session_manager.get_session(session.session_id)

    # Verify retrieved session
    assert retrieved is not None, "Retrieved session should not be None"
    assert len(retrieved.action_history) == 1, "Should have one action"
    assert (
        retrieved.action_history[0]["name"] == "Test Action"
    ), "Action name should match"
    assert (
        retrieved.action_history[0]["description"] == "Test description"
    ), "Action description should match"


def test_session_markdown(session_manager):
    """Test session markdown generation."""
    session = session_manager.create_session(branch="test-branch")
    session.add_action({"name": "Test Action", "description": "Test description"})

    markdown = session.to_markdown()

    # Verify markdown content
    assert "# Session Context:" in markdown, "Should have session context header"
    assert "- Branch: test-branch" in markdown, "Should have branch info"
    assert "- Current Action: Initial" in markdown, "Should have current action"
    assert "# Action: Test Action" in markdown, "Should have action header"
    assert "Test description" in markdown, "Should have action description"


def test_template_markdown(template_manager):
    """Test template markdown generation."""
    template = template_manager.create_template(
        title="Test Template",
        current_action="Initial",
        context="Test context",
        task="Test task",
        requirements=["Requirement 1"],
        expected_output="Test output",
    )

    markdown = template.to_markdown()

    # Verify markdown content
    assert "# Test Template" in markdown, "Should have template title"
    assert "## Current Action: Initial" in markdown, "Should have current action"
    assert "## Context" in markdown, "Should have context section"
    assert "Test context" in markdown, "Should have context content"
    assert "## Task" in markdown, "Should have task section"
    assert "Test task" in markdown, "Should have task content"
    assert "## Requirements" in markdown, "Should have requirements section"
    assert "- Requirement 1" in markdown, "Should have requirement item"
    assert "## Expected Output" in markdown, "Should have expected output section"
    assert "Test output" in markdown, "Should have expected output content"
