# JSON Contracts

This document describes the documented JSON outputs intended for integrations such as a future VSCode extension.

Scope:

- Stable means the documented top-level keys are intended for integration use.
- Essential nested structures are documented where useful.
- Heuristic text, ordering inside advisory lists, and undocumented nested details may evolve.
- Human-readable Rich output is not a machine contract.

External tools should prefer `--json` or documented JSON file formats instead of parsing terminal prose.

## `detect --json`

Purpose: detect the project category using static file signals.

Example:

```bash
robopilot detect path/to/project --json
```

Top-level stable keys:

- `project_path`
- `exists`
- `project_type`
- `confidence`
- `detected_signals`
- `missing_common_files`
- `notes`
- `suggested_next_steps`

Experimental fields: individual signal wording and confidence heuristics.

Safety notes: read-only; does not import project modules or execute files.

Minimal output:

```json
{
  "project_path": "path/to/project",
  "exists": true,
  "project_type": "robopilot_project",
  "confidence": "high",
  "detected_signals": ["robopilot.yaml"],
  "missing_common_files": [],
  "notes": [],
  "suggested_next_steps": []
}
```

## `inspect --json`

Purpose: statically inspect a RoboPilot-generated or ROS-style project.

Example:

```bash
robopilot inspect examples/generated_projects/demo_detector --json
```

Top-level stable keys:

- `project_path`
- `exists`
- `is_empty`
- `package_name`
- `spec`
- `files`
- `issues`
- `suggested_next_steps`

Essential nested keys:

- `spec`: `exists`, `valid`, `selected_template`, `errors`
- `files`: `package_xml`, `setup_py`, `setup_cfg`, `readme`, `launch_files`, `config_files`, `python_node_files`

Experimental fields: issue wording and suggested next steps.

Safety notes: read-only; does not execute generated code or launch files.

Minimal output:

```json
{
  "project_path": "examples/generated_projects/demo_detector",
  "exists": true,
  "is_empty": false,
  "package_name": "demo_detector",
  "spec": {
    "exists": true,
    "valid": true,
    "selected_template": "object_detection",
    "errors": []
  },
  "files": {
    "package_xml": true,
    "setup_py": true,
    "setup_cfg": true,
    "readme": true,
    "launch_files": ["launch/demo_detector.launch.py"],
    "config_files": ["config/params.yaml"],
    "python_node_files": ["demo_detector/detector_node.py"]
  },
  "issues": [],
  "suggested_next_steps": []
}
```

## `inspect-ros1 --json`

Purpose: statically inspect a ROS1 catkin package.

Example:

```bash
robopilot inspect-ros1 path/to/ros1_package --json
```

Top-level stable keys:

- `project_path`
- `exists`
- `package_name`
- `package_format`
- `detected_project_type`
- `dependencies`
- `catkin`
- `files`
- `nodes`
- `rospy_usage`
- `roscpp_usage`
- `issues`
- `suggested_next_steps`
- `safety_note`

Essential nested keys:

- `dependencies`: `buildtool`, `build`, `exec`, `run`
- `catkin`: `find_package_catkin`, `catkin_components`, `catkin_package`
- `files`: `launch_files`, `msg_files`, `srv_files`, `action_files`, `python_files`, `cpp_files`
- `nodes`: `python_node_candidates`, `cpp_node_candidates`

Experimental fields: node candidate heuristics and issue wording.

Safety notes: read-only; does not require ROS or run `catkin_make`.

Minimal output:

```json
{
  "project_path": "path/to/ros1_package",
  "exists": true,
  "package_name": "demo_pkg",
  "package_format": "2",
  "detected_project_type": "ros1_catkin_package",
  "dependencies": {
    "buildtool": ["catkin"],
    "build": ["rospy"],
    "exec": ["rospy"],
    "run": []
  },
  "catkin": {
    "find_package_catkin": true,
    "catkin_components": ["rospy"],
    "catkin_package": true
  },
  "files": {
    "launch_files": [],
    "msg_files": [],
    "srv_files": [],
    "action_files": [],
    "python_files": ["scripts/talker.py"],
    "cpp_files": []
  },
  "nodes": {
    "python_node_candidates": ["scripts/talker.py"],
    "cpp_node_candidates": []
  },
  "rospy_usage": true,
  "roscpp_usage": false,
  "issues": [],
  "suggested_next_steps": [],
  "safety_note": "Static inspection only."
}
```

## `inspect-ros2 --json`

Purpose: statically inspect a ROS2 ament Python or ament CMake package.

