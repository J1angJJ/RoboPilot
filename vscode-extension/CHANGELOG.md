# Changelog

All notable changes to the RoboPilot VSCode extension are documented here.

## 0.4.0

- Prepared Visual Studio Marketplace publishing metadata and documentation.
- Documented that `publisher` is currently `j1angjj` and must match the Marketplace publisher id before publishing.
- Added safety guidance for manual publishing, GitHub Actions publishing, PAT handling, and rollback considerations.
- No Marketplace publishing was performed.

## 0.3.0

- Added local VSIX packaging support with project-local `@vscode/vsce`.
- Added `npm run package` and `vscode:prepublish` compile behavior.
- Added `.vscodeignore` and local VSIX install/uninstall documentation.

## 0.2.0

- Added VSCode commands for the migration scaffold review workflow.
- Added migration scaffold preview, generation, validation, report generation, and report opening commands.
- Improved OutputChannel and TreeView summaries while keeping RoboPilot CLI JSON contracts as the source of truth.

## 0.1.0

- Added the initial RoboPilot VSCode extension MVP.
- Wrapped RoboPilot CLI commands for workspace detection, ROS1 inspection, dependency analysis, migration planning, migration preview, ProjectSpec validation, and output display.
- Added a lightweight Explorer TreeView and OutputChannel integration.
