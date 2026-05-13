# RoboPilot Workflows

This document shows the main RoboPilot workflows. All workflows are designed to work without ROS, ROS2, catkin, colcon, simulator runtimes, or robot hardware.

## Basic Spec-First Project Generation

Use `plan` to create a reviewable `ProjectSpec`, validate it, then generate a deterministic ROS-style package.

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

Use `generate --name --task` for the shorter compatibility path:

```bash
robopilot generate --name demo_detector --task "Create an object detection pipeline"
```

## Iterative Spec Refinement

Refinement writes a new spec and preserves the original.

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
robopilot validate --spec refined.yaml
```

The default refiner is rule-based and offline. Optional LLM refinement is constrained to validated `ProjectSpec` output.

## Safe Apply and Rollback

Use apply-preview and apply-plan before writing files.

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml
```

The first `apply` call is a dry-run. Add `--confirm` only after reviewing the plan.

```bash
robopilot apply --plan apply_plan.yaml --confirm
robopilot history --project outputs/demo_detector
```

If an updated file needs to be restored, use the backup created by confirmed apply:

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

Rollback does not delete newly created files in this version.

## Project Inspection and Report

Inspect project structure, get repair suggestions, and export a Markdown report.

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

These commands are static and do not execute project files.

## ROS Project Detection

Detect whether a directory looks like a RoboPilot project, ROS1 catkin package, ROS2 ament package, mixed ROS-style project, non-ROS project, or unknown project.

```bash
robopilot detect path/to/project
robopilot detect path/to/project --json
```

Detection is heuristic and conservative.

## ROS1 Static Inspection

Inspect ROS1 catkin package metadata and file structure without ROS.

```bash
robopilot inspect-ros1 path/to/ros1_package
robopilot inspect-ros1 path/to/ros1_package --json
```

The inspector reads `package.xml`, `CMakeLists.txt`, launch files, interfaces, Python files, and C++ files statically.

## ROS2 Static Inspection

Inspect ROS2 ament package metadata and file structure without ROS2.

```bash
robopilot inspect-ros2 path/to/ros2_package
robopilot inspect-ros2 path/to/ros2_package --json
```

The inspector reads `package.xml`, `CMakeLists.txt`, `setup.py`, `setup.cfg`, `resource/`, launch files, config files, interfaces, Python files, and C++ files statically.

## Dependency Analysis

Analyze declared dependencies and detected usage.

```bash
robopilot deps path/to/project
robopilot deps path/to/project --json
```

Dependency analysis reports conservative hints such as `possibly_missing`, `possibly_unused`, ROS/package-manager style hints, and ROS1-to-ROS2 migration-oriented dependency review notes.

## ROS1 to ROS2 Migration Planning

Generate a migration plan, validate it, compare revisions, and preview file-level work.

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-plan-diff --old migration_plan_v1.yaml --new migration_plan_v2.yaml
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
robopilot migrate-scaffold-preview --plan migration_plan.yaml
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
```

This workflow is read-only for the source ROS1 project. `migrate-preview` reports impact against the existing source project. `migrate-scaffold-preview` previews the ROS2 target package scaffold. `migrate-scaffold` writes conservative placeholder scaffold files only to the explicit output directory, refuses overwrites by default, and does not automatically migrate business logic. `migrate-scaffold-validate` is read-only and checks the generated scaffold against the plan before manual migration work continues. `migrate-scaffold-report` turns validation results into a Markdown report and writes only the explicit report file when `--output` is provided.

This completes the first migration scaffold review loop. Post-v1.10 work should focus on VSCode accessibility, examples, documentation, and UX polish for this existing loop rather than migration apply, automatic source conversion, ROS/ROS2 execution, colcon execution, or launch execution before v2.0.

## VSCode-Assisted Migration Scaffold Workflow

The VSCode extension can drive the same migration scaffold review loop through the RoboPilot CLI. It stores integration outputs under `.robopilot_vscode` by default:

```txt
RoboPilot: Generate Migration Plan
  -> RoboPilot: Preview Migration Scaffold
  -> RoboPilot: Generate Migration Scaffold
  -> RoboPilot: Validate Migration Scaffold
  -> RoboPilot: Generate Scaffold Report
  -> RoboPilot: Open Scaffold Report
```

The extension remains a thin wrapper over CLI JSON contracts and Markdown report output. It does not run ROS, ROS2, colcon, launch files, or generated code.

## Offline Utilities

Analyze common robotics error logs:

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

Generate a Mermaid pipeline graph:

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```
