import json
from pathlib import Path

from typer.testing import CliRunner

from robopilot.main import app
from robopilot.rollback.rollback import rollback_project


def _project_with_backup(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "demo_detector"
    backup = project / ".robopilot_backups" / "20260101_000000"
    (project / "config").mkdir(parents=True)
    (backup / "config").mkdir(parents=True)
    (project / "config" / "params.yaml").write_text("current\n", encoding="utf-8")
    (backup / "config" / "params.yaml").write_text("backup\n", encoding="utf-8")
    return project, backup


def test_default_rollback_is_dry_run_and_does_not_modify_files(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)

    summary = rollback_project(project_path=project, backup_path=backup)

    assert summary.dry_run
    assert summary.files_to_restore == ("config/params.yaml",)
    assert summary.files_restored == ()
    assert (project / "config" / "params.yaml").read_text(encoding="utf-8") == "current\n"


def test_confirm_restores_changed_file_from_backup(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)

    summary = rollback_project(project_path=project, backup_path=backup, confirm=True)

    assert not summary.dry_run
    assert summary.files_restored == ("config/params.yaml",)
    assert (project / "config" / "params.yaml").read_text(encoding="utf-8") == "backup\n"


def test_rollback_creates_parent_directories_if_needed(tmp_path: Path) -> None:
    project = tmp_path / "demo_detector"
    backup = project / ".robopilot_backups" / "20260101_000000"
    project.mkdir()
    (backup / "nested").mkdir(parents=True)
    (backup / "nested" / "file.txt").write_text("backup\n", encoding="utf-8")

    rollback_project(project_path=project, backup_path=backup, confirm=True)

    assert (project / "nested" / "file.txt").read_text(encoding="utf-8") == "backup\n"


def test_non_existent_project_path_is_rejected(tmp_path: Path) -> None:
    backup = tmp_path / "backup"
    backup.mkdir()

    try:
        rollback_project(project_path=tmp_path / "missing", backup_path=backup)
    except ValueError as exc:
        assert "Project path does not exist" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_non_existent_backup_path_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    try:
        rollback_project(project_path=project, backup_path=project / ".robopilot_backups" / "missing")
    except ValueError as exc:
        assert "Backup path does not exist" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_unsafe_backup_path_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "project"
    backup = tmp_path / "external_backup"
    project.mkdir()
    backup.mkdir()

    try:
        rollback_project(project_path=project, backup_path=backup)
    except ValueError as exc:
        assert ".robopilot_backups" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_unsafe_relative_paths_inside_backup_are_skipped(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)
    unsafe = backup / "linked.txt"
    target = tmp_path / "outside.txt"
    target.write_text("outside\n", encoding="utf-8")
    try:
        unsafe.symlink_to(target)
    except OSError:
        return

    summary = rollback_project(project_path=project, backup_path=backup)

    assert "linked.txt" in summary.skipped_files
    assert any("unsafe" in error for error in summary.errors)


def test_json_output_has_stable_keys(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["rollback", "--project", str(project), "--backup", str(backup), "--json"],
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert list(data.keys()) == [
        "project_path",
        "backup_path",
        "dry_run",
        "files_to_restore",
        "files_restored",
        "skipped_files",
        "errors",
        "safety_note",
    ]


def test_rollback_does_not_delete_unrelated_files(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)
    unrelated = project / "new_file.txt"
    unrelated.write_text("keep me\n", encoding="utf-8")

    rollback_project(project_path=project, backup_path=backup, confirm=True)

    assert unrelated.read_text(encoding="utf-8") == "keep me\n"


def test_cli_confirm_restores_file(tmp_path: Path) -> None:
    project, backup = _project_with_backup(tmp_path)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["rollback", "--project", str(project), "--backup", str(backup), "--confirm"],
    )

    assert result.exit_code == 0
    assert "Rollback Summary" in result.output
    assert (project / "config" / "params.yaml").read_text(encoding="utf-8") == "backup\n"
