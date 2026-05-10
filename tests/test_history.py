import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.apply.apply_plan import apply_from_plan
from robopilot.apply_plan.plan import export_apply_plan
from robopilot.generator.project_generator import generate_project_from_spec
from robopilot.history.journal import list_history, record_history_entry
from robopilot.main import app
from robopilot.planner.rule_based_planner import RuleBasedPlanner
from robopilot.rollback.rollback import rollback_project
from robopilot.spec.io import write_spec


TASK = "Create an object detection node publishing bounding boxes"


def _base_spec():
    return RuleBasedPlanner().plan(package_name="demo_detector", task=TASK)


def _write_plan_for_missing_project(tmp_path: Path) -> tuple[Path, Path]:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    project_path = tmp_path / "history_target"
    plan_path = tmp_path / "apply_plan.yaml"
    write_spec(spec, spec_path)
    export_apply_plan(
        spec_path=spec_path,
        project_path=project_path,
        output_path=plan_path,
    )
    return plan_path, project_path


def _project_with_backup(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "demo_detector"
    backup = project / ".robopilot_backups" / "20260101_000000"
    (project / "config").mkdir(parents=True)
    (backup / "config").mkdir(parents=True)
    (project / "config" / "params.yaml").write_text("current\n", encoding="utf-8")
    (backup / "config" / "params.yaml").write_text("backup\n", encoding="utf-8")
    return project, backup


def test_confirmed_apply_records_history_entry(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)

    apply_from_plan(plan_path, confirm=True)
    report = list_history(project_path)

    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.operation == "apply"
    assert entry.success is True
    assert entry.dry_run is False
    assert entry.plan_path == str(plan_path)
    assert "package.xml" in entry.files_created
    assert entry.files_updated == ()


def test_dry_run_apply_does_not_record_successful_modification_entry(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)

    apply_from_plan(plan_path)

    assert not (project_path / ".robopilot_history").exists()


def test_confirmed_rollback_records_history_entry(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)

    rollback_project(project_path=project, backup_path=backup, confirm=True)
    report = list_history(project)

    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.operation == "rollback"
    assert entry.backup_path == str(backup)
    assert entry.files_restored == ("config/params.yaml",)


def test_dry_run_rollback_does_not_record_successful_modification_entry(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)

    rollback_project(project_path=project, backup_path=backup)

    assert not (project / ".robopilot_history").exists()


def test_history_command_handles_project_with_no_history(tmp_path: Path) -> None:
    project = tmp_path / "empty_history"
    project.mkdir()
    runner = CliRunner()

    result = runner.invoke(app, ["history", "--project", str(project)])

    assert result.exit_code == 0
    assert "No RoboPilot history entries found" in result.output


def test_history_command_handles_missing_project_path(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["history", "--project", str(tmp_path / "missing")])

    assert result.exit_code == 1
    assert "Project path does not exist" in result.output


def test_history_json_output_has_stable_keys(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)
    apply_from_plan(plan_path, confirm=True)
    runner = CliRunner()

    result = runner.invoke(app, ["history", "--project", str(project_path), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == ["project_path", "history_dir", "entries"]
    assert list(data["entries"][0].keys()) == [
        "id",
        "operation",
        "timestamp",
        "project_path",
        "plan_path",
        "backup_path",
        "dry_run",
        "success",
        "files_created",
        "files_updated",
        "files_restored",
        "files_kept",
        "conflicts",
        "skipped_files",
        "summary",
    ]


def test_history_entries_are_sorted_deterministically(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    first = record_history_entry(
        project_path=project,
        operation="apply",
        files_created=("a.txt",),
        summary="first",
    )
    second = record_history_entry(
        project_path=project,
        operation="rollback",
        files_restored=("a.txt",),
        summary="second",
    )

    report = list_history(project)

    assert [entry.id for entry in report.entries] == [first.id, second.id]


def test_history_entries_do_not_include_file_contents(tmp_path: Path) -> None:
    spec = _base_spec()
    spec_path = tmp_path / "spec.yaml"
    write_spec(spec, spec_path)
    project = generate_project_from_spec(spec=spec, output_root=tmp_path / "generated")
    secret = "secret file content should not be journaled"
    readme = project.output_dir / "README.md"
    readme.write_text(secret, encoding="utf-8")
    plan_path = tmp_path / "apply_plan.yaml"
    export_apply_plan(
        spec_path=spec_path,
        project_path=project.output_dir,
        output_path=plan_path,
    )

    apply_from_plan(plan_path, confirm=True)
    history_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (project.output_dir / ".robopilot_history").glob("*.json")
    )

    assert secret not in history_text
    assert "README.md" in history_text


def test_history_cli_readable_output_lists_recent_entries(tmp_path: Path) -> None:
    plan_path, project_path = _write_plan_for_missing_project(tmp_path)
    apply_from_plan(plan_path, confirm=True)
    runner = CliRunner()

    result = runner.invoke(app, ["history", "--project", str(project_path)])

    assert result.exit_code == 0
    assert "History Summary" in result.output
    assert "apply" in result.output
