# RoboPilot VSCode Extension

This is a lightweight VSCode extension for RoboPilot. It wraps the installed `robopilot` CLI and consumes documented JSON outputs.

The extension does not reimplement RoboPilot logic in TypeScript. The Python CLI remains the source of truth.

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

This repository supports local VSIX generation for testing. It does not publish to the VSCode Marketplace.

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
code --install-extension robopilot-vscode-0.4.0.vsix
```

Uninstall with:

```bash
code --uninstall-extension j1angjj.robopilot-vscode
```

## Marketplace Preparation

Marketplace publishing is prepared but not performed. The `publisher` field is currently `j1angjj`; confirm that it matches the Visual Studio Marketplace publisher id before any public release.

See `docs/vscode_marketplace.md` in the repository root for the publishing checklist, token safety guidance, and manual workflow notes.

## Safety

The extension calls static RoboPilot commands. It does not run ROS, ROS2, catkin, colcon, launch files, generated nodes, or external APIs.

Migration workflow commands write only to the configured extension output directory. The scaffold report command writes `.robopilot_vscode/scaffold_report.md` by default.
