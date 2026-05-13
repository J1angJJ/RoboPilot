# Developer Setup

This guide is for contributors who want to run RoboPilot locally from source.

## Supported Python Versions

Use Python 3.10 or 3.11 for development and release checks.

Package metadata declares:

```txt
>=3.10,<3.12
```

Python 3.12 is not claimed because it was not available for this release validation pass. Python 3.13 is not currently claimed as supported because the CLI test suite has known Typer compatibility issues there.

## Clone the Repository

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
```

## Create an Environment

Using `venv`:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Using conda:

```bash
conda create -n robopilot python=3.10 -y
conda activate robopilot
```

## Install Editable Package

```bash
python -m pip install -U pip
pip install -e ".[dev]"
```

Optional LLM support is installed separately:

```bash
pip install -e ".[llm]"
```

The default RoboPilot workflow remains offline and rule-based. LLM features require explicit configuration and must not be required for normal tests.

## Run Tests

```bash
python -m pytest
```

Windows fallback:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

Run JSON contract tests:

```bash
python -m pytest tests/test_json_contracts.py
```

## Run CLI Help

```bash
robopilot --help
robopilot detect --help
robopilot migrate-plan --help
robopilot migrate-scaffold-validate --help
robopilot migrate-scaffold-report --help
```

## Try the Python API

The CLI remains the main user interface, but integration code can call the lightweight API layer directly:

```python
from robopilot.api.static_analysis import detect_project_type

result = detect_project_type("examples/generated_projects/demo_detector")
print(result["project_type"])
```

API functions are designed to avoid Rich rendering and direct stdout printing.

## VSCode Extension Development

The extension is a thin wrapper around the RoboPilot CLI JSON outputs:

```bash
cd vscode-extension
npm install
npm run compile
npm test
```

Then launch an Extension Development Host from VSCode. The extension requires the `robopilot` CLI to be installed or configured with `robopilot.executablePath`.

For local VSIX packaging:

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

The package command creates a local `.vsix` for installation testing. It does not publish to the VSCode Marketplace.

Marketplace publishing preparation is documented in `docs/vscode_marketplace.md`. Publishing requires a confirmed Marketplace publisher id and a `VSCE_PAT` secret; do not run publishing workflows during normal development.

## Packaging Checks

For local package verification:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

Do not commit files from `dist/`, `build/`, or `*.egg-info`.
