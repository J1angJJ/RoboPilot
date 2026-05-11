# RoboPilot VSCode Extension MVP

This is a lightweight VSCode extension MVP for RoboPilot. It wraps the installed `robopilot` CLI and consumes documented JSON outputs.

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

## Safety

The extension calls static RoboPilot commands. It does not run ROS, ROS2, catkin, colcon, launch files, generated nodes, or external APIs.

The migration plan command writes only to the configured extension output directory.
