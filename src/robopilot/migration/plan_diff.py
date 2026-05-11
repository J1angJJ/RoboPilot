"""Static diff for ROS1-to-ROS2 migration plans."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from robopilot.migration.plan_validator import validate_migration_plan_file
from robopilot.migration.ros1_to_ros2 import LIST_FIELDS, load_migration_plan


SAFETY_NOTE = (
    "This migration plan diff is static and read-only. RoboPilot did not "
    "modify either migration plan file, modify source projects, generate "
    "migrated files, require ROS, require ROS2, run catkin_make, run colcon, "
    "execute launch files, execute code, or import user project modules."
)

SCALAR_FIELDS = (
    "source_path",
    "target",
    "source_project_type",
    "package_name",
    "confidence",
    "summary",
)

LIST_DIFF_FIELDS = tuple(
    field
    for field in (
        "package_xml_migration",
        "build_system_migration",
        "source_code_migration",
        "launch_migration",
        "interface_migration",
        "suggested_file_changes",
        "manual_review_items",
        "risks",
        "suggested_next_steps",
    )
    if field in LIST_FIELDS
)


@dataclass(frozen=True)
class MigrationPlanDiffResult:
    """Structured diff between two migration plans."""

    old_plan: str
    new_plan: str
    valid: bool
    has_changes: bool
    changed_fields: dict[str, dict[str, str]]
    added_items: dict[str, list[str]]
    removed_items: dict[str, list[str]]
    unchanged_fields: tuple[str, ...]
    warnings: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "old_plan": self.old_plan,
            "new_plan": self.new_plan,
            "valid": self.valid,
            "has_changes": self.has_changes,
            "changed_fields": self.changed_fields,
            "added_items": self.added_items,
            "removed_items": self.removed_items,
            "unchanged_fields": list(self.unchanged_fields),
            "warnings": list(self.warnings),
            "safety_note": self.safety_note,
        }


def diff_migration_plans(old_plan_path: Path, new_plan_path: Path) -> MigrationPlanDiffResult:
    """Compare two valid migration plans without modifying either file."""
    old_validation = validate_migration_plan_file(old_plan_path)
    new_validation = validate_migration_plan_file(new_plan_path)
    errors: list[str] = []
    if not old_validation.valid:
        errors.append("old migration plan is invalid: " + _validation_errors(old_validation))
    if not new_validation.valid:
        errors.append("new migration plan is invalid: " + _validation_errors(new_validation))
    if errors:
        raise ValueError("; ".join(errors))

    old_plan = load_migration_plan(old_plan_path)
    new_plan = load_migration_plan(new_plan_path)
    changed_fields: dict[str, dict[str, str]] = {}
    added_items: dict[str, list[str]] = {}
    removed_items: dict[str, list[str]] = {}
    unchanged: list[str] = []

    for field in SCALAR_FIELDS:
        old_value = str(old_plan.get(field, ""))
        new_value = str(new_plan.get(field, ""))
        if old_value != new_value:
            changed_fields[field] = {"old": old_value, "new": new_value}
        else:
            unchanged.append(field)

    for field in LIST_DIFF_FIELDS:
        old_values = _string_list(old_plan.get(field, []))
        new_values = _string_list(new_plan.get(field, []))
        added = sorted(set(new_values) - set(old_values))
        removed = sorted(set(old_values) - set(new_values))
        if added:
            added_items[field] = added
        if removed:
            removed_items[field] = removed
        if not added and not removed:
            unchanged.append(field)

    old_dependency = _flatten_dependency_migration(old_plan.get("dependency_migration", {}))
    new_dependency = _flatten_dependency_migration(new_plan.get("dependency_migration", {}))
    added_dependency = sorted(set(new_dependency) - set(old_dependency))
    removed_dependency = sorted(set(old_dependency) - set(new_dependency))
    if added_dependency:
        added_items["dependency_migration"] = added_dependency
    if removed_dependency:
        removed_items["dependency_migration"] = removed_dependency
    if not added_dependency and not removed_dependency:
        unchanged.append("dependency_migration")

    warnings = tuple(sorted(dict.fromkeys(old_validation.warnings + new_validation.warnings)))
    has_changes = bool(changed_fields or added_items or removed_items)
    return MigrationPlanDiffResult(
        old_plan=str(old_plan_path),
        new_plan=str(new_plan_path),
        valid=True,
        has_changes=has_changes,
        changed_fields=changed_fields,
        added_items=added_items,
        removed_items=removed_items,
        unchanged_fields=tuple(sorted(unchanged)),
        warnings=warnings,
        safety_note=SAFETY_NOTE,
    )


def _validation_errors(report) -> str:
    parts: list[str] = []
    parts.extend(f"missing {field}" for field in report.missing_fields)
    parts.extend(report.invalid_fields)
    return ", ".join(parts) or "unknown validation error"


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return sorted(str(item) for item in value)
    if isinstance(value, tuple):
        return sorted(str(item) for item in value)
    return []


def _flatten_dependency_migration(value: object) -> list[str]:
    if not isinstance(value, dict):
        return []
    flattened: list[str] = []
    _flatten_value(flattened, "", value)
    return sorted(flattened)


def _flatten_value(items: list[str], prefix: str, value: Any) -> None:
    if isinstance(value, dict):
        for key in sorted(value):
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            _flatten_value(items, child_prefix, value[key])
        return
    if isinstance(value, list):
        for item in sorted(str(item) for item in value):
            items.append(f"{prefix}: {item}")
        return
    items.append(f"{prefix}: {json.dumps(value, sort_keys=True)}")