Example:

```bash
robopilot inspect-ros2 path/to/ros2_package --json
```

Top-level stable keys:

- `project_path`
- `exists`
- `package_name`
- `package_format`
- `detected_project_type`
- `dependencies`
- `build_system`
- `files`
- `nodes`
- `rclpy_usage`
- `rclcpp_usage`
- `issues`
- `suggested_next_steps`
- `safety_note`

Essential nested keys:

- `dependencies`: `buildtool`, `build`, `exec`, `test`
- `build_system`: `ament_cmake`, `ament_python`, `ament_package`, `setup_py`, `setup_cfg`, `resource_marker`
- `files`: `launch_files`, `config_files`, `msg_files`, `srv_files`, `action_files`, `python_files`, `cpp_files`
- `nodes`: `python_node_candidates`, `cpp_node_candidates`

Experimental fields: node candidate heuristics, issue wording, and partial ROS2 structure warnings.

Safety notes: read-only; does not require ROS2 or run `colcon`.

Minimal output:

```json
{
  "project_path": "path/to/ros2_package",
  "exists": true,
  "package_name": "demo_pkg",
  "package_format": "3",
  "detected_project_type": "ros2_ament_python_package",
  "dependencies": {
    "buildtool": [],
    "build": [],
    "exec": ["rclpy"],
    "test": []
  },
  "build_system": {
    "ament_cmake": false,
    "ament_python": true,
    "ament_package": false,
    "setup_py": true,
    "setup_cfg": true,
    "resource_marker": true
  },
  "files": {
    "launch_files": [],
    "config_files": [],
    "msg_files": [],
    "srv_files": [],
    "action_files": [],
    "python_files": ["demo_pkg/node.py"],
    "cpp_files": []
  },
  "nodes": {
    "python_node_candidates": ["demo_pkg/node.py"],
    "cpp_node_candidates": []
  },
  "rclpy_usage": true,
  "rclcpp_usage": false,
  "issues": [],
  "suggested_next_steps": [],
  "safety_note": "Static inspection only."
}
```

## `deps --json`

Purpose: analyze declared dependencies and detected dependency usage.

Example:

```bash
robopilot deps path/to/project --json
```

Top-level stable keys:

- `project_path`
- `exists`
- `project_type`
- `declared_dependencies`
- `detected_usage`
- `inferred_dependencies`
- `possibly_missing`
- `possibly_unused`
- `hints`
- `migration_hints`
- `rosdep_hints`
- `warnings`
- `suggested_next_steps`
- `safety_note`

Essential nested keys:

- `declared_dependencies`: `buildtool`, `build`, `exec`, `run`, `test`
- `detected_usage`: `python_imports`, `cpp_includes`, `cmake_find_package`, `catkin_components`, `launch_references`

Experimental fields: inference rules, warning wording, nested dependency details, and hint wording. The top-level keys are documented for integration use, but individual heuristic messages may evolve.

Safety notes: read-only and conservative; no ROS environment is required.

Minimal output:

```json
{
  "project_path": "path/to/project",
  "exists": true,
  "project_type": "ros1_catkin_package",
  "declared_dependencies": {
    "buildtool": ["catkin"],
    "build": [],
    "exec": ["rospy"],
    "run": [],
    "test": []
  },
  "detected_usage": {
    "python_imports": ["rospy"],
    "cpp_includes": [],
    "cmake_find_package": [],
    "catkin_components": [],
    "launch_references": []
  },
  "inferred_dependencies": ["rospy"],
  "possibly_missing": [],
  "possibly_unused": [],
  "hints": [],
  "migration_hints": ["migration_hint: ROS1 dependency 'rospy' should be reviewed for ROS2 direction: rclpy"],
  "rosdep_hints": ["rosdep_hint: Python import 'rospy' may require rospy"],
  "warnings": [],
  "suggested_next_steps": [],
  "safety_note": "Static analysis only."
}
```

## `migrate-plan --format json`

Purpose: write a static ROS1-to-ROS2 migration plan as JSON.

