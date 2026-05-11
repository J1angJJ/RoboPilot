# Testing RoboPilot

RoboPilot's default test suite is designed to run without ROS, ROS2, catkin, colcon, simulator runtimes, robot hardware, network access, or API keys.

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
