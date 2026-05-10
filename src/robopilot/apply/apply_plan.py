"""Safely apply a previously exported apply plan."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from robopilot.apply_plan.plan import (
    apply_plan_from_preview,
    load_apply_plan,
    validate_apply_plan,
)
from robopilot.apply_preview.preview import preview_apply
from robopilot.generator.project_generator import render_project_files
from robopilot.history.journal import record_history_entry
from robopilot.spec.io import load_spec
from robopilot.spec.validator import validate_spec


SAFETY_NOTE = (
    "RoboPilot apply validates the plan, re-runs apply-preview, refuses stale "
    "plans and conflicts, and only writes files listed in files_to_create or "
    "files_to_update when --confirm is provided."
)


@dataclass(frozen=True)
class ApplySummary:
    """Summary of a dry-run or confirmed apply operation."""

    plan_path: str
    project_path: str
    dry_run: bool
    files_created: tuple[str, ...]
    files_updated: tuple[str, ...]
    files_kept: tuple[str, ...]
    backups_created: tuple[str, ...]
    skipped_files: tuple[str, ...]
    conflicts: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""
        return {
            "plan_path": self.plan_path,
            "project_path": self.project_path,
            "dry_run": self.dry_run,
            "files_created": list(self.files_created),
            "files_updated": list(self.files_updated),
            "files_kept": list(self.files_kept),
            "backups_created": list(self.backups_created),
            "skipped_files": list(self.skipped_files),
            "conflicts": list(self.conflicts),
            "safety_note": self.safety_note,
        }


def apply_from_plan(plan_path: Path, *, confirm: bool = False) -> ApplySummary:
    """Dry-run or apply a saved plan after conservative safety checks."""
    plan = load_apply_plan(plan_path)
    validation = validate_apply_plan(plan)
    if not validation.is_valid:
        raise ValueError("Invalid apply plan: " + "; ".join(validation.errors))

    spec_path = Path(_string_field(plan, "spec_path"))
    project_path = Path(_string_field(plan, "project_path"))
    spec = load_spec(spec_path)
    spec_validation = validate_spec(spec)
    if not spec_validation.is_valid:
        raise ValueError("Invalid ProjectSpec: " + "; ".join(spec_validation.errors))

    fresh_preview = preview_apply(spec_path, project_path)
    fresh_plan = apply_plan_from_preview(fresh_preview)
    _ensure_plan_is_fresh(plan, fresh_plan)

    conflicts = tuple(_list_field(plan, "conflicts"))
    if confirm and conflicts:
        raise ValueError("Refusing to apply because conflicts are present.")

    files_to_create = tuple(_validate_relative_paths(_list_field(plan, "files_to_create")))
    files_to_update = tuple(_validate_relative_paths(_list_field(plan, "files_to_update")))
    files_to_keep = tuple(_validate_relative_paths(_list_field(plan, "files_to_keep")))
    expected_files = {
        path.as_posix(): content for path, content in render_project_files(spec).items()
    }

    _ensure_planned_files_are_expected(files_to_create + files_to_update, expected_files)

    if not confirm:
        return ApplySummary(
            plan_path=str(plan_path),
            project_path=str(project_path),
            dry_run=True,
            files_created=(),
            files_updated=(),
            files_kept=files_to_keep,
            backups_created=(),
            skipped_files=tuple(sorted(files_to_create + files_to_update + files_to_keep + conflicts)),
            conflicts=conflicts,
            safety_note="Dry run only. No files were modified. " + SAFETY_NOTE,
        )

    created: list[str] = []
    updated: list[str] = []
    backups: list[str] = []
    backup_root = project_path / ".robopilot_backups" / _timestamp()

    for relative_path in files_to_create:
        target = project_path / relative_path
        if target.exists():
            raise ValueError(f"Refusing to create existing file: {relative_path}")
        _write_expected_file(target, expected_files[relative_path])
        created.append(relative_path)

    for relative_path in files_to_update:
        target = project_path / relative_path
        if not target.is_file():
            raise ValueError(f"Refusing to update missing file: {relative_path}")
        backup_path = backup_root / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup_path)
        backups.append(backup_path.relative_to(project_path).as_posix())
        _write_expected_file(target, expected_files[relative_path])
        updated.append(relative_path)

    summary = ApplySummary(
        plan_path=str(plan_path),
        project_path=str(project_path),
        dry_run=False,
        files_created=tuple(sorted(created)),
        files_updated=tuple(sorted(updated)),
        files_kept=files_to_keep,
        backups_created=tuple(sorted(backups)),
        skipped_files=tuple(sorted(files_to_keep + conflicts)),
        conflicts=conflicts,
        safety_note=SAFETY_NOTE,
    )
    record_history_entry(
        project_path=project_path,
        operation="apply",
        plan_path=str(plan_path),
        dry_run=False,
        success=True,
        files_created=summary.files_created,
        files_updated=summary.files_updated,
        files_kept=summary.files_kept,
        conflicts=summary.conflicts,
        skipped_files=summary.skipped_files,
        summary=(
            f"Applied plan with {len(summary.files_created)} files created "
            f"and {len(summary.files_updated)} files updated."
        ),
    )
    return summary


def _ensure_plan_is_fresh(
    saved_plan: dict[str, object],
    fresh_plan: dict[str, object],
) -> None:
    compared_fields = (
        "spec_path",
        "project_path",
        "package_name",
        "selected_template",
        "files_to_create",
        "files_to_update",
        "files_to_keep",
        "conflicts",
        "missing_project",
    )
    for field in compared_fields:
        if saved_plan.get(field) != fresh_plan.get(field):
            raise ValueError(f"Refusing to apply stale plan: {field} changed.")


def _ensure_planned_files_are_expected(
    relative_paths: tuple[str, ...],
    expected_files: dict[str, str],
) -> None:
    for relative_path in relative_paths:
        if relative_path not in expected_files:
            raise ValueError(f"Refusing to modify unexpected file: {relative_path}")


def _write_expected_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _string_field(plan: dict[str, object], field: str) -> str:
    value = plan.get(field)
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string.")
    return value


def _list_field(plan: dict[str, object], field: str) -> tuple[str, ...]:
    value = plan.get(field)
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return tuple(str(item) for item in value)


def _validate_relative_paths(paths: tuple[str, ...]) -> tuple[str, ...]:
    validated: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Refusing unsafe relative path: {raw_path}")
        validated.append(path.as_posix())
    return tuple(validated)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
