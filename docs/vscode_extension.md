# VSCode Extension

RoboPilot includes a lightweight VSCode extension under `vscode-extension/`.

The extension is a thin UI layer over the RoboPilot CLI. It does not reimplement RoboPilot logic in TypeScript, does not require ROS, and does not execute ROS launch files, generated nodes, catkin, or colcon.

## Requirements

Install the RoboPilot CLI:

```bash
pip install robopilot
```

For local repository development:

```bash
pip install -e ".[dev]"
```

If `robopilot` is not on PATH, configure:

```txt
robopilot.executablePath
```

## Settings

- `robopilot.executablePath`: path to the RoboPilot CLI executable. Default: `robopilot`.
- `robopilot.outputDirectory`: directory for extension-generated migration plans and reports. Default: `.robopilot_vscode`.

## Commands

- `RoboPilot: Detect Workspace`
- `RoboPilot: Inspect ROS1 Package`
- `RoboPilot: Analyze Dependencies`
- `RoboPilot: Generate Migration Plan`
- `RoboPilot: Preview Migration`
- `RoboPilot: Preview Migration Scaffold`
- `RoboPilot: Generate Migration Scaffold`
- `RoboPilot: Validate Migration Scaffold`
- `RoboPilot: Generate Scaffold Report`
- `RoboPilot: Open Scaffold Report`
- `RoboPilot: Validate ProjectSpec`
- `RoboPilot: Show Output`

The extension calls documented CLI JSON commands where available and renders summaries in a RoboPilot OutputChannel and a small Explorer TreeView.

## Migration Scaffold Workflow

The extension uses `robopilot.outputDirectory` for generated integration files. The default is:

```txt
.robopilot_vscode
```

The migration scaffold workflow uses these paths:

- `.robopilot_vscode/migration_plan.json`
- `.robopilot_vscode/ros2_scaffold/`
- `.robopilot_vscode/scaffold_report.md`

Typical command order:

```txt
RoboPilot: Generate Migration Plan
  -> RoboPilot: Preview Migration Scaffold
  -> RoboPilot: Generate Migration Scaffold
  -> RoboPilot: Validate Migration Scaffold
  -> RoboPilot: Generate Scaffold Report
  -> RoboPilot: Open Scaffold Report
```

The scaffold preview, generation, and validation commands consume RoboPilot CLI JSON output. `Generate Scaffold Report` writes a Markdown report and displays the report path; it does not rely on Rich terminal formatting.

`Generate Migration Scaffold` writes only under the configured extension output directory and does not pass `--overwrite` by default. If the scaffold directory already contains conflicting files, the extension shows the RoboPilot failure and asks the user to review the output directory.

For a step-by-step tutorial, see [Tutorial: VSCode-Assisted Migration Scaffold Workflow](tutorial_vscode_migration_workflow.md).

## Safety Model

The extension is static by default:

- It does not require ROS or ROS2.
- It does not run `catkin_make` or `colcon`.
- It does not execute launch files.
- It does not execute generated nodes.
- It does not call OpenAI or external APIs.
- It does not modify source project files.

`RoboPilot: Generate Migration Plan` writes only a migration plan JSON file to the configured extension output directory.
`RoboPilot: Generate Migration Scaffold` writes only conservative scaffold placeholders to the configured extension output directory.
`RoboPilot: Generate Scaffold Report` writes only `.robopilot_vscode/scaffold_report.md` unless the output directory setting changes.

## Run Locally

```bash
cd vscode-extension
npm install
npm run compile
npm test
```

Open the repository in VSCode, open the Run and Debug view, and start an Extension Development Host using the extension entry point.

## Local VSIX Packaging

The extension can be packaged locally as a VSIX for testing:

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

Install the generated VSIX locally with:

```bash
code --install-extension robopilot-vscode-0.4.0.vsix
```

See [VSCode Extension Packaging](vscode_packaging.md) for troubleshooting and uninstall steps.

## Marketplace Status

Local VSIX packaging is available for installation testing. Marketplace publishing preparation is documented in [VSCode Marketplace Publishing](vscode_marketplace.md).

The extension is not guaranteed to be listed on the Visual Studio Marketplace until it is explicitly published. The current `publisher` value is `j1angjj`; confirm that it matches the Marketplace publisher id before publishing.
