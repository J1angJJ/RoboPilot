"""Project-local history journal for confirmed file-changing operations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


HISTORY_DIR_NAME = ".robopilot_history"


@dataclass(frozen=True)
class HistoryEntry:
    """One project-local history entry."""

    id: str
    operation: str
    timestamp: str
    project_path: str
    plan_path: str
    backup_path: str
    dry_run: bool
    success: bool
    files_created: tuple[str, ...]
    files_updated: tuple[str, ...]
    files_restored: tuple[str, ...]
    files_kept: tuple[str, ...]
    conflicts: tuple[str, ...]
    skipped_files: tuple[str, ...]
    summary: str

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""
        return {
            "id": self.id,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "project_path": self.project_path,
            "plan_path": self.plan_path,
            "backup_path": self.backup_path,
            "dry_run": self.dry_run,
            "success": self.success,
            "files_created": list(self.files_created),
            "files_updated": list(self.files_updated),
            "files_restored": list(self.files_restored),
            "files_kept": list(self.files_kept),
            "conflicts": list(self.conflicts),
            "skipped_files": list(self.skipped_files),
            "summary": self.summary,
        }


@dataclass(frozen=True)
class HistoryReport:
    """History entries for one project."""

    project_path: str
    history_dir: str
    entries: tuple[HistoryEntry, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a stable JSON-serializable representation."""
        return {
            "project_path": self.project_path,
            "history_dir": self.history_dir,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def record_history_entry(
    *,
    project_path: Path,
    operation: str,
    plan_path: str = "",
    backup_path: str = "",
    dry_run: bool = False,
    success: bool = True,
    files_created: tuple[str, ...] = (),
    files_updated: tuple[str, ...] = (),
    files_restored: tuple[str, ...] = (),
    files_kept: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
    skipped_files: tuple[str, ...] = (),
    summary: str = "",
) -> HistoryEntry:
    """Write one history entry under the project's history directory."""
    if dry_run:
        raise ValueError("History entries are only recorded for confirmed operations.")

    normalized_operation = operation.strip().lower()
    if normalized_operation not in {"apply", "rollback"}:
        raise ValueError(f"Unsupported history operation: {operation}")

    project_root = _resolve_project_directory(project_path)
    history_dir = _history_dir(project_root)
    history_dir.mkdir(parents=True, exist_ok=True)

    timestamp = _timestamp()
    entry_id = _unique_entry_id(history_dir, timestamp, normalized_operation)
    entry = HistoryEntry(
        id=entry_id,
        operation=normalized_operation,
        timestamp=timestamp,
        project_path=str(project_path),
        plan_path=plan_path,
        backup_path=backup_path,
        dry_run=dry_run,
        success=success,
        files_created=tuple(sorted(files_created)),
        files_updated=tuple(sorted(files_updated)),
        files_restored=tuple(sorted(files_restored)),
        files_kept=tuple(sorted(files_kept)),
        conflicts=tuple(sorted(conflicts)),
        skipped_files=tuple(sorted(skipped_files)),
        summary=summary,
    )
    output_path = history_dir / f"{entry_id}.json"
    output_path.write_text(
        json.dumps(entry.to_dict(), indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return entry


def list_history(project_path: Path) -> HistoryReport:
    """Load project history entries in deterministic chronological order."""
    project_root = _resolve_project_directory(project_path)
    history_dir = _history_dir(project_root)
    entries: list[HistoryEntry] = []
    if history_dir.is_dir():
        for path in sorted(history_dir.glob("*.json"), key=lambda item: item.name):
            try:
                entry = _entry_from_json(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            entries.append(entry)
    entries.sort(key=lambda entry: (entry.timestamp, entry.id))
    return HistoryReport(
        project_path=str(project_path),
        history_dir=str(history_dir),
        entries=tuple(entries),
    )


def _entry_from_json(path: Path) -> HistoryEntry:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("History entry must be a JSON object.")
    return HistoryEntry(
        id=_string(data, "id"),
        operation=_string(data, "operation"),
        timestamp=_string(data, "timestamp"),
        project_path=_string(data, "project_path"),
        plan_path=_string(data, "plan_path"),
        backup_path=_string(data, "backup_path"),
        dry_run=_bool(data, "dry_run"),
        success=_bool(data, "success"),
        files_created=_strings(data, "files_created"),
        files_updated=_strings(data, "files_updated"),
        files_restored=_strings(data, "files_restored"),
        files_kept=_strings(data, "files_kept"),
        conflicts=_strings(data, "conflicts"),
        skipped_files=_strings(data, "skipped_files"),
        summary=_string(data, "summary"),
    )


def _resolve_project_directory(path: Path) -> Path:
    if not path.exists():
        raise ValueError(f"Project path does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"Project path is not a directory: {path}")
    return path.resolve()


def _history_dir(project_root: Path) -> Path:
    history_dir = (project_root / HISTORY_DIR_NAME).resolve()
    if not _is_relative_to(history_dir, project_root):
        raise ValueError("History directory must be inside the project path.")
    return history_dir


def _unique_entry_id(history_dir: Path, timestamp: str, operation: str) -> str:
    base = f"{timestamp}_{operation}"
    candidate = base
    index = 1
    while (history_dir / f"{candidate}.json").exists():
        candidate = f"{base}_{index:03d}"
        index += 1
    return candidate


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _string(data: dict[str, Any], field: str) -> str:
    value = data.get(field, "")
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string.")
    return value


def _bool(data: dict[str, Any], field: str) -> bool:
    value = data.get(field, False)
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean.")
    return value


def _strings(data: dict[str, Any], field: str) -> tuple[str, ...]:
    value = data.get(field, [])
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return tuple(str(item) for item in value)
