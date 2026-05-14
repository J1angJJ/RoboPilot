# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects.

It helps robotics learners and developers plan, refine, validate, generate, inspect, update, roll back, document, and review ROS/ROS2-style project structure without installing ROS, ROS2, catkin, colcon, simulator runtimes, or robot hardware.

## What RoboPilot Does

- Creates and validates `ProjectSpec` files from robotics tasks.
- Renders deterministic ROS-style Python package skeletons.
- Refines and diffs specs before generation.
- Previews, exports, applies, backs up, rolls back, and journals safe project updates.
- Inspects projects and exports read-only reports.
- Detects RoboPilot, ROS1, ROS2, mixed, non-ROS, and unknown project types.
- Statically inspects ROS1 catkin and ROS2 ament packages.
- Analyzes declared and detected dependencies.
- Builds static ROS1-to-ROS2 migration plans, validates/diffs them, previews file-level migration work, generates conservative ROS2 scaffold placeholders, validates generated scaffolds, and exports scaffold reports.
- Provides small offline utilities for robotics error logs and Mermaid workflow graphs.
- Optionally uses an LLM only to produce or refine validated `ProjectSpec` data.
- Provides a lightweight Python API layer for scripts and future integrations.
- Documents stable top-level JSON keys for integration-oriented `--json` outputs.
- Includes a VSCode extension source tree that wraps the RoboPilot CLI JSON outputs, including the migration scaffold review workflow.

RoboPilot does not run ROS, ROS2, launch files, generated code, `catkin_make`, or `colcon`.

## Quick Start

Supported Python versions for this release line are Python 3.10 and 3.11. Package metadata declares `>=3.10,<3.12`; Python 3.12 and 3.13 are not claimed until the test suite passes there.

Install from source for now:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[dev]"
robopilot --help
```

After PyPI release:

```bash
pip install robopilot
robopilot --help
```

On Windows, if pytest has temporary directory permission issues:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## Core Workflows

Spec-first generation:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

Iterative spec review:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
```

Safe project update loop:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot history --project outputs/demo_detector
```

Static project review:

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

ROS-style static analysis:

```bash
robopilot detect path/to/project
robopilot inspect-ros1 path/to/ros1_package
robopilot inspect-ros2 path/to/ros2_package
robopilot deps path/to/project
```

ROS1 to ROS2 migration planning:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
robopilot migrate-scaffold-preview --plan migration_plan.yaml
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
```

## Documentation

- [Chinese Documentation](docs/zh-CN/README.md)
- [Command Reference](docs/command_reference.md)
- [Workflows](docs/workflows.md)
- [Architecture](docs/architecture.md)
- [Python API](docs/api.md)
- [JSON Contracts](docs/json_contracts.md)
- [Integration Notes](docs/integration_notes.md)
- [VSCode Extension](docs/vscode_extension.md)
- [VSCode Packaging](docs/vscode_packaging.md)
- [VSCode Marketplace Publishing](docs/vscode_marketplace.md)
- [ROS1 to ROS2 Migration Tutorial](docs/tutorial_ros1_to_ros2_migration.md)
- [VSCode Migration Tutorial](docs/tutorial_vscode_migration_workflow.md)
- [Demo Walkthrough](docs/demo_walkthrough.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Developer Setup](docs/developer_setup.md)
- [Testing](docs/testing.md)
- [Release Process](docs/release_process.md)
- [PyPI Publishing](docs/pypi_publish.md)
- [Compatibility](docs/compatibility.md)
- [Known Limitations](docs/known_limitations.md)
- [Stability Policy](docs/stability_policy.md)
- [Demo Script](docs/demo_script.md)
- [v1.0.0 Scope](docs/v1_scope.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](roadmap.md)

## Safety Model

RoboPilot is designed around static analysis and explicit review:

- Default planning, validation, diff, inspection, report, detection, dependency, and migration commands are read-only.
- `apply` is dry-run by default and writes only with `--confirm`.
- Confirmed updates write only files listed in a validated apply plan.
- Existing files are backed up before updates.
- `rollback` is dry-run by default and restores only files from RoboPilot backup directories.
- Migration planning, validation, diff, and preview do not modify source projects.
- Migration scaffold generation writes only to the explicit output directory, refuses overwrites by default, and does not modify the original ROS1 project.
- Migration scaffold validation is read-only and checks generated placeholders without executing or importing scaffold code.
- Migration scaffold reports are read-only unless writing to an explicit report output file.
- Optional LLM paths are limited to `ProjectSpec` planning/refinement and must pass validation before generation or apply workflows.

## Example Output

A static generated demo project is committed at:

```txt
examples/generated_projects/demo_detector/
```

Migration tutorial examples are committed at:

```txt
examples/ros1_migration_demo/
examples/ros2_scaffold_demo/
examples/migration_outputs/
```

Start with [the ROS1-to-ROS2 migration tutorial](docs/tutorial_ros1_to_ros2_migration.md), the [VSCode migration tutorial](docs/tutorial_vscode_migration_workflow.md), or the [demo walkthrough](docs/demo_walkthrough.md).

Transient generated projects should go under `outputs/`, which is intentionally ignored by git.

## Project Status

Current release line: `v1.17.0`.

RoboPilot's no-ROS-required static engineering workflow remains the stable v1 baseline:

```txt
plan -> refine -> diff -> validate -> generate
      -> apply-preview -> apply-plan -> apply -> rollback -> history
      -> inspect -> repair-suggest -> report
      -> detect -> inspect-ros1 -> inspect-ros2 -> deps
      -> migrate-plan -> migrate-plan-validate -> migrate-plan-diff -> migrate-preview
      -> migrate-scaffold-preview -> migrate-scaffold -> migrate-scaffold-validate
      -> migrate-scaffold-report
```

The Python API layer, documented CLI JSON contracts, ROS2 static inspector, enhanced dependency analyzer, and VSCode extension source are available for integration work while the CLI remains the primary user interface.

The VSCode extension lives under `vscode-extension/`, requires the RoboPilot CLI to be installed, supports the migration scaffold workflow, and can be packaged locally as a VSIX. Marketplace publishing is prepared for extension id `j1angjj.robopilot-vscode`, but no Marketplace availability is claimed until listing verification succeeds. See [docs/vscode_extension.md](docs/vscode_extension.md), [docs/vscode_packaging.md](docs/vscode_packaging.md), and [docs/vscode_marketplace.md](docs/vscode_marketplace.md).

Final pre-v2.0 roadmap work is aimed at Chinese documentation expansion, VSCode Marketplace publishing, and stability / compatibility cleanup. v2.0 is intended as a stage-completion release for the current static toolchain, not a breaking rewrite unless a future release plan says so.

## Development

Run tests:

```bash
python -m pytest
```

Windows fallback:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## License

MIT
