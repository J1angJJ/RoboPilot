# AGENTS.md

## Project Goal

RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects.

It helps robotics learners and developers plan, refine, validate, generate, inspect, update, roll back, document, analyze, and migrate ROS/ROS2-style project structure without requiring a local ROS installation.

RoboPilot should grow as a practical developer toolchain, not as a general-purpose coding agent and not as a runtime ROS automation tool.

## Product Positioning

RoboPilot intentionally works without:

- ROS installation
- ROS2 installation
- catkin workspace
- colcon workspace
- robot hardware
- simulator runtime
- launch execution
- generated node execution

The core value is static engineering support:

```txt
spec-first project planning
static project inspection
safe project updates
dependency and structure analysis
ROS1 / ROS2 migration assistance
optional LLM-assisted ProjectSpec workflows
```

RoboPilot should avoid competing directly with general-purpose coding agents. Its niche is ROS-style project structure, no-ROS-required static analysis, safe update planning, dependency analysis, migration assistance, and beginner-friendly robotics engineering workflows.

## Current Stable Baseline

The current stable baseline is:

```txt
v1.13.0
```

The stable baseline includes:

- no-ROS-required default behavior
- ProjectSpec-based generation
- read-only detect / inspect / deps / report workflows
- dry-run-first apply / rollback workflows
- project-local history journal
- ROS project detection
- ROS1 static inspection
- ROS2 static inspection
- static dependency analysis
- ROS1-to-ROS2 migration planning
- migration plan validation and diff
- migration preview
- optional LLM planner / refiner boundaries

Do not break the v1.0.0 command surface or documented safety model unless the task explicitly asks for a planned compatibility change.

## Current Priority

The current priority is:

```txt
v1.14.0 Examples / Tutorials / Demo Pack
```

The goal is to make the no-ROS-required ROS engineering and ROS1-to-ROS2 migration scaffold workflows easier to learn and demonstrate.

This milestone should focus on:

- static ROS1 migration demo package
- representative ROS2 scaffold demo
- sample migration plan and scaffold report artifacts
- concise CLI and VSCode tutorials
- presentation-friendly demo walkthrough
- README and workflow links into the examples
- no ROS, ROS2, catkin, colcon, launch execution, generated code execution, or generated module imports

This milestone must not add new product commands, change Python migration logic, publish to the VSCode Marketplace, add migration apply, automatic source conversion, automatic colcon execution, ROS runtime execution, or launch execution.

## Near-term Direction

After v1.10.0, the recommended direction is:

```txt
v1.10.0 Migration Scaffold Report
v1.11.0 VSCode Extension Migration Workflow Polish
v1.12.0 VSCode Extension VSIX Packaging
v1.13.0 VSCode Marketplace Publish Preparation
v1.14.0 Examples / Tutorials / Demo Pack
v1.15.0 Migration Workflow UX Polish
v1.16.0 Stability / Compatibility / Cleanup
v2.0.0-rc.1
v2.0.0
```

The VSCode extension should be a thin beginner-friendly interface over the CLI / API layer. It should not duplicate RoboPilot core logic.

RoboPilot should treat v2.0.0 as a stage-completion milestone for the mature v1.x toolchain, not as an excuse for risky expansion. Unless explicitly planned otherwise, v2.0.0 is not intended to be a breaking rewrite.

Before v2.0.0, do not pursue full automatic ROS1-to-ROS2 migration, migration apply, automatic source code conversion, automatic ROS/ROS2 execution, automatic `colcon` execution, or launch execution. Focus on making the existing static migration assistant workflow usable, documented, beginner-friendly, and VSCode-accessible.

## Important Constraints

- Do not require a real ROS installation.
- Do not require a real ROS2 installation.
- Do not require a GPU.
- Do not require Docker.
- Do not run heavy model training.
- Do not execute generated ROS nodes.
- Do not execute launch files.
- Do not run `catkin_make`.
- Do not run `colcon build`.
- Do not call OpenAI API or any LLM API unless the task explicitly involves optional LLM planning or refinement.
- Do not add LangChain, Streamlit, Gradio, RAG, VSCode extension, or large frameworks unless explicitly requested.
- Do not introduce new product commands during packaging / release-engineering work.
- Prefer pure Python implementations.
- Keep the project lightweight and easy to clone, install, test, publish, and understand.
- Static analysis must not execute user code.

## PyPI and Packaging Rules

For packaging-related work:

