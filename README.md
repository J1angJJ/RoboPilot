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
- Statically inspects ROS1 catkin packages.
- Analyzes declared and detected dependencies.
- Builds static ROS1-to-ROS2 migration plans, validates/diffs them, and previews file-level migration work.
- Provides small offline utilities for robotics error logs and Mermaid workflow graphs.
- Optionally uses an LLM only to produce or refine validated `ProjectSpec` data.
- Provides a lightweight Python API layer for scripts and future integrations.

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
robopilot deps path/to/project
```

ROS1 to ROS2 migration planning:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

## Documentation

- [Command Reference](docs/command_reference.md)
- [Workflows](docs/workflows.md)
- [Architecture](docs/architecture.md)
- [Python API](docs/api.md)
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
- Optional LLM paths are limited to `ProjectSpec` planning/refinement and must pass validation before generation or apply workflows.

## Example Output

A static generated demo project is committed at:

```txt
examples/generated_projects/demo_detector/
```

Transient generated projects should go under `outputs/`, which is intentionally ignored by git.

## Project Status

Current release line: `v1.2.0`.

RoboPilot's no-ROS-required static engineering workflow remains the stable v1 baseline:

```txt
plan -> refine -> diff -> validate -> generate
      -> apply-preview -> apply-plan -> apply -> rollback -> history
      -> inspect -> repair-suggest -> report
      -> detect -> inspect-ros1 -> deps
      -> migrate-plan -> migrate-plan-validate -> migrate-plan-diff -> migrate-preview
```

The Python API layer is available for integration work while the CLI remains the primary user interface.

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
