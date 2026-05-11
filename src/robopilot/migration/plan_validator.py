"""Static validation for serialized migration plans."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from robopilot.migration.ros1_to_ros2 import (
    LIST_FIELDS,
    SUPPORTED_TARGETS,
    TOP_LEVEL_FIELDS,
    load_migration_plan,
)


SAFETY_NOTE = (
    "This migration plan validation is static and read-only. RoboPilot did not "
    "modify migration plan files, modify source projects, generate migrated "
    "files, require ROS, require ROS2, run catkin_make, run colcon, execute "
    "launch files, execute code, or import user project modules."
)


@dataclass(frozen=True)
class MigrationPlanValidationReport:
    """Structured validation report for a migration plan file."""

    plan_path: str
    valid: bool
    missing_fields: tuple[str, ...]
    invalid_fields: tuple[str, ...]
    warnings: tuple[str, ...]
    suggested_next_steps: tuple[str, ...]
    safety_note: str

    def to_dict(self) -> dict[str, object]:
        """Return stable JSON-ready data."""
        return {
            "plan_path": self.plan_path,
            "valid": self.valid,
            "missing_fields": list(self.missing_fields),
            "invalid_fields": list(self.invalid_fields),
            "warnings": list(self.warnings),
            "suggested_next_steps": list(self.suggested_next_steps),
            "safety_note": self.safety_note,
        }


def validate_migration_plan_file(plan_path: Path) -> MigrationPlanValidationReport:
    """Validate a serialized migration plan without modifying it."""
    try:
        plan = load_migration_plan(plan_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return MigrationPlanValidationReport(
            plan_path=str(plan_path),
            valid=False,
            missing_fields=(),
            invalid_fields=(f"plan could not be loaded: {exc}",),
            warnings=(),
            suggested_next_steps=("Fix the migration plan syntax and run validation again.",),
            safety_note=SAFETY_NOTE,
        )
    return validate_migration_plan_data(plan, plan_path=plan_path)


def validate_migration_plan_data(
    plan: dict[str, object],
    *,
    plan_path: Path,
) -> MigrationPlanValidationReport:
    """Validate migration plan data with stable field-level diagnostics."""
    missing_fields = tuple(field for field in TOP_LEVEL_FIELDS if field not in plan)
    invalid: list[str] = []

    for field in LIST_FIELDS:
        if field in plan and not isinstance(plan[field], list):
            invalid.append(f"{field} must be a list")

    for field in (
        "generated_by",
        "source_path",
        "target",
        "source_project_type",
        "package_name",
        "confidence",
        "summary",
        "safety_note",
    ):
        if field in plan and not isinstance(plan[field], str):
            invalid.append(f"{field} must be a string")

    if "dependency_migration" in plan and not isinstance(plan["dependency_migration"], dict):
        invalid.append("dependency_migration must be a mapping")

    target = str(plan.get("target", "")).strip().lower()
    if "target" in plan and target not in SUPPORTED_TARGETS:
        invalid.append("target must be ros2")

    warnings = _warnings(plan)
    valid = not missing_fields and not invalid
    return MigrationPlanValidationReport(
        plan_path=str(plan_path),
        valid=valid,
        missing_fields=missing_fields,
        invalid_fields=tuple(sorted(dict.fromkeys(invalid))),
        warnings=warnings,
        suggested_next_steps=_suggested_next_steps(valid, missing_fields, invalid),
        safety_note=SAFETY_NOTE,
    )


def _warnings(plan: dict[str, object]) -> tuple[str, ...]:
    warnings: list[str] = []
    source_path = str(plan.get("source_path", "")).strip()
    if source_path and Path(source_path).exists():
        warnings.append("source_path exists on this machine; validation did not inspect or modify it")
    confidence = str(plan.get("confidence", "")).strip().lower()
    if confidence in {"low", "none"}:
        warnings.append(f"migration plan confidence is {confidence}")
    source_type = str(plan.get("source_project_type", "")).strip()
    if source_type and source_type != "ros1_catkin_package":
        warnings.append(f"source_project_type is {source_type}; review plan assumptions carefully")
    return tuple(sorted(dict.fromkeys(warnings)))


def _suggested_next_steps(
    valid: bool,
    missing_fields: tuple[str, ...],
    invalid_fields: list[str],
) -> tuple[str, ...]:
    if valid:
        return (
            "Review the migration plan before running migrate-preview.",
            "Run robopilot migrate-plan-diff when comparing plan revisions.",
        )
    steps: list[str] = []
    if missing_fields:
        steps.append("Regenerate the migration plan or restore the missing required fields.")
    if invalid_fields:
        steps.append("Fix invalid field types or unsupported values and validate again.")
    return tuple(steps)
