import pytest
import importlib
from unittest.mock import Mock
from app.services.prompt_service import PromptService, Template

# Skip module if missing dependencies
try:
    importlib.import_module("app.services.prompt_service")
except ImportError:
    pytest.skip(
        "Skipping tests for prompt_service due to missing dependencies",
        allow_module_level=True,
    )


# Placeholder test for prompt_service
def test_placeholder_prompt_service():
    assert True


@pytest.fixture
async def prompt_service():
    return PromptService(model_registry=Mock(), orchestration_service=Mock())


@pytest.mark.asyncio
async def test_default_templates_registered(prompt_service):
    # list_templates should include default template names
    names = [t["name"] for t in prompt_service.list_templates()]
    assert set(names) == {"analysis", "comparison", "evaluation"}


def test_register_and_get_template(prompt_service):
    new = Template(
        name="custom", description="desc", template="Hello {name}", variables=["name"]
    )
    prompt_service.register_template(new)
    tmpl = prompt_service.get_template("custom")
    assert tmpl is new


def test_register_duplicate_raises(prompt_service):
    with pytest.raises(ValueError):
        prompt_service.register_template(prompt_service.get_template("analysis"))


def test_update_template(prompt_service):
    prompt_service.update_template("analysis", {"description": "newdesc"})
    assert prompt_service.get_template("analysis").description == "newdesc"


def test_format_output_plain(prompt_service):
    content = "# Heading\n- item\nline"
    out = prompt_service._format_output(content, "plain")
    assert "Heading" in out and "item" in out and "#" not in out


def test_format_output_html(prompt_service):
    content = "# Heading"
    out = prompt_service._format_output(content, "html")
    assert "<h1>" in out


def test_format_output_json(prompt_service):
    content = "text"
    out = prompt_service._format_output(content, "json")
    assert '"content": "text"' in out


def test_render_template_success(prompt_service):
    tmpl = Template(name="t", description="", template="Val: {v}", variables=["v"])
    out = prompt_service._render_template(tmpl, {"v": "X"})
    assert out == "Val: X"


def test_render_template_missing_var(prompt_service):
    tmpl = Template(name="t", description="", template="Val: {v}", variables=["v"])
    with pytest.raises(ValueError):
        prompt_service._render_template(tmpl, {})


def test_render_template_invalid_var(prompt_service):
    tmpl = Template(
        name="t", description="", template="Val: {v} {x}", variables=["v", "x"]
    )
    with pytest.raises(ValueError):
        prompt_service._render_template(tmpl, {"v": "X"})


# TODO: Implement unit tests for prompt_service
