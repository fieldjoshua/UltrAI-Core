import pytest
import json
from app.services.prompt_templates import PromptTemplateManager, PromptTemplate


def test_register_and_get_template():
    mgr = PromptTemplateManager()
    mgr.register_template(
        name="t", template="Hello {{name}}", description="desc", variables=["name"]
    )
    tmpl = mgr.get_template("t")
    assert isinstance(tmpl, PromptTemplate)
    assert tmpl.name == "t"
    assert "name" in tmpl.variables


def test_list_templates_empty():
    mgr = PromptTemplateManager()
    assert mgr.list_templates() == []


def test_render_template_success():
    mgr = PromptTemplateManager()
    mgr.register_template(
        name="t", template="Hello {{name}}", description="desc", variables=["name"]
    )
    out = mgr.render_template("t", {"name": "X"})
    assert "X" in out


def test_render_template_missing_strict():
    mgr = PromptTemplateManager()
    mgr.register_template(
        name="t",
        template="Hello {{name}} {{age}}",
        description="desc",
        variables=["name", "age"],
    )
    with pytest.raises(ValueError):
        mgr.render_template("t", {"name": "X"}, strict=True)


def test_render_template_missing_not_strict():
    mgr = PromptTemplateManager()
    mgr.register_template(
        name="t", template="Hello {{name}}", description="desc", variables=["name"]
    )
    # strict=False should not raise
    out = mgr.render_template("t", {}, strict=False)
    assert "Hello" in out


def test_load_templates_from_file(tmp_path):
    data = [
        {"name": "t1", "template": "A", "description": "d", "variables": []},
        {"name": "t2", "template": "B", "description": "d2", "variables": []},
    ]
    file = tmp_path / "temp.json"
    file.write_text(json.dumps(data))
    mgr = PromptTemplateManager()
    mgr.load_templates_from_file(str(file))
    names = [t["name"] for t in mgr.list_templates()]
    assert set(names) == {"t1", "t2"}
