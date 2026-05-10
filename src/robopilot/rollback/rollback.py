"""Safely restore files from a RoboPilot backup directory."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from robopilot.history.journal import record_history_entry


SAFETY_NOTE = (
    "Rollback is dry-run by default. RoboPilot restores only files contained in "
    "the selected backup directory, preserves relative paths, does not delete "
    "newly created files, and does not execute ROS2, launch files, colcon, or "
    "generated code."
)


@dataclass(frozen=True)
class RollbackSummary:
    """Summary of a dry-run or confirmed rollback operation."""

    project_path: str
    backup_path: str
    dry_run: bool
    files_to_restore: tuple[str, ...]
    files_restored: tuple[str, ...]
    skipped_files: tuple[str, ...]
    errors: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""
        return {
            "project_path": self.project_path,
            "backup_path": self.backup_path,
            "dry_run": self.dry_run,
            "files_to_restore": list(self.files_to_restore),
            "files_restored": list(self.files_restored),
            "skipped_files": list(self.skipped_files),
            "errors": list(self.errors),
            "safety_note": self.safety_note,
        }


def rollback_project(
    *,
    project_path: Path,
    backup_path: Path,
    confirm: bool = False,
) -> RollbackSummary:
    """Dry-run or restore files from a RoboPilot backup directory."""
    project_root = _resolve_existing_directory(project_path, "Project path")
    backup_root = _resolve_existing_directory(backup_path, "Backup path")
    _validate_backup_location(project_root, backup_root)

    files_to_restore: list[str] = []
    skipped_files: list[str] = []
    errors: list[str] = []
    backup_files: list[tuple[Path, str]] = []

    for source in sorted(backup_root.rglob("*")):
        if not source.is_file():
            continue
        relative_path = source.relative_to(backup_root)
        normalized = relative_path.as_posix()
        if source.is_symlink() or _is_unsafe_relative_path(relative_path):
            skipped_files.append(normalized)
            errors.append(f"Skipped unsafe backup file: {normalized}")
            continue
        target = project_root / relative_path
        try:
            _ensure_inside_project(project_root, target)
        except ValueError as exc:
            skipped_files.append(normalized)
            errors.append(str(exc))
            continue
        files_to_restore.append(normalized)
        backup_files.append((source, normalized))

    if not confirm:
        return RollbackSummary(
            project_path=str(project_path),
            backup_path=str(backup_path),
            dry_run=True,
            files_to_restore=tuple(files_to_restore),
            files_restored=(),
            skipped_files=tuple(skipped_files),
            errors=tuple(errors),
            safety_note="Dry run only. No files were modified. " + SAFETY_NOTE,
        )

    restored: list[str] = []
    for source, normalized in backup_files:
        target = project_root / normalized
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        restored.append(normalized)

    summary = RollbackSummary(
        project_path=str(project_path),
        backup_path=str(backup_path),
        dry_run=False,
        files_to_restore=tuple(files_to_restore),
        files_restored=tuple(restored),
        skipped_files=tuple(skipped_files),
        errors=tuple(errors),
        safety_note=SAFETY_NOTE,
    )
    record_history_entry(
        project_path=project_path,
        operation="rollback",
        backup_path=str(backup_path),
        dry_run=False,
        success=True,
        files_restored=summary.files_restored,
        skipped_files=summary.skipped_files,
        summary=f"Restored {len(summary.files_restored)} files from backup.",
    )
    return summary


def _resolve_existing_directory(path: Path, label: str) -> Path:
    if not path.exists():
        raise ValueError(f"{label} does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"{label} is not a directory: {path}")
    return path.resolve()


def _validate_backup_location(project_root: Path, backup_root: Path) -> None:
    backups_root = (project_root / ".robopilot_backups").resolve()
    if not _is_relative_to(backup_root, backups_root):
        raise ValueError(
            "Backup path must be inside the project's .robopilot_backups directory."
        )


def _ensure_inside_project(project_root: Path, target: Path) -> None:
    resolved_parent = target.parent.resolve()
    if not _is_relative_to(resolved_parent, project_root):
        raise ValueError(f"Refusing path traversal outside project: {target}")


def _is_unsafe_relative_path(path: Path) -> bool:
    return path.is_absolute() or ".." in path.parts


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
