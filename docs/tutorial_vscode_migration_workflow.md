# Tutorial: VSCode-Assisted Migration Scaffold Workflow

The RoboPilot VSCode extension is a thin UI wrapper over the RoboPilot CLI and JSON contracts. It helps run the migration scaffold review loop from the Command Palette while keeping the same no-ROS-required safety model.

## Prerequisites

Install the RoboPilot CLI:

```bash
pip install robopilot
```

For source development:

```bash
python -m pip install -e ".[dev]"
```

Install or launch the local RoboPilot extension as described in [VSCode Extension](vscode_extension.md) and [VSCode Packaging](vscode_packaging.md).

If VSCode cannot find `robopilot`, configure:

```txt
robopilot.executablePath
```

For a conda environment on Windows, this may need to point at the environment's `robopilot.exe` or a wrapper script that activates the environment.

## Open a Workspace

Open this repository or the demo package in VSCode:

```txt
examples/ros1_migration_demo/
```

The extension writes integration artifacts under:

```txt
.robopilot_vscode/
```

by default. You can change this with `robopilot.outputDirectory`.

## Command Palette Workflow

Run these commands from the VSCode Command Palette:

```txt
RoboPilot: Detect Workspace
RoboPilot: Generate Migration Plan
RoboPilot: Preview Migration Scaffold
RoboPilot: Generate Migration Scaffold
RoboPilot: Validate Migration Scaffold
RoboPilot: Generate Scaffold Report
RoboPilot: Open Scaffold Report
```

The expected artifact loop is:

```txt
.robopilot_vscode/migration_plan.json
  -> .robopilot_vscode/ros2_scaffold/
  -> .robopilot_vscode/scaffold_report.md
```

The OutputChannel remains the main UI. It reports target style, files to create, generated files, validation status, issues, warnings, and report path.

## Safety Model

The extension does not reimplement migration logic in TypeScript. It calls the RoboPilot CLI with safe argument arrays and consumes CLI JSON or Markdown outputs.

The workflow does not run ROS, ROS2, `catkin_make`, `colcon`, launch files, or generated nodes.

## Troubleshooting

`robopilot` command not found:

- Install RoboPilot in the Python environment visible to VSCode.
- Set `robopilot.executablePath` to the full CLI path.

Conda environment PATH is not visible to VSCode:

- Start VSCode from an activated conda shell, or set `robopilot.executablePath`.
- On Windows, verify the path in the same terminal VSCode uses.

Stale `.robopilot_vscode` output:

- Review or remove old generated artifacts before rerunning scaffold generation.
- RoboPilot refuses scaffold overwrites by default.

Existing scaffold conflicts:

- Generate into a fresh output directory or manually clear only the intended demo output.
- Do not delete source project files to resolve scaffold conflicts.

Report missing:

- Run `RoboPilot: Generate Scaffold Report` before `RoboPilot: Open Scaffold Report`.
