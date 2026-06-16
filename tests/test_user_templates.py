"""Tests for user-configurable templates (v2.1.0 Milestone 8)."""

from pathlib import Path

from robopilot.user_templates import (
    TEMPLATES_DIR,
    TEMPLATE_FILE,
    CustomTemplate,
    TemplateValidationResult,
    build_project_spec_from_custom,
    init_templates_dir,
    list_custom_templates,
    load_custom_template,
    validate_custom_template,
)


def test_init_creates_directory_and_example(tmp_path: Path) -> None:
    templates_dir = init_templates_dir(tmp_path)
    assert templates_dir.is_dir()
    assert (templates_dir / "README.md").exists()
    example = templates_dir / "my_custom_node"
    assert example.is_dir()
    assert (example / TEMPLATE_FILE).exists()


def test_list_custom_templates_finds_example(tmp_path: Path) -> None:
    init_templates_dir(tmp_path)
    ct_list = list_custom_templates(tmp_path)
    assert "my_custom_node" in ct_list
    ct = ct_list["my_custom_node"]
    assert ct.name == "my_custom_node"
    assert ct.extends == "generic_node"
    assert ct.definition.node_file_name == "my_node.py"


def test_load_custom_template(tmp_path: Path) -> None:
    init_templates_dir(tmp_path)
    ct = load_custom_template("my_custom_node", tmp_path)
    assert ct is not None
    assert ct.name == "my_custom_node"


def test_load_nonexistent_template(tmp_path: Path) -> None:
    assert load_custom_template("nope", tmp_path) is None


def test_validate_valid_template(tmp_path: Path) -> None:
    init_templates_dir(tmp_path)
    result = validate_custom_template(tmp_path / TEMPLATES_DIR / "my_custom_node")
    assert result.is_valid
    assert result.template_name == "my_custom_node"


def test_validate_missing_directory(tmp_path: Path) -> None:
    result = validate_custom_template(tmp_path / "does_not_exist")
    assert not result.is_valid


def test_validate_missing_template_yaml(tmp_path: Path) -> None:
    d = tmp_path / "empty"
    d.mkdir()
    result = validate_custom_template(d)
    assert not result.is_valid
    assert any("Missing template.yaml" in e for e in result.errors)


def test_validate_result_to_dict() -> None:
    r = TemplateValidationResult("t", "/p", True, ())
    d = r.to_dict()
    assert d["is_valid"] is True


def test_build_from_custom_template(tmp_path: Path) -> None:
    init_templates_dir(tmp_path)
    spec = build_project_spec_from_custom("my_custom_node", "Test task", root=tmp_path, package_name="my_project")
    assert spec is not None
    assert spec.selected_template == "my_custom_node"
    assert spec.package_name == "my_project"
    assert spec.nodes[0].class_name == "MyCustomNode"
    assert len(spec.topics) == 2
    assert spec.topics[0].name == "/my_input"


def test_build_from_unknown_template(tmp_path: Path) -> None:
    spec = build_project_spec_from_custom("unknown_template", "Task", root=tmp_path)
    assert spec is None
