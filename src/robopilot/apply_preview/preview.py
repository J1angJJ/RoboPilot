"""Read-only preview of applying a ProjectSpec to a project directory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from robopilot.generator.project_generator import render_project_files
from robopilot.spec.io import load_spec
from robopilot.spec.validator import validate_spec


SAFETY_NOTE = (
    "This is a read-only apply preview. RoboPilot did not modify project files, "
    "execute ROS2, run launch files, run colcon, or execute generated Python code."
)


@dataclass(frozen=True)
class ApplyPreviewResult:
    """Structured apply preview result."""

    spec_path: str
    project_path: str
    package_name: str
    selected_template: str
    files_to_create: tuple[str, ...]
    files_to_update: tuple[str, ...]
    files_to_keep: tuple[str, ...]
    conflicts: tuple[str, ...]
    missing_project: bool
    safety_note: str
    suggested_next_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""
        return {
            "spec_path": self.spec_path,
            "project_path": self.project_path,
            "package_name": self.package_name,
            "selected_template": self.selected_template,
            "files_to_create": list(self.files_to_create),
            "files_to_update": list(self.files_to_update),
            "files_to_keep": list(self.files_to_keep),
            "conflicts": list(self.conflicts),
            "missing_project": self.missing_project,
            "safety_note": self.safety_note,
            "suggested_next_steps": list(self.suggested_next_steps),
        }


def preview_apply(spec_path: Path, project_path: Path) -> ApplyPreviewResult:
    """Preview what applying a ProjectSpec would change without writing files."""
    spec = load_spec(spec_path)
    validation = validate_spec(spec)
    if not validation.is_valid:
        raise ValueError("Invalid ProjectSpec: " + "; ".join(validation.errors))

    expected_files = render_project_files(spec)
    missing_project = not project_path.exists()
    files_to_create: list[str] = []
    files_to_update: list[str] = []
    files_to_keep: list[str] = []

    for relative_path, expected_content in expected_files.items():
        normalized = _normalize_path(relative_path)
        target = project_path / relative_path
        if missing_project or not target.exists():
            files_to_create.append(normalized)
            continue
        if not target.is_file():
            files_to_update.append(normalized)
            continue
        try:
            existing_content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            files_to_update.append(normalized)
            continue
        if existing_content == expected_content:
            files_to_keep.append(normalized)
        else:
            files_to_update.append(normalized)

    conflicts = _detect_conflicts(project_path, set(expected_files))
    return ApplyPreviewResult(
        spec_path=str(spec_path),
        project_path=str(project_path),
        package_name=spec.package_name,
        selected_template=spec.selected_template,
        files_to_create=tuple(sorted(files_to_create)),
        files_to_update=tuple(sorted(files_to_update)),
        files_to_keep=tuple(sorted(files_to_keep)),
        conflicts=conflicts,
        missing_project=missing_project,
        safety_note=SAFETY_NOTE,
        suggested_next_steps=_suggest_next_steps(
            missing_project=missing_project,
            files_to_create=files_to_create,
            files_to_update=files_to_update,
            conflicts=conflicts,
            spec_path=spec_path,
            project_path=project_path,
        ),
    )


def _detect_conflicts(project_path: Path, expected_paths: set[Path]) -> tuple[str, ...]:
    if not project_path.exists() or not project_path.is_dir():
        return ()

    conflicts: list[str] = []
    for path in project_path.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(project_path)
        if _is_ignored_artifact(relative_path):
            continue
        if relative_path not in expected_paths:
            conflicts.append(_normalize_path(relative_path))
    return tuple(sorted(conflicts))


def _suggest_next_steps(
    *,
    missing_project: bool,
    files_to_create: list[str],
    files_to_update: list[str],
    conflicts: tuple[str, ...],
    spec_path: Path,
    project_path: Path,
) -> tuple[str, ...]:
    steps: list[str] = []
    if missing_project:
        steps.append("Create the project with robopilot generate --spec before applying future changes.")
    if files_to_create or files_to_update:
        steps.append(f"Review this preview before generating from {spec_path}.")
    if conflicts:
        steps.append("Review conflicts manually; RoboPilot will not overwrite unexpected files blindly.")
    if not steps:
        steps.append("No file changes are needed for the expected generated files.")
    steps.append(f"Run robopilot inspect {project_path} for a static project health check.")
    return tuple(steps)


def _is_ignored_artifact(relative_path: Path) -> bool:
    parts = set(relative_path.parts)
    return (
        "__pycache__" in parts
        or ".robopilot_backups" in parts
        or ".robopilot_history" in parts
        or relative_path.suffix in {".pyc", ".pyo"}
    )


def _normalize_path(path: Path) -> str:
    return path.as_posix()