Example:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.json --format json
```

Top-level stable keys:

- `generated_by`
- `source_path`
- `target`
- `source_project_type`
- `package_name`
- `confidence`
- `summary`
- `package_xml_migration`
- `build_system_migration`
- `source_code_migration`
- `launch_migration`
- `interface_migration`
- `dependency_migration`
- `suggested_file_changes`
- `manual_review_items`
- `risks`
- `suggested_next_steps`
- `safety_note`

Experimental fields: migration advice wording, risk wording, and dependency migration detail structure.

Safety notes: writes only the explicit output plan file; does not modify the source project.

Minimal output:

```json
{
  "generated_by": "RoboPilot ROS1ToROS2MigrationPlan",
  "source_path": "path/to/ros1_package",
  "target": "ros2",
  "source_project_type": "ros1_catkin_package",
  "package_name": "demo_pkg",
  "confidence": "medium",
  "summary": "Static ROS1-to-ROS2 migration plan.",
  "package_xml_migration": [],
  "build_system_migration": [],
  "source_code_migration": [],
  "launch_migration": [],
  "interface_migration": [],
  "dependency_migration": {},
  "suggested_file_changes": [],
  "manual_review_items": [],
  "risks": [],
  "suggested_next_steps": [],
  "safety_note": "Static plan only."
}
```

## `migrate-plan-validate --json`

Purpose: validate a migration plan file.

Example:

```bash
robopilot migrate-plan-validate --plan migration_plan.yaml --json
```

Top-level stable keys:

- `plan_path`
- `valid`
- `missing_fields`
- `invalid_fields`
- `warnings`
- `suggested_next_steps`
- `safety_note`

Experimental fields: warning wording and suggested next steps.

Safety notes: read-only; does not require the source path to exist.

Minimal output:

```json
{
  "plan_path": "migration_plan.yaml",
  "valid": true,
  "missing_fields": [],
  "invalid_fields": [],
  "warnings": [],
  "suggested_next_steps": [],
  "safety_note": "Static validation only."
}
```

## `migrate-plan-diff --json`

Purpose: compare two migration plan files.

Example:

```bash
robopilot migrate-plan-diff --old migration_plan_v1.yaml --new migration_plan_v2.yaml --json
```

Top-level stable keys:

- `old_plan`
- `new_plan`
- `valid`
- `has_changes`
- `changed_fields`
- `added_items`
- `removed_items`
- `unchanged_fields`
- `warnings`
- `safety_note`

Experimental fields: nested diff grouping for advisory sections.

Safety notes: read-only; does not modify either plan.

Minimal output:

```json
{
  "old_plan": "migration_plan_v1.yaml",
  "new_plan": "migration_plan_v2.yaml",
  "valid": true,
  "has_changes": false,
  "changed_fields": {},
  "added_items": {},
  "removed_items": {},
  "unchanged_fields": ["target"],
  "warnings": [],
  "safety_note": "Static diff only."
}
```

## `migrate-preview --json`

Purpose: preview file-level ROS1-to-ROS2 migration work from a migration plan.

Example:

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package --json
```

Top-level stable keys:

- `plan_path`
- `project_path`
- `source_project_type`
- `target`
- `package_name`
- `files_to_create`
- `files_to_update`
- `files_to_keep`
- `files_requiring_manual_migration`
- `interface_files_to_review`
- `dependency_items_to_review`
- `conflicts`
- `risks`
- `suggested_next_steps`
- `safety_note`

Experimental fields: migration classification heuristics, risk wording, and dependency review wording.

Safety notes: read-only; does not generate migrated files.

Minimal output:

```json
{
  "plan_path": "migration_plan.yaml",
  "project_path": "path/to/ros1_package",
  "source_project_type": "ros1_catkin_package",
  "target": "ros2",
  "package_name": "demo_pkg",
  "files_to_create": ["package.xml", "CMakeLists.txt"],
  "files_to_update": [],
  "files_to_keep": ["msg/Demo.msg"],
  "files_requiring_manual_migration": ["scripts/talker.py"],
  "interface_files_to_review": ["msg/Demo.msg"],
  "dependency_items_to_review": [],
  "conflicts": [],
  "risks": [],
  "suggested_next_steps": [],
  "safety_note": "Read-only preview."
}
```

## `migrate-scaffold-preview --json`

Purpose: preview the future ROS2 target package scaffold implied by a migration plan.

Example:

```bash
robopilot migrate-scaffold-preview --plan migration_plan.yaml --json
```

Top-level stable keys:

- `plan_path`
- `source_path`
- `target`
- `package_name`
- `target_style`
- `scaffold_files_to_create`
- `placeholder_files`
- `files_requiring_manual_migration`
- `interface_files_to_review`
- `dependency_items_to_review`
- `build_system_notes`
- `launch_notes`
- `risks`
- `conflicts`
- `suggested_next_steps`
- `safety_note`

Essential nested keys:

- `scaffold_files_to_create` items: `path`, `purpose`, `source_basis`, `status`
- `placeholder_files` items: `path`, `purpose`, `source_basis`, `status`

