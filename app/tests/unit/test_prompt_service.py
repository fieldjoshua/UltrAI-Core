import pytest
from unittest.mock import MagicMock
from app.services.prompt_service import PromptService, Template, PromptRequest
from app.services.model_registry import ModelRegistry
from app.services.orchestration_service import OrchestrationService


@pytest.fixture
def mock_services():
    model_registry = MagicMock(spec=ModelRegistry)
    orchestration_service = MagicMock(spec=OrchestrationService)
    return model_registry, orchestration_service


@pytest.fixture
def prompt_service(mock_services):
    model_registry, orchestration_service = mock_services
    return PromptService(model_registry, orchestration_service)


def test_register_and_get_template(prompt_service):
    template = Template(
        name="test",
        description="Test template",
        template="Hello {name}",
        variables=["name"],
    )
    prompt_service.register_template(template)
    result = prompt_service.get_template("test")
    assert result == template


def test_update_template(prompt_service):
    template = Template(
        name="update",
        description="To update",
        template="Hi {name}",
        variables=["name"],
    )
    prompt_service.register_template(template)
    prompt_service.update_template("update", {"description": "Updated!"})
    updated = prompt_service.get_template("update").description
    assert updated == "Updated!"


def test_list_templates(prompt_service):
    templates = prompt_service.list_templates()
    assert isinstance(templates, list)
    assert any("name" in t for t in templates)


def test_render_template(prompt_service):
    template = Template(
        name="render",
        description="Render test",
        template="Hi {name}",
        variables=["name"],
    )
    prompt_service.register_template(template)
    rendered = prompt_service._render_template(template, {"name": "Ultra"})
    assert rendered == "Hi Ultra"


def test_process_prompt_success(prompt_service):
    template = Template(
        name="process",
        description="Process test",
        template="Hi {name}",
        variables=["name"],
    )
    prompt_service.register_template(template)
    req = PromptRequest(
        template_name="process",
        variables={"name": "Ultra"},
        models=["test-model"],
    )
    # Mock orchestration_service to avoid async call
    prompt_service.orchestration_service.process_prompt = MagicMock(
        return_value={"result": "ok"}
    )
    # The actual process_prompt is async, so we need to run it in an event loop
    import asyncio

    result = asyncio.run(prompt_service.process_prompt(req))
    assert "result" in result


def test_process_prompt_missing_template(prompt_service):
    req = PromptRequest(
        template_name="notfound",
        variables={},
        models=[],
    )
    import asyncio

    with pytest.raises(ValueError):
        asyncio.run(prompt_service.process_prompt(req))
