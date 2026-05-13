# Testing RoboPilot

RoboPilot's default test suite is designed to run without ROS, ROS2, catkin, colcon, simulator runtimes, robot hardware, network access, or API keys.

## Supported Python Versions

Run the supported release test suite on Python 3.10 and 3.11.

Package metadata declares:

```txt
>=3.10,<3.12
```

Python 3.12 is not part of the supported matrix until the full suite is run there. Python 3.13 is not part of the supported matrix until the Typer / CLI compatibility issues are resolved and the full suite passes there.

## Install Dev Dependencies

From the repository root:

```bash
python -m pip install -U pip
pip install -e ".[dev]"
```

Optional LLM provider dependencies are not required for the default tests. Install `.[llm]` only when manually testing real provider integration.

## Run the Full Test Suite

```bash
python -m pytest
```

On Windows, if pytest cannot access the default temporary directory, use the project-local temp workaround:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## Run Selected Tests

Run one file:

```bash
python -m pytest tests/test_project_detector.py
```

Run tests matching a name:

```bash
python -m pytest -k migration
```

Run one test:

```bash
python -m pytest tests/test_dependency_analyzer.py::test_detects_python_imports
python -m pytest tests/test_dependency_analyzer.py::test_ros1_rospy_usage_produces_migration_hint_toward_rclpy
```

## Manual Verification

Before release-oriented changes, manually check representative CLI help and static workflows:

```bash
robopilot --help
robopilot detect --help
robopilot migrate-plan --help
robopilot apply --help
robopilot history --help
```

Useful smoke checks:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output .pytest_tmp/base_spec.yaml
robopilot validate --spec .pytest_tmp/base_spec.yaml
robopilot generate --spec .pytest_tmp/base_spec.yaml --output-root .pytest_tmp/generated --overwrite
robopilot inspect .pytest_tmp/generated/demo_detector
```

Static ROS-style checks:

```bash
robopilot detect examples/generated_projects/demo_detector
robopilot deps examples/generated_projects/demo_detector
```

Migration scaffold validation smoke checks can be run after generating a temporary migration scaffold:

```bash
robopilot migrate-scaffold-validate --plan .pytest_tmp/migration_plan.yaml --scaffold .pytest_tmp/ros2_scaffold
robopilot migrate-scaffold-validate --plan .pytest_tmp/migration_plan.yaml --scaffold .pytest_tmp/ros2_scaffold --json
robopilot migrate-scaffold-report --plan .pytest_tmp/migration_plan.yaml --scaffold .pytest_tmp/ros2_scaffold
robopilot migrate-scaffold-report --plan .pytest_tmp/migration_plan.yaml --scaffold .pytest_tmp/ros2_scaffold --output .pytest_tmp/scaffold_report.md
```

## Packaging Checks

For packaging or release-readiness changes, run:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

These checks do not publish anything. They only verify that the local source distribution and wheel can be built and rendered cleanly.

For VSCode extension packaging changes, run:

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

The VSIX package command is a local packaging check only. It must not publish to the VSCode Marketplace.

Marketplace preparation checks should stop at compile, tests, and local package generation unless a release task explicitly requests publishing. Do not run `vsce publish` during normal test passes.

## Expected Test Behavior

- Tests should create temporary files only under pytest-managed temp directories or `.pytest_tmp`.
- Tests should not require ROS, ROS2, catkin, colcon, launch execution, or generated node execution.
- Tests should not import user project modules.
- Tests should not require network access.
- Tests should not require `OPENAI_API_KEY`.
- Optional LLM tests should use fake clients or mocked provider responses by default.
- Real provider checks should be explicit manual checks, not part of the default CI suite.

## CI Expectations

The GitHub Actions test workflow should install the package in editable mode with dev dependencies and run:

```bash
pytest
```

Local Windows runs may use:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```