Experimental fields: target-style inference, scaffold classification heuristics, advisory wording, and placeholder naming.

Safety notes: read-only; does not generate scaffold files or modify the source project or migration plan.

Minimal output:

```json
{
  "plan_path": "migration_plan.yaml",
  "source_path": "path/to/ros1_package",
  "target": "ros2",
  "package_name": "demo_pkg",
  "target_style": "ament_python",
  "scaffold_files_to_create": [
    {
      "path": "package.xml",
      "purpose": "ROS2 package metadata",
      "source_basis": "package_xml_migration",
      "status": "planned"
    }
  ],
  "placeholder_files": [],
  "files_requiring_manual_migration": ["scripts/talker.py"],
  "interface_files_to_review": ["msg/Demo.msg"],
  "dependency_items_to_review": [],
  "build_system_notes": [],
  "launch_notes": [],
  "risks": [],
  "conflicts": [],
  "suggested_next_steps": [],
  "safety_note": "Read-only scaffold preview."
}
```

## `migrate-scaffold --json`

Purpose: generate a conservative ROS2 scaffold from a migration plan and return the generation summary.

Example:

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold --json
```

Top-level stable keys:

- `plan_path`
- `output_path`
- `source_path`
- `target`
- `package_name`
- `target_style`
- `dry_run`
- `files_to_create`
- `files_created`
- `conflicts`
- `skipped_files`
- `manual_migration_required`
- `interface_files_to_review`
- `dependency_items_to_review`
- `risks`
- `suggested_next_steps`
- `safety_note`

Experimental fields: target-style inference, placeholder file naming, risk wording, and manual migration guidance.

Safety notes: writes only to the explicit output directory, refuses to overwrite existing files by default, does not modify the original ROS1 source project or migration plan, and generates placeholders rather than a full automatic migration.

Minimal output:

```json
{
  "plan_path": "migration_plan.yaml",
  "output_path": "path/to/ros2_scaffold",
  "source_path": "path/to/ros1_package",
  "target": "ros2",
  "package_name": "demo_pkg",
  "target_style": "ament_python",
  "dry_run": false,
  "files_to_create": ["package.xml", "setup.py", "MIGRATION_NOTES.md"],
  "files_created": ["package.xml", "setup.py", "MIGRATION_NOTES.md"],
  "conflicts": [],
  "skipped_files": [],
  "manual_migration_required": ["scripts/talker.py"],
  "interface_files_to_review": ["msg/Demo.msg"],
  "dependency_items_to_review": [],
  "risks": [],
  "suggested_next_steps": [],
  "safety_note": "Scaffold generation only."
}
```

## `migrate-scaffold-validate --json`

Purpose: validate a generated migration scaffold against a migration plan and RoboPilot scaffold expectations.

Example:

```bash
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --json
```

Top-level stable keys:

- `plan_path`
- `scaffold_path`
- `source_path`
- `target`
- `package_name`
- `target_style`
- `valid`
- `expected_files`
- `present_files`
- `missing_files`
- `unexpected_files`
- `placeholder_checks`
- `migration_notes_present`
- `ros2_inspection_summary`
- `issues`
- `warnings`
- `suggested_next_steps`
- `safety_note`

Essential nested keys:

- `placeholder_checks` items: `path`, `passed`, `missing_concepts`
- `ros2_inspection_summary`: `exists`, `package_name`, `detected_project_type`, `build_system`, `files`, `nodes`, `issues`

Experimental fields: placeholder concept labels, ROS2 inspection warning wording, and unexpected-file policy.

Safety notes: read-only; does not modify the scaffold, source project, or migration plan. It does not require ROS/ROS2, run build tools, execute launch files, execute generated code, or import generated scaffold modules.

Minimal output:

```json
{
  "plan_path": "migration_plan.yaml",
  "scaffold_path": "path/to/ros2_scaffold",
  "source_path": "path/to/ros1_package",
  "target": "ros2",
  "package_name": "demo_pkg",
  "target_style": "ament_python",
  "valid": true,
  "expected_files": ["package.xml", "setup.py", "MIGRATION_NOTES.md"],
  "present_files": ["package.xml", "setup.py", "MIGRATION_NOTES.md"],
  "missing_files": [],
  "unexpected_files": [],
  "placeholder_checks": [],
  "migration_notes_present": true,
  "ros2_inspection_summary": {
    "exists": true,
    "package_name": "demo_pkg",
    "detected_project_type": "ros2_ament_python_package",
    "build_system": {},
    "files": {},
    "nodes": {},
    "issues": []
  },
  "issues": [],
  "warnings": [],
  "suggested_next_steps": [],
  "safety_note": "Read-only scaffold validation."
}
```

## `apply-preview --json`

Purpose: compare a ProjectSpec with a project directory before apply.

Example:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector --json
```