- Prefer PyPI Trusted Publishing over long-lived API tokens.
- Do not commit PyPI tokens.
- Do not commit TestPyPI tokens.
- Do not commit `.pypirc`.
- Do not commit build artifacts from `dist/`.
- Do not commit wheel or sdist files unless explicitly requested.
- Use standard packaging tools such as `build` and `twine` for local checks.
- Keep package metadata accurate and conservative.
- Keep `pyproject.toml` as the source of package metadata.
- Ensure the `robopilot` console script remains available.
- Ensure default installation does not require optional LLM dependencies.
- Optional LLM dependencies should remain under an extra such as `llm`.

Suggested packaging checks:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

If GitHub Actions publishing is added, it should use a dedicated workflow such as:

```txt
.github/workflows/publish.yml
```

If Trusted Publishing is used, the PyPI pending publisher should match:

```txt
Owner: J1angJJ
Repository: RoboPilot
Workflow: publish.yml
Environment: pypi
Project name: robopilot
```

## Open-source Project Rules

For public developer experience work, prefer adding or updating:

- `CONTRIBUTING.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `docs/pypi_publish.md`
- `docs/developer_setup.md`

Keep these documents concise and practical.

Do not overpromise community processes that are not actually maintained yet.

## API Layer Direction

The API layer should make RoboPilot easier to integrate with VSCode, scripts, and future UI tools.

Preferred direction:

```txt
src/robopilot/api/
├─ __init__.py
├─ project.py
├─ static_analysis.py
├─ migration.py
├─ apply.py
└─ models.py
```

The API layer should:

- avoid Rich rendering
- avoid direct stdout printing
- avoid `sys.exit`
- return dataclasses, typed results, or stable dictionaries
- expose predictable exceptions or result objects
- keep file-writing explicit
- reuse existing core modules
- allow CLI to remain a presentation layer

The CLI should eventually become:

```txt
CLI command
    ↓
API function
    ↓
core module
    ↓
result object
    ↓
CLI renderer
```

Do not perform a broad API refactor during packaging work unless explicitly requested.

## VSCode Extension Direction

A future VSCode extension should be beginner-friendly but thin.

Preferred first approach:

```txt
VSCode extension
    ↓
spawn robopilot CLI with --json
    ↓
parse JSON
    ↓
display TreeView / Webview / OutputChannel
```

The extension should not reimplement RoboPilot logic in TypeScript.

Possible VSCode MVP commands:

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
- RoboPilot: Open Report

VSCode work should continue to wrap the RoboPilot CLI/API instead of reimplementing core logic in TypeScript.

## Development Philosophy

Prioritize:

- clear architecture
- stable `ProjectSpec` workflow
- no-ROS-required usage
- deterministic behavior
- safe file operations
- dry-run-first workflows
- backup and rollback support
- auditable project updates
- testable modules
- readable generated files
- useful CLI output
- concise documentation
- minimal dependencies
- backward compatibility with v1.0.0 commands
- public package quality
- beginner-friendly installation and usage

Avoid:

- overengineering
- unnecessary multi-agent architecture
- heavy framework lock-in
- unstable LLM-only behavior
- direct LLM code generation
- direct LLM file modification
- features that require unavailable hardware or runtime environments
- changing public CLI behavior without updating tests and documentation
- duplicating validation, rendering, or preview logic instead of reusing existing modules
- putting core logic inside VSCode or UI code

## Recommended Tech Stack

- Python 3.10+
- Typer for CLI
- Rich for terminal output
- Pytest for tests
- pathlib for file operations
- standard Python packaging via `pyproject.toml`
- GitHub Actions for CI / publishing
- built-in serialization helpers for RoboPilot's limited YAML-like schemas

Optional dependencies:

- OpenAI SDK for optional LLM-powered planning/refinement

Do not add optional dependencies unless they are required for the current task.

## Code Style

- Use type hints.
- Prefer `pathlib.Path` over `os.path`.
- Keep functions small and focused.
- Separate CLI code from business logic.
- Separate templates from file-writing logic.
- Reuse existing spec loader and validator where possible.
- Reuse existing apply-preview and rendering logic where possible.
- Reuse existing apply-plan validation where possible.
- Use clear function and variable names.
- Add docstrings for public functions.
- Avoid hidden side effects.
- Avoid global mutable state.
- Keep output deterministic for tests.
- Keep JSON output keys stable once introduced.

## Markdown Style

Markdown files should be readable in raw form and render cleanly on GitHub.

Use:

- normal line breaks
- fenced code blocks
- clear headings
- short paragraphs
- relative links to docs
- concise examples

Avoid:

- extremely long single-line Markdown sections
- dense README content that should live in `docs/`
- duplicated command documentation across many files
- outdated roadmap promises

## Safety Rules

- Never delete user files automatically.
- Never overwrite existing files unless explicitly allowed.
- Default behavior for file-writing operations should be dry-run when practical.
- Confirmed file-writing operations must require explicit flags such as `--confirm`.
- Generated projects should be written to `outputs/` by default.
- Do not commit generated temporary outputs from `outputs/`.
- Never commit API keys, tokens, private paths, local environment files, logs, backups, local history artifacts, or package build artifacts.
- Never assume the user has ROS or ROS2 installed.
- Never require external services for default offline features.
- Apply must only write files listed in a validated apply plan.
- Rollback must only restore files from a RoboPilot backup.
- History writing must only write RoboPilot metadata under `.robopilot_history/`.

## Existing CLI Commands

The following commands should remain supported:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
```

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

