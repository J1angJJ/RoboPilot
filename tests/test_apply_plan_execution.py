import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.apply.apply_plan import apply_from_plan
from robopilot.apply_plan.plan import export_apply_plan
from robopilot.generator.project_generator import generate_project_from_spec
from robopilot.inspector.project_inspector import inspect_project
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.spec.io import write_spec


TASK = "Create an object detection node publishing bounding boxes"


def _base_spec():
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def _write_plan_for_missing_project(tmp_path: Path) -> tuple[Path, Path]:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    project_path = tmp_path / "apply_target"
    plan_path = tmp_path / "apply_plan.yaml"
    write_spec(spec, spec_path)
    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=plan_path,
    )
    return plan_path, project_path


def _write_plan_for_existing_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    write_spec(spec, spec_path)
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    plan_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project.output_dir,
        output_path=plan_path,
    )
    return plan_path, project.output_dir, spec_path


def test_default_apply_is_dry_run_and_does_not_modify_files(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)

    summary = apply_from_plan(plan_path)

    assert summary.dry_run
    assert summary.files_created == ()
    assert not project_path.exists()


def test_confirm_creates_missing_files_listed_in_plan(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)

    summary = apply_from_plan(plan_path, confirm=True)

    assert not summary.dry_run
    assert "package.xml" in summary.files_created
    assert (project_path / "package.xml").is_file()
    assert (project_path / "demo_detector" / "detector_node.py").is_file()


def test_confirm_updates_changed_files_listed_in_plan(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    write_spec(spec, spec_path)
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    readme_path = project.output_dir / "README.md"
    readme_path.write_text("local stale readme\n", encoding="utf-8")
    plan_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project.output_dir,
        output_path=plan_path,
    )

    summary = apply_from_plan(plan_path, confirm=True)

    assert "README.md" in summary.files_updated
    assert "local stale readme" not in readme_path.read_text(encoding="utf-8")


def test_backups_are_created_before_updating_files(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    write_spec(spec, spec_path)
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    package_xml = project.output_dir / "package.xml"
    package_xml.write_text("old package xml\n", encoding="utf-8")
    plan_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project.output_dir,
        output_path=plan_path,
    )

    summary = apply_from_plan(plan_path, confirm=True)

    assert summary.backups_created
    backup_paths = [project.output_dir / path for path in summary.backups_created]
    assert any(path.name == "package.xml" for path in backup_paths)
    assert any(path.read_text(encoding="utf-8") == "old package xml\n" for path in backup_paths)


def test_files_to_keep_are_not_modified(tmp_path: Path) -> None:
    plan_path, project_path, _ = _write_plan_for_existing_project(tmp_path)
    setup_cfg = project_path / "setup.cfg"
    before = setup_cfg.read_text(encoding="utf-8")

    summary = apply_from_plan(plan_path, confirm=True)

    assert "setup.cfg" in summary.files_kept
    assert setup_cfg.read_text(encoding="utf-8") == before


def test_conflicts_cause_confirmed_apply_to_fail(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    (project.output_dir / "unexpected.txt").write_text("do not touch\n", encoding="utf-8")
    write_spec(spec, spec_path)
    plan_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project.output_dir,
        output_path=plan_path,
    )

    try:
        apply_from_plan(plan_path, confirm=True)
    except ValueError as exc:
        assert "conflicts are present" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
    assert (project.output_dir / "unexpected.txt").read_text(encoding="utf-8") == "do not touch\n"


def test_stale_plan_is_rejected(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)
    project_path.mkdir()
    (project_path / "package.xml").write_text("created after plan\n", encoding="utf-8")

    try:
        apply_from_plan(plan_path, confirm=True)
    except ValueError as exc:
        assert "stale plan" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_plan_is_rejected(tmp_path: Path) -> None:
    plan_path = tmp_path / "invalid.yaml"
    plan_path.write_text("generated_by: \"RoboPilot ApplyPlan\"\n", encoding="utf-8")

    try:
        apply_from_plan(plan_path, confirm=True)
    except ValueError as exc:
        assert "Invalid apply plan" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    plan_path, _ = _write_plan_for_missing_project(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["apply", "--plan", str(plan_path), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "plan_path",
        "project_path",
        "dry_run",
        "files_created",
        "files_updated",
        "files_kept",
        "backups_created",
        "skipped_files",
        "conflicts",
        "safety_note",
    ]
    assert data["dry_run"] is True


def test_generated_project_remains_inspectable_after_apply(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)

    apply_from_plan(plan_path, confirm=True)
    report = inspect_project(project_path)

    assert report.exists
    assert report.package_name == "demo_detector"
    assert report.spec.valid
    assert report.issues == ()


def test_existing_commands_still_work(tmp_path: Path) -> None:
    runner = CliRunner()

    generate_result = runner.invoke(
        app,
        [
            "generate",
            "--name",
            "demo_detector",
            "--task",
            TASK,
            "--output-root",
            str(tmp_path),
        ],
    )
    inspect_result = runner.invoke(app, ["inspect", str(tmp_path / "demo_detector")])

    assert generate_result.exit_code == 0
    assert inspect_result.exit_code == 0
