import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.apply_plan.plan import (
    apply_plan_from_yaml,
    export_apply_plan,
    load_apply_plan,
    validate_apply_plan_file,
)
from robopilot.apply_preview.preview import preview_apply
from robopilot.generator.project_generator import generate_project_from_spec
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.refiner.spec_refiner import refine_spec
from robopilot.spec.io import write_spec


TASK = "Create an object detection node publishing bounding boxes"


def _base_spec():
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def _write_refined_spec(tmp_path: Path) -> tuple[Path, Path]:
    base = _base_spec()
    refined = refine_spec(base, "Add a tracker node after the detector")
    spec_path = tmp_path / "refined.yaml"
    write_spec(refined, spec_path)
    project = generate_project_from_spec(spec=base, output_root=tmp_path / "generated")
    return spec_path, project.output_dir


def test_exports_yaml_like_apply_plan(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.yaml"

    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=output_path,
    )

    text = output_path.read_text(encoding="utf-8")
    assert "generated_by: \"RoboPilot ApplyPlan\"" in text
    assert "files_to_create:" in text
    assert "demo_detector/tracker_node.py" in text


def test_exports_json_apply_plan(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.json"

    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=output_path,
        output_format="json",
    )

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["generated_by"] == "RoboPilot ApplyPlan"
    assert "demo_detector/tracker_node.py" in data["files_to_create"]


def test_apply_plan_contains_stable_keys(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.yaml"

    plan = export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=output_path,
    )

    assert list(plan.keys()) == [
        "generated_by",
        "spec_path",
        "project_path",
        "package_name",
        "selected_template",
        "files_to_create",
        "files_to_update",
        "files_to_keep",
        "conflicts",
        "missing_project",
        "safety_note",
        "suggested_next_steps",
    ]


def test_apply_plan_reuses_apply_preview_classifications(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.yaml"

    preview = preview_apply(spec_path, project_path)
    plan = export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=output_path,
    )

    assert plan["files_to_create"] == list(preview.files_to_create)
    assert plan["files_to_update"] == list(preview.files_to_update)
    assert plan["conflicts"] == list(preview.conflicts)


def test_apply_plan_validate_accepts_valid_plan(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=output_path,
    )

    result = validate_apply_plan_file(output_path)

    assert result.is_valid
    assert result.errors == ()


def test_apply_plan_validate_rejects_missing_required_fields(tmp_path: Path) -> None:
    plan_path = tmp_path / "broken_plan.yaml"
    plan_path.write_text(
        "generated_by: \"RoboPilot ApplyPlan\"\n"
        "files_to_create:\n"
        "  - \"package.xml\"\n",
        encoding="utf-8",
    )

    result = validate_apply_plan_file(plan_path)

    assert not result.is_valid
    assert "spec_path is required." in result.errors
    assert "missing_project is required." in result.errors


def test_apply_plan_export_does_not_modify_project(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    package_xml = project_path / "package.xml"
    before = package_xml.read_text(encoding="utf-8")

    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=tmp_path / "apply_plan.yaml",
    )

    assert package_xml.read_text(encoding="utf-8") == before
    assert not (project_path / "demo_detector" / "tracker_node.py").exists()


def test_existing_apply_preview_still_works(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)

    result = preview_apply(spec_path, project_path)

    assert "demo_detector/tracker_node.py" in result.files_to_create


def test_cli_apply_plan_and_validate_work(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.yaml"
    runner = CliRunner()

    export_result = runner.invoke(
        app,
        [
            "apply-plan",
            "--spec",
            str(spec_path),
            "--project",
            str(project_path),
            "--output",
            str(output_path),
        ],
    )
    validate_result = runner.invoke(
        app,
        ["apply-plan-validate", "--plan", str(output_path)],
    )

    assert export_result.exit_code == 0
    assert output_path.is_file()
    assert validate_result.exit_code == 0
    assert "Valid apply plan" in validate_result.output


def test_cli_apply_plan_json_format_works(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.json"
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "apply-plan",
            "--spec",
            str(spec_path),
            "--project",
            str(project_path),
            "--output",
            str(output_path),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert load_apply_plan(output_path)["generated_by"] == "RoboPilot ApplyPlan"


def test_yaml_parser_round_trips_plan_values(tmp_path: Path) -> None:
    spec_path, project_path = _write_refined_spec(tmp_path)
    output_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=output_path,
    )

    parsed = apply_plan_from_yaml(output_path.read_text(encoding="utf-8"))

    assert parsed["generated_by"] == "RoboPilot ApplyPlan"
    assert parsed["missing_project"] is False
