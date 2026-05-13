"""Static migration planning helpers."""

from robopilot.migration.plan_diff import MigrationPlanDiffResult, diff_migration_plans
from robopilot.migration.plan_validator import (
    MigrationPlanValidationReport,
    validate_migration_plan_file,
)
from robopilot.migration.preview import MigrationPreviewResult, preview_migration
from robopilot.migration.scaffold_generator import (
    MigrationScaffoldGenerationResult,
    generate_migration_scaffold,
)
from robopilot.migration.scaffold_preview import (
    MigrationScaffoldPreviewResult,
    preview_migration_scaffold,
)
from robopilot.migration.scaffold_validator import (
    MigrationScaffoldValidationResult,
    validate_migration_scaffold,
)
from robopilot.migration.ros1_to_ros2 import (
    MigrationPlanValidationResult,
    ROS1ToROS2MigrationPlan,
    generate_migration_plan,
    load_migration_plan,
    validate_migration_plan,
    write_migration_plan,
)

__all__ = [
    "MigrationPlanDiffResult",
    "MigrationPlanValidationReport",
    "MigrationPlanValidationResult",
    "MigrationPreviewResult",
    "MigrationScaffoldGenerationResult",
    "MigrationScaffoldPreviewResult",
    "MigrationScaffoldValidationResult",
    "ROS1ToROS2MigrationPlan",
    "diff_migration_plans",
    "generate_migration_plan",
    "generate_migration_scaffold",
    "load_migration_plan",
    "preview_migration",
    "preview_migration_scaffold",
    "validate_migration_scaffold",
    "validate_migration_plan_file",
    "validate_migration_plan",
    "write_migration_plan",
]
