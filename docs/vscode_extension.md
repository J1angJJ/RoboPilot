# VSCode Extension MVP

RoboPilot includes a lightweight VSCode extension MVP under `vscode-extension/`.

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
- `RoboPilot: Validate ProjectSpec`
- `RoboPilot: Show Output`

The extension calls documented CLI JSON commands where available and renders summaries in a RoboPilot OutputChannel and a small Explorer TreeView.

## Safety Model

The extension is static by default:

- It does not require ROS or ROS2.
- It does not run `catkin_make` or `colcon`.
- It does not execute launch files.
- It does not execute generated nodes.
- It does not call OpenAI or external APIs.
- It does not modify source project files.

`RoboPilot: Generate Migration Plan` writes only a migration plan JSON file to the configured extension output directory.

## Run Locally

```bash
cd vscode-extension
npm install
npm run compile
npm test
```

Open the repository in VSCode, open the Run and Debug view, and start an Extension Development Host using the extension entry point.

## Packaging Later

This milestone does not publish the extension to the VSCode Marketplace.

A later packaging flow may use `@vscode/vsce` to create a VSIX:

```bash
cd vscode-extension
npm install
npm run compile
npx @vscode/vsce package
```

Do not publish a VSIX until the release process and Marketplace metadata are reviewed.
