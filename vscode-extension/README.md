# RoboPilot

RoboPilot is a lightweight VSCode extension for the RoboPilot no-ROS-required static engineering toolchain for ROS-style projects.

The extension wraps the installed `robopilot` CLI, consumes documented JSON outputs where available, and shows results in VSCode. It does not reimplement RoboPilot logic in TypeScript. The Python CLI remains the source of truth.

## Requirements

- RoboPilot CLI installed and available on PATH, or configured with `robopilot.executablePath`.
- No ROS or ROS2 installation is required.

Install RoboPilot:

```bash
pip install robopilot
```

For local development from this repository:

```bash
pip install -e ".[dev]"
```

## Development

```bash
cd vscode-extension
npm install
npm run compile
npm test
```

Open this folder in VSCode and run the extension in an Extension Development Host.

## Settings

- `robopilot.executablePath`: path to the RoboPilot CLI executable. Default: `robopilot`.
- `robopilot.outputDirectory`: directory for extension-generated migration plans, scaffold files, and reports. Default: `.robopilot_vscode`.

## Commands

- RoboPilot: Detect Workspace
- RoboPilot: Inspect ROS1 Package
- RoboPilot: Analyze Dependencies
- RoboPilot: Generate Migration Plan
- RoboPilot: Preview Migration
- RoboPilot: Preview Migration Scaffold
- RoboPilot: Generate Migration Scaffold
- RoboPilot: Validate Migration Scaffold
- RoboPilot: Generate Scaffold Report
- RoboPilot: Open Scaffold Report
- RoboPilot: Validate ProjectSpec
- RoboPilot: Show Output

## Local VSIX Packaging

This repository supports local VSIX generation for testing. Local packaging does not publish a new VSCode Marketplace version.

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

The package command runs the VSCode prepublish compile step and creates a `.vsix` file in this directory.

Install a local VSIX with:

```bash
code --install-extension robopilot-vscode-0.5.0.vsix
```

Uninstall with:

```bash
code --uninstall-extension j1angjj.robopilot-vscode
```

## Marketplace

The extension is available from Visual Studio Marketplace as:

```txt
j1angjj.robopilot-vscode
```

Install it with:

```bash
code --install-extension j1angjj.robopilot-vscode
```

The `publisher` field is `j1angjj`; future Marketplace updates must keep that publisher id aligned with the Visual Studio Marketplace publisher.

See `docs/vscode_marketplace.md` in the repository root for the listing, token safety guidance, and future update workflow notes.

## Troubleshooting

- If `robopilot` is not found, install the CLI with `pip install robopilot` or configure `robopilot.executablePath`.
- If a conda environment is not visible to VSCode, start VSCode from the activated environment or configure an absolute executable path.
- If scaffold generation reports existing output conflicts, review `.robopilot_vscode/ros2_scaffold` or choose a different `robopilot.outputDirectory`.
- If a report is missing, run `RoboPilot: Generate Scaffold Report` before `RoboPilot: Open Scaffold Report`.

## Safety

The extension calls static RoboPilot commands. It does not run ROS, ROS2, catkin, colcon, launch files, generated nodes, or external APIs.

Migration workflow commands write only to the configured extension output directory. The scaffold report command writes `.robopilot_vscode/scaffold_report.md` by default.

The migration scaffold workflow is not a full automatic ROS1-to-ROS2 migration. Manual review is still required for source code, QoS, parameters, dependencies, interfaces, launch behavior, build system details, and runtime validation.
