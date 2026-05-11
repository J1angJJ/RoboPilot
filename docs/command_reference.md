# RoboPilot Command Reference

RoboPilot commands are static by default. Commands that can write files say so explicitly, and confirmed file-writing flows use reviewable plans or output paths.

## `plan`

Purpose: create a `ProjectSpec` from a package name and robotics task.

Example:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
```

Mode: file-writing only when `--output` is provided.

Safety notes: default planner is offline and rule-based. `--planner llm` is optional and must still return validated `ProjectSpec` data.

## `refine`

Purpose: refine an existing `ProjectSpec` into a new spec file.

Example:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

Mode: file-writing to the explicit `--output` path.

Safety notes: the original spec is not modified. LLM refinement is optional and must validate the refined spec before writing.

## `diff`

Purpose: compare two `ProjectSpec` files.

Example:

```bash
robopilot diff --old robopilot.yaml --new refined.yaml
```

Mode: read-only.

Safety notes: both specs are loaded and validated; no files are modified.

## `validate`

Purpose: validate a `ProjectSpec`.

Example:

```bash
robopilot validate --spec refined.yaml
```

Mode: read-only.

Safety notes: validation does not generate, modify, or execute project files.

## `generate`

Purpose: generate a deterministic ROS-style package from a spec or task.

Example:

```bash
robopilot generate --spec refined.yaml
```

Mode: file-writing under `outputs/` by default or under `--output-root`.

Safety notes: existing project directories are not overwritten unless `--overwrite` is provided.

## `apply-preview`

Purpose: compare a spec with an existing project and preview create/update/keep/conflict classifications.

Example:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
```

Mode: read-only.

Safety notes: does not modify the project directory.

## `apply-plan`

Purpose: export an apply-preview result into a reviewable plan.

Example:

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
```

Mode: file-writing to the explicit `--output` plan file.

Safety notes: does not modify the target project.

## `apply-plan-validate`

Purpose: validate an exported apply plan.

Example:

```bash
robopilot apply-plan-validate --plan apply_plan.yaml
```

Mode: read-only.

Safety notes: validation does not execute the plan.

## `apply`

Purpose: dry-run or safely apply a validated apply plan.

Example:

```bash
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
```

Mode: dry-run by default; file-writing only with `--confirm`.

Safety notes: before writing, RoboPilot validates the plan, reloads the spec, re-runs apply-preview, rejects stale plans and conflicts, writes only planned create/update files, and backs up updated files.

## `rollback`

Purpose: dry-run or restore files from a RoboPilot backup directory.

Example:

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

Mode: dry-run by default; file-writing only with `--confirm`.

Safety notes: restores only files contained in the backup and does not delete newly created files.

## `history`

Purpose: list project-local RoboPilot apply and rollback journal entries.

Example:

```bash
robopilot history --project outputs/demo_detector
```

Mode: read-only.

Safety notes: reads `.robopilot_history/`; confirmed apply and rollback write history metadata.

## `detect`

Purpose: detect whether a directory looks like a RoboPilot, ROS1, ROS2, mixed, non-ROS, or unknown project.

Example:

```bash
robopilot detect path/to/project
```

Mode: read-only.

Safety notes: static only; does not import project modules or execute files.

## `inspect`

Purpose: statically inspect a RoboPilot-generated or ROS-style project.

Example:

```bash
robopilot inspect examples/generated_projects/demo_detector
```

Mode: read-only.

Safety notes: inspects project files and spec metadata without running code.

## `inspect-ros1`

Purpose: statically inspect a ROS1 catkin package.

Example:

```bash
robopilot inspect-ros1 path/to/ros1_package
```

Mode: read-only.

Safety notes: does not require ROS, run `catkin_make`, execute launch files, or import user code.

## `inspect-ros2`

Purpose: statically inspect a ROS2 ament Python or ament CMake package.

Example:

```bash
robopilot inspect-ros2 path/to/ros2_package
```

Mode: read-only.

Safety notes: does not require ROS2, run `colcon`, execute launch files, or import user code.

## `deps`

Purpose: analyze declared and detected dependencies in ROS-style projects.

Example:

```bash
robopilot deps path/to/project
```

Mode: read-only.

Safety notes: dependency inference is conservative and static. `--json` includes stable top-level keys for `hints`, `migration_hints`, and `rosdep_hints`; the wording of individual heuristic messages may evolve.

## `migrate-plan`

Purpose: generate a static ROS1-to-ROS2 migration plan.

Example:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

Mode: file-writing to the explicit `--output` plan file.

Safety notes: does not modify the source project or generate migrated files.

## `migrate-plan-validate`

Purpose: validate a migration plan.

Example:

```bash
robopilot migrate-plan-validate --plan migration_plan.yaml
```

Mode: read-only.

Safety notes: validates plan structure and supported target values without requiring the source path to exist.

## `migrate-plan-diff`

Purpose: compare two migration plans.

Example:

```bash
robopilot migrate-plan-diff --old migration_plan_v1.yaml --new migration_plan_v2.yaml
```

Mode: read-only.

Safety notes: does not modify either plan.

## `migrate-preview`

Purpose: turn a migration plan into a file-level migration preview.

Example:

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

Mode: read-only.

Safety notes: does not generate migrated files or modify the source project.

## `migrate-scaffold-preview`

Purpose: preview the future ROS2 target scaffold implied by a migration plan.

Example:

```bash
robopilot migrate-scaffold-preview --plan migration_plan.yaml
```

Mode: read-only.

Safety notes: does not generate scaffold files, modify the source project, modify the migration plan, require ROS/ROS2, run build tools, or execute project code.

## `repair-suggest`

Purpose: suggest read-only repairs based on project inspection issues.

Example:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
```

Mode: read-only.

Safety notes: suggestions are advisory; no `--apply` behavior is implemented here.

## `report`

Purpose: generate a Markdown inspection and repair report.

Example:

```bash
robopilot report examples/generated_projects/demo_detector --output report.md
```

Mode: read-only when printed to terminal; file-writing when `--output` is provided.

Safety notes: static report generation does not run project code.

## `debug`

Purpose: analyze robotics error logs with offline rules.

Example:

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
robopilot debug --text "ModuleNotFoundError: No module named 'cv_bridge'"
```

Mode: read-only.

Safety notes: no LLM or external API is used.

## `graph`

Purpose: generate a Mermaid graph from an arrow-based robotics pipeline.

Example:

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

Mode: read-only when printed to terminal; file-writing when `--output` is provided.

Safety notes: graph generation is deterministic and offline.

## JSON Output

Several commands support `--json`, including `diff`, `apply-preview`, `apply`, `rollback`, `history`, `detect`, `inspect`, `inspect-ros1`, `inspect-ros2`, `deps`, `migrate-plan-validate`, `migrate-plan-diff`, `migrate-preview`, `migrate-scaffold-preview`, and `repair-suggest`. Some commands write JSON files via format options, such as `migrate-plan --format json` and `apply-plan --format json`. JSON keys are intended to be stable for tests and lightweight integrations.

For documented integration contracts, see [JSON Contracts](json_contracts.md). External tools should prefer `--json` and should not parse Rich human-readable output.