Top-level stable keys:

- `spec_path`
- `project_path`
- `package_name`
- `selected_template`
- `files_to_create`
- `files_to_update`
- `files_to_keep`
- `conflicts`
- `missing_project`
- `safety_note`
- `suggested_next_steps`

Experimental fields: conflict wording and suggested next steps.

Safety notes: read-only; does not modify the project.

Minimal output:

```json
{
  "spec_path": "refined.yaml",
  "project_path": "outputs/demo_detector",
  "package_name": "demo_detector",
  "selected_template": "object_detection",
  "files_to_create": [],
  "files_to_update": ["robopilot.yaml"],
  "files_to_keep": ["package.xml"],
  "conflicts": [],
  "missing_project": false,
  "safety_note": "Preview only.",
  "suggested_next_steps": []
}
```

## `apply --json`

Purpose: dry-run or apply a validated apply plan and return a summary.

Example:

```bash
robopilot apply --plan apply_plan.yaml --json
robopilot apply --plan apply_plan.yaml --confirm --json
```

Top-level stable keys:

- `plan_path`
- `project_path`
- `dry_run`
- `files_created`
- `files_updated`
- `files_kept`
- `backups_created`
- `skipped_files`
- `conflicts`
- `safety_note`

Experimental fields: safety note wording and skipped file wording.

Safety notes: dry-run by default. Confirmed apply writes only files listed in a valid apply plan and backs up updated files.

Minimal output:

```json
{
  "plan_path": "apply_plan.yaml",
  "project_path": "outputs/demo_detector",
  "dry_run": true,
  "files_created": ["package.xml"],
  "files_updated": [],
  "files_kept": [],
  "backups_created": [],
  "skipped_files": [],
  "conflicts": [],
  "safety_note": "Dry-run by default."
}
```

## `rollback --json`

Purpose: dry-run or restore files from a RoboPilot backup directory.

Example:

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --json
```

Top-level stable keys:

- `project_path`
- `backup_path`
- `dry_run`
- `files_to_restore`
- `files_restored`
- `skipped_files`
- `errors`
- `safety_note`

Experimental fields: error wording and skipped file wording.

Safety notes: dry-run by default. Confirmed rollback restores only files present in the selected RoboPilot backup and does not delete newly created files.

Minimal output:

```json
{
  "project_path": "outputs/demo_detector",
  "backup_path": "outputs/demo_detector/.robopilot_backups/20260511_120000",
  "dry_run": true,
  "files_to_restore": ["README.md"],
  "files_restored": [],
  "skipped_files": [],
  "errors": [],
  "safety_note": "Rollback is dry-run by default."
}
```

## `history --json`

Purpose: read project-local apply and rollback history.

Example:

```bash
robopilot history --project outputs/demo_detector --json
```

Top-level stable keys:

- `project_path`
- `history_dir`
- `entries`

Essential entry keys:

- `id`
- `operation`
- `timestamp`
- `project_path`
- `plan_path`
- `backup_path`
- `dry_run`
- `success`
- `files_created`
- `files_updated`
- `files_restored`
- `files_kept`
- `conflicts`
- `skipped_files`
- `summary`

Experimental fields: summary wording.

Safety notes: read-only. Confirmed apply and rollback write history metadata under `.robopilot_history/`.

Minimal output:

```json
{
  "project_path": "outputs/demo_detector",
  "history_dir": "outputs/demo_detector/.robopilot_history",
  "entries": []
}
```

## `repair-suggest --json`

Purpose: return read-only repair suggestions for project inspection issues.

Example:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector --json
```

Top-level stable keys:

- `project_path`
- `issues`
- `repair_suggestions`
- `safety_note`
- `suggested_commands`

Essential repair suggestion keys:

- `issue`
- `suggestion`
- `severity`

Experimental fields: suggestion wording, severity mapping, and suggested commands.

Safety notes: read-only; does not implement automatic repair.

Minimal output:

```json
{
  "project_path": "examples/generated_projects/demo_detector",
  "issues": [],
  "repair_suggestions": [],
  "safety_note": "RoboPilot repair-suggest does not modify files automatically.",
  "suggested_commands": []
}
```
