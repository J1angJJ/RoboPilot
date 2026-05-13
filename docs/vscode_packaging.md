# VSCode Extension Packaging

This document describes local VSIX packaging for the RoboPilot VSCode extension.

The packaging flow is for local testing only. It does not publish to the VSCode Marketplace.

## Requirements

- Node.js 20
- npm
- RoboPilot CLI installed for runtime testing

Install the CLI:

```bash
pip install robopilot
```

For local repository development:

```bash
pip install -e ".[dev]"
```

## Build And Package

From the repository root:

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

The package command runs `vsce package`. The `vscode:prepublish` script runs `npm run compile` so the compiled `out/` files are refreshed before packaging.

Expected output:

```txt
vscode-extension/robopilot-vscode-<version>.vsix
```

## Local Install

Install the local VSIX:

```bash
code --install-extension robopilot-vscode-0.4.0.vsix
```

Uninstall if needed:

```bash
code --uninstall-extension j1angjj.robopilot-vscode
```

If the `code` command is not available, install it from VSCode's command palette with `Shell Command: Install 'code' command in PATH`, or install the VSIX through the Extensions view.

## Configuration

If VSCode cannot find the RoboPilot CLI, configure:

```txt
robopilot.executablePath
```

For conda users, VSCode may not inherit the activated terminal PATH. In that case, point `robopilot.executablePath` to the full executable path inside the conda environment.

The extension writes integration outputs under:

```txt
.robopilot_vscode
```

Delete that directory manually if stale migration plans, scaffold directories, or reports confuse a local test.

## Troubleshooting

- `robopilot not found`: install RoboPilot or set `robopilot.executablePath`.
- Conda CLI not visible in VSCode: use an absolute path to the environment's `robopilot` executable.
- Stale scaffold conflicts: review and remove `.robopilot_vscode/ros2_scaffold` or choose a different output directory.
- Package version mismatch: run `npm install`, `npm run compile`, and `npm run package` again after changing `package.json`.
- Missing compiled files: ensure `npm run compile` succeeds before packaging.

## Marketplace Boundary

The extension package metadata includes a `publisher` value for local VSIX packaging. Marketplace publishing requires confirming that this value matches the Visual Studio Marketplace publisher id.

See [VSCode Marketplace Publishing](vscode_marketplace.md) for the future publishing checklist. Do not publish to the Marketplace unless a release task explicitly asks for it.