```bash
robopilot diff --old robopilot.yaml --new refined.yaml
```

```bash
robopilot validate --spec refined.yaml
```

```bash
robopilot generate --spec refined.yaml
```

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
```

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
```

```bash
robopilot apply-plan-validate --plan apply_plan.yaml
```

```bash
robopilot apply --plan apply_plan.yaml
```

```bash
robopilot apply --plan apply_plan.yaml --confirm
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

```bash
robopilot history --project outputs/demo_detector
```

```bash
robopilot detect outputs/demo_detector
```

```bash
robopilot inspect-ros1 path/to/ros1_package
```

```bash
robopilot deps path/to/project
```

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

```bash
robopilot migrate-plan-validate --plan migration_plan.yaml
```

```bash
robopilot migrate-plan-diff --old migration_plan_v1.yaml --new migration_plan_v2.yaml
```

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

```bash
robopilot migrate-scaffold-preview --plan migration_plan.yaml
```

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
```

```bash
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
```

```bash
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
```

```bash
robopilot inspect outputs/demo_detector
```

```bash
robopilot repair-suggest outputs/demo_detector
```

```bash
robopilot report outputs/demo_detector --output report.md
```

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

## ProjectSpec Rules

`ProjectSpec` is the central intermediate representation.

Generation, refinement, and apply-related features should flow through `ProjectSpec` or through validated plans derived from `ProjectSpec`.

A valid spec should include at least:

- package name
- original task
- selected template
- nodes
- topics or topic-like fields when applicable
- config files
- launch files
- generator name
- notes

Generated projects should include a `robopilot.yaml` file.

`robopilot.yaml` should be usable as input for:

```bash
robopilot generate --spec robopilot.yaml
```

## LLM Rules

LLM features are optional.

The default workflow must remain offline.

LLM components may:

- generate ProjectSpec
- refine ProjectSpec
- explain reports in future versions

LLM components must not:

- directly write project files
- directly generate arbitrary source files
- execute commands
- bypass validation
- bypass diff review
- bypass apply-preview or apply-plan
- modify files without explicit apply workflow

Expected safe LLM path:

```txt
LLM output
    ↓
ProjectSpec
    ↓
validate
    ↓
diff / preview
    ↓
deterministic generation or apply
```

## Testing

Before finalizing a change, run:

```bash
python -m pytest
```

On Windows, if pytest cannot access the default temporary directory, run:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

For packaging-related work, also run:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

For CLI polish, manually verify:

```bash
robopilot --help
robopilot plan --help
robopilot migrate-plan --help
robopilot apply --help
robopilot detect --help
robopilot deps --help
```

## Preferred Development Workflow

1. Read `README.md`, `README.zh-CN.md`, `roadmap.md`, `CHANGELOG.md`, `pyproject.toml`, and this file first.
2. Understand the existing architecture before editing.
3. Implement one small change at a time.
4. Reuse existing modules instead of duplicating logic.
5. Add or update tests.
6. Run tests.
7. Run relevant CLI commands manually.
8. Update README and docs when behavior changes.
9. Update `CHANGELOG.md` under `Unreleased`.
10. Summarize changed files, design decisions, and test results.

## Current Implementation Target

Implement:

```txt
v1.14.0 Examples / Tutorials / Demo Pack
```

This milestone should add static examples and tutorials for the existing no-ROS-required migration scaffold review loop.

Suggested implementation items:

```txt
examples/ros1_migration_demo/
examples/ros2_scaffold_demo/
examples/migration_outputs/
docs/tutorial_ros1_to_ros2_migration.md
docs/tutorial_vscode_migration_workflow.md
docs/demo_walkthrough.md
```

Do not add ROS runtime behavior, ROS2 runtime behavior, catkin/colcon execution, migration apply, automatic source conversion, actual VSCode Marketplace publishing, real tokens, or new LLM behavior during this milestone unless explicitly requested.
