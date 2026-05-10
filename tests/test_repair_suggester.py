from dataclasses import replace
from pathlib import Path

from robopilot.generator.project_generator import create_project_spec, generate_project
from robopilot.repair.repair_suggester import suggest_repairs
from robopilot.spec.io import write_spec


TASK = (
    "Create an object detection node subscribing to camera images and publishing "
    "bounding boxes."
)


def test_valid_project_produces_no_critical_repair_suggestions(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    report = suggest_repairs(generated.output_dir)

    assert report.issues == ()
    assert report.repair_suggestions == ()
    assert report.suggested_commands == (f"robopilot inspect {generated.output_dir}",)


def test_missing_package_xml_produces_package_xml_repair_suggestion(
    tmp_path: Path,
) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    (generated.output_dir / "package.xml").unlink()

    report = suggest_repairs(generated.output_dir)

    suggestions = [item.suggestion for item in report.repair_suggestions]
    assert "missing package.xml" in report.issues
    assert any("package.xml" in suggestion for suggestion in suggestions)
    assert any("robopilot generate --spec" in command for command in report.suggested_commands)


def test_missing_robopilot_yaml_produces_spec_repair_suggestion(
    tmp_path: Path,
) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    (generated.output_dir / "robopilot.yaml").unlink()

    report = suggest_repairs(generated.output_dir)

    suggestions = [item.suggestion for item in report.repair_suggestions]
    assert "missing robopilot.yaml" in report.issues
    assert any("robopilot plan" in command for command in report.suggested_commands)
    assert any("ProjectSpec" in suggestion for suggestion in suggestions)


def test_invalid_robopilot_yaml_produces_validation_repair_suggestion(
    tmp_path: Path,
) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )
    spec = create_project_spec(name="demo_detector", task=TASK)
    write_spec(replace(spec, package_name=""), generated.output_dir / "robopilot.yaml")

    report = suggest_repairs(generated.output_dir)

    assert "robopilot.yaml exists but fails validation" in report.issues
    assert any("robopilot validate --spec" in command for command in report.suggested_commands)
    assert any(
        suggestion.issue == "robopilot.yaml exists but fails validation"
        for suggestion in report.repair_suggestions
    )


def test_empty_project_directory_produces_bootstrap_suggestions(tmp_path: Path) -> None:
    empty_project = tmp_path / "empty_project"
    empty_project.mkdir()

    report = suggest_repairs(empty_project)

    assert "empty project directory" in report.issues
    assert any("robopilot generate" in command for command in report.suggested_commands)
    assert any("Bootstrap" in suggestion.suggestion for suggestion in report.repair_suggestions)


def test_nonexistent_path_produces_path_check_suggestions(tmp_path: Path) -> None:
    missing_project = tmp_path / "does_not_exist"

    report = suggest_repairs(missing_project)

    assert "project path does not exist" in report.issues
    assert any("Check" in suggestion.suggestion for suggestion in report.repair_suggestions)
    assert report.suggested_commands == (f"robopilot inspect {missing_project}",)


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    generated = generate_project(
        name="demo_detector",
        task=TASK,
        output_root=tmp_path,
    )

    data = suggest_repairs(generated.output_dir).to_dict()

    assert set(data) == {
        "project_path",
        "issues",
        "repair_suggestions",
        "safety_note",
        "suggested_commands",
    }
    assert data["repair_suggestions"] == []
    assert "does not modify files automatically" in data["safety_note"]
