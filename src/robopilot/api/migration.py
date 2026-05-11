"""Python API wrappers for RoboPilot migration planning features."""

from __future__ import annotations

from robopilot.api.models import PathLike, StructuredResult, normalize_path, to_structured_result
from robopilot.migration.plan_diff import MigrationPlanDiffResult, diff_migration_plans
from robopilot.migration.plan_validator import (
    MigrationPlanValidationReport,
    validate_migration_plan_file as core_validate_migration_plan_file,
)
from robopilot.migration.preview import MigrationPreviewResult, preview_migration
from robopilot.migration.ros1_to_ros2 import (
    ROS1ToROS2MigrationPlan,
    generate_migration_plan,
    write_migration_plan,
)


def create_ros1_to_ros2_migration_plan(
    source_path: PathLike,
    *,
    target: str = "ros2",
    output_path: PathLike | None = None,
    output_format: str = "yaml",
    as_dict: bool = True,
) -> StructuredResult | ROS1ToROS2MigrationPlan:
    """Create a ROS1-to-ROS2 migration plan, writing it only when requested."""
    normalized_source_path = normalize_path(source_path)
    if output_path is None:
        result = generate_migration_plan(normalized_source_path, target=target)
    else:
        result = write_migration_plan(
            source_path=normalized_source_path,
            target=target,
            output_path=normalize_path(output_path),
            output_format=output_format,
        )
    return to_structured_result(result) if as_dict else result


def validate_migration_plan_file(
    plan_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | MigrationPlanValidationReport:
    """Validate a migration plan without modifying files."""
    result = core_validate_migration_plan_file(normalize_path(plan_path))
    return to_structured_result(result) if as_dict else result


def diff_migration_plan_files(
    old_plan_path: PathLike,
    new_plan_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | MigrationPlanDiffResult:
    """Diff two migration plans without modifying either file."""
    result = diff_migration_plans(normalize_path(old_plan_path), normalize_path(new_plan_path))
    return to_structured_result(result) if as_dict else result


def preview_migration_plan(
    plan_path: PathLike,
    project_path: PathLike,
    *,
    as_dict: bool = True,
) -> StructuredResult | MigrationPreviewResult:
    """Preview file-level migration actions without generating migrated files."""
    result = preview_migration(normalize_path(plan_path), normalize_path(project_path))
    return to_structured_result(result) if as_dict else result
