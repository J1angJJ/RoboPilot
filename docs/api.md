# Python API

RoboPilot includes a lightweight Python API layer for scripts, future VSCode integration, and possible UI wrappers.

The CLI remains the primary user interface. The API layer is intentionally thin: it reuses the same core modules as the CLI, avoids Rich rendering, avoids direct stdout printing, and returns dictionaries or existing RoboPilot result objects.

## Stability

The API is useful for integration work, but it is newer than the CLI. Until the API is explicitly marked stable, prefer treating function names and dictionary fields as provisional integration surfaces.

The API does not add runtime ROS behavior. It does not run ROS, ROS2, launch files, generated code, `catkin_make`, or `colcon`.

## API vs CLI JSON

Use the Python API for Python scripts and in-process integrations. Use CLI `--json` outputs for external tools such as a future VSCode extension, shell scripts, or non-Python clients.

Do not parse Rich human-readable CLI output. See [JSON Contracts](json_contracts.md) and [Integration Notes](integration_notes.md) for integration guidance.

Dependency analysis API results mirror `robopilot deps --json`, including conservative `migration_hints` and `rosdep_hints` fields. The top-level fields are documented for integrations; individual heuristic messages may evolve.

## Static Analysis Example

```python
from robopilot.api.static_analysis import detect_project_type

result = detect_project_type("examples/generated_projects/demo_detector")
print(result["project_type"])
```

ROS-specific static inspection is also available:

```python
from robopilot.api.static_analysis import inspect_ros2_project_static

result = inspect_ros2_project_static("path/to/ros2_package")
print(result["package_name"])
```

## ProjectSpec Example

```python
from robopilot.api.project import plan_project, validate_project_spec

spec = plan_project(
    "demo_detector",
    "Create an object detection pipeline",
    output_path="robopilot.yaml",
)

validation = validate_project_spec("robopilot.yaml")
print(validation["is_valid"])
```

## Migration Example

```python
from robopilot.api.migration import (
    create_ros1_to_ros2_migration_plan,
    preview_migration_plan,
    preview_migration_scaffold,
)

plan = create_ros1_to_ros2_migration_plan(
    "path/to/ros1_package",
    output_path="migration_plan.yaml",
)

preview = preview_migration_plan(
    "migration_plan.yaml",
    "path/to/ros1_package",
)
print(preview["files_requiring_manual_migration"])

scaffold = preview_migration_scaffold("migration_plan.yaml")
print(scaffold["target_style"])
```

## Apply Example

```python
from robopilot.api.apply import preview_apply, read_project_history

preview = preview_apply("refined.yaml", "outputs/demo_detector")
history = read_project_history("outputs/demo_detector")
```

`apply_exported_plan()` and `rollback_project_backup()` preserve RoboPilot's safety model. They are dry-run by default unless `confirm=True` is passed.

## API Groups

- `robopilot.api.project`: ProjectSpec planning, refinement, validation, diff, and generation wrappers.
- `robopilot.api.static_analysis`: project detection, inspection, ROS1 inspection, ROS2 inspection, dependency analysis, and report export wrappers.
- `robopilot.api.migration`: ROS1-to-ROS2 migration plan, validation, diff, and preview wrappers.
- `robopilot.api.apply`: apply-preview, apply-plan export/validation, apply, rollback, and history wrappers.
- `robopilot.api.models`: small helper aliases for path-like inputs and structured results.
