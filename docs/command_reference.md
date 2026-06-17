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

Next step: run `robopilot migrate-plan-validate --plan migration_plan.yaml`, then `robopilot migrate-scaffold-preview --plan migration_plan.yaml`.

## `migrate-plan-validate`

Purpose: validate a migration plan.

Example:

```bash
robopilot migrate-plan-validate --plan migration_plan.yaml
```

Mode: read-only.

Safety notes: validates plan structure and supported target values without requiring the source path to exist.

Next step: if valid, run `robopilot migrate-scaffold-preview --plan migration_plan.yaml`.

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

Next step: after reviewing risks and conflicts, run `robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold`.

## `migrate-scaffold`

Purpose: generate a conservative ROS2 scaffold from a migration plan.

Example:

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
```

Mode: file-writing to the explicit `--output` directory.

Safety notes: does not modify the original ROS1 source project or migration plan. Existing scaffold files are not overwritten unless `--overwrite` is provided, and RoboPilot checks all intended paths before writing.

Next step: run `robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold`.

## `migrate-scaffold-validate`

Purpose: validate a generated ROS2 migration scaffold against its migration plan and RoboPilot scaffold expectations.

Example:

```bash
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
```

Mode: read-only.

Safety notes: does not modify the scaffold, source project, or migration plan. It statically checks expected files, placeholder safety wording, ROS2 scaffold structure, and unexpected files without importing generated modules or running ROS2 tooling.

Next step: run `robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md`.

## `migrate-scaffold-report`

Purpose: export a deterministic Markdown report for a generated ROS2 migration scaffold.

Example:

```bash
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
```

Mode: read-only when printed to stdout; file-writing only to the explicit `--output` report path.

Safety notes: reuses scaffold validation, does not modify the scaffold, source project, or migration plan, and does not run ROS, ROS2, `catkin_make`, `colcon`, launch files, generated code, or generated scaffold imports. Existing report files are not overwritten unless `--overwrite` is provided.

Next step: review `MIGRATION_NOTES.md`, `scaffold_report.md`, manual migration items, dependency items, and safety notes before editing ROS2 code.

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

## `lint`

Purpose: run static quality checks on a ROS project.

Example:

```bash
robopilot lint path/to/package
robopilot lint path/to/package --json
```

Mode: read-only.

Safety notes: static only; no ROS runtime.

## `launch-lint`

Purpose: validate launch files (ROS1 XML and ROS2 Python).

Example:

```bash
robopilot launch-lint path/to/package
```

Mode: read-only.

## `migrate-score`

Purpose: score a ROS1 package on ROS2 migration readiness (0-100).

Example:

```bash
robopilot migrate-score path/to/ros1_package
robopilot migrate-score path/to/ros1_package --json
```

Mode: read-only.

## `tutorial`

Purpose: run interactive step-by-step RoboPilot tutorials.

Example:

```bash
robopilot tutorial --list
robopilot tutorial --lesson demo_detector
robopilot tutorial --all
```

Mode: read-only except for explicit `generate` steps within lessons.

## `workspace`

Purpose: analyze a multi-package ROS workspace.

Example:

```bash
robopilot workspace path/to/catkin_ws/src
robopilot workspace path/to/catkin_ws/src --json
```

Mode: read-only.

## `template-init`

Purpose: scaffold a `.robopilot/templates/` directory.

Example:

```bash
robopilot template-init
```

Mode: file-writing (creates `.robopilot/templates/`).

## `template-validate`

Purpose: validate a custom template definition.

Example:

```bash
robopilot template-validate --path .robopilot/templates/my_template
```

Mode: read-only.

## `template-install`

Purpose: install a community template from a URL or file.

Example:

```bash
robopilot template-install https://example.com/template.yaml --name my_tpl
```

Mode: file-writing.

## `ci-check`

Purpose: run aggregated quality checks (lint + deps + launch) with SARIF/Markdown export.

Example:

```bash
robopilot ci-check path/to/package --format sarif --output report.sarif
robopilot ci-check path/to/package --json
```

Mode: read-only; file-writing when `--output` is provided. Exit codes 0/1/2 for CI.

## `doctor`

Purpose: self-diagnose the RoboPilot environment.

Example:

```bash
robopilot doctor
robopilot doctor --json
```

Mode: read-only.

## `schema`

Purpose: export a JSON Schema for the robopilot.yaml format.

Example:

```bash
robopilot schema
```

Mode: read-only (prints to stdout).

## JSON Output

Commands supporting `--json`: `diff`, `apply-preview`, `apply`, `rollback`, `history`, `detect`, `inspect`, `inspect-ros1`, `inspect-ros2`, `deps`, `lint`, `launch-lint`, `migrate-score`, `workspace`, `ci-check`, `doctor`, `migrate-plan-validate`, `migrate-plan-diff`, `migrate-preview`, `migrate-scaffold-preview`, `migrate-scaffold`, `migrate-scaffold-validate`, `repair-suggest`, `tutorial`. Some commands write JSON files via format options (`migrate-plan --format json`, `apply-plan --format json`). JSON keys are intended to be stable for tests and integrations.

For documented integration contracts, see [JSON Contracts](json_contracts.md). External tools should prefer `--json` and should not parse Rich human-readable output.
