# RoboPilot Architecture

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects. Its architecture favors deterministic intermediate representations, reviewable plans, and conservative file writing.

## No-ROS-Required Design

RoboPilot reads project files statically. It does not require or invoke:

- ROS or ROS2
- `catkin_make`
- `colcon`
- launch execution
- generated node execution
- imports from user project modules
- robot hardware or simulator runtimes

This keeps the tool usable on normal development machines and CI runners.

## ProjectSpec Workflow

`ProjectSpec` is the central representation for RoboPilot-generated project structure.

```txt
task text
  -> planner
  -> ProjectSpec
  -> validate
  -> render / diff / preview / apply
```

Generation and update workflows should not bypass validation. `robopilot.yaml` is both a generated metadata file and an input format for later generation.

## Planner and Refiner Architecture

The default planner and refiner are rule-based, offline, deterministic, and testable.

Optional LLM planning/refinement is constrained:

- LLMs may only produce ProjectSpec-compatible structured data.
- LLMs do not write files directly.
- LLMs do not generate arbitrary project source files directly.
- LLM output is parsed and validated before downstream use.

## Deterministic Rendering

The generator renders expected files from a validated `ProjectSpec`. Rendering is reusable:

- `generate` writes rendered files.
- `apply-preview` compares rendered files with an existing project.
- `apply` writes only files listed in a validated apply plan.

This avoids separate logic for generation and update preview.

## Apply Safety Chain

File updates move through a deliberate safety sequence:

```txt
ProjectSpec
  -> validate
  -> apply-preview
  -> apply-plan
  -> apply-plan-validate
  -> apply dry-run
  -> apply --confirm
  -> backup
  -> history
  -> rollback if needed
```

Confirmed apply re-runs preview and rejects stale plans or conflicts. Existing files are backed up before update. Rollback restores only files from RoboPilot backup directories and is dry-run by default.

## ROS Static Analysis Modules

RoboPilot includes no-ROS-required static modules for existing projects:

- `detector`: classifies project type from file and content signals.
- `ros1`: inspects ROS1 catkin package metadata and node candidates.
- `deps`: extracts declared dependencies, imports, includes, CMake packages, launch references, and conservative hints.
- `inspector`, `repair`, and `report`: inspect RoboPilot-generated or ROS-style projects and produce reviewable output.

These modules must not execute launch files, import user code, or run build tools.

## Migration Planning Modules

ROS1-to-ROS2 migration support is currently planning and preview only:

- `migrate-plan` creates a static migration plan from detection, ROS1 inspection, and dependency analysis.
- `migrate-plan-validate` checks plan shape and supported target values.
- `migrate-plan-diff` compares two migration plan revisions.
- `migrate-preview` turns a plan into conservative file-level preview categories.

Migration modules do not generate migrated files, modify the source project, or run ROS tooling.

## Optional LLM Boundaries

LLM features are optional and off by default. The safe boundary is:

```txt
LLM output
  -> ProjectSpec parsing
  -> ProjectSpec validation
  -> diff / preview
  -> deterministic rendering or plan-based apply
```

LLM components must not bypass validation, apply-preview, apply-plan, backups, or rollback.
