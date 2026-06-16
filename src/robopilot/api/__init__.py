"""Public Python API for RoboPilot.

The API layer provides thin wrappers over RoboPilot core modules for scripts,
future editor integrations, and UI wrappers. It avoids Rich rendering and
stdout printing; CLI modules remain responsible for terminal presentation.
"""

from robopilot.api.apply import (
    apply_exported_plan,
    export_apply_plan,
    preview_apply,
    read_project_history,
    rollback_project_backup,
    validate_apply_plan_file,
)
from robopilot.api.migration import (
    create_ros1_to_ros2_migration_plan,
    diff_migration_plan_files,
    preview_migration_plan,
    score_migration_readiness_api,
    validate_migration_plan_file,
)
from robopilot.api.project import (
    diff_project_specs,
    generate_project,
    plan_project,
    refine_project_spec,
    validate_project_spec,
)
from robopilot.api.static_analysis import (
    analyze_project_dependencies,
    detect_project_type,
    export_project_report,
    inspect_project_static,
    inspect_ros1_project_static,
    lint_project_api,
)

__all__ = [
    "analyze_project_dependencies",
    "apply_exported_plan",
    "create_ros1_to_ros2_migration_plan",
    "detect_project_type",
    "diff_migration_plan_files",
    "diff_project_specs",
    "export_apply_plan",
    "export_project_report",
    "generate_project",
    "inspect_project_static",
    "inspect_ros1_project_static",
    "lint_project_api",
    "plan_project",
    "preview_apply",
    "preview_migration_plan",
    "read_project_history",
    "refine_project_spec",
    "rollback_project_backup",
    "score_migration_readiness_api",
    "validate_apply_plan_file",
    "validate_migration_plan_file",
    "validate_project_spec",
]
