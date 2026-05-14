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
v1.16.0
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
- migration scaffold preview / generate / validate / report workflow
- examples, tutorials, demo pack, and migration workflow UX polish
- Chinese documentation expansion and encoding guardrails
- optional LLM planner / refiner boundaries

Do not break the v1.0.0 command surface or documented safety model unless the task explicitly asks for a planned compatibility change.

## Current Priority

The current priority is:

```txt
v1.17.0 VSCode Marketplace Publish
```

The goal is to finalize Marketplace readiness for the RoboPilot VSCode extension and publish only through an explicit, manually confirmed path.

This milestone should focus on:

- confirming `vscode-extension/package.json` metadata
- confirming publisher id `j1angjj`
- confirming extension id `j1angjj.robopilot-vscode`
- updating extension README and CHANGELOG for Marketplace readiness
- keeping `.github/workflows/vscode-publish.yml` manual-only
- using `VSCE_PAT` only from GitHub Secrets
- documenting install, update, verification, and failure recovery steps
- no committed secrets or hardcoded PAT values
- no product behavior changes unless required for listing quality

This milestone must not add product features, Python CLI commands, migration apply, automatic source conversion, ROS runtime execution, ROS2 runtime execution, automatic colcon execution, launch execution, new LLM behavior, or broad VSCode UI changes.

## Near-term Direction

After v1.15.0, the final pre-v2.0 direction is:

```txt
v1.17.0 VSCode Marketplace Publish
v1.18.0 Stability / Compatibility / Cleanup
v2.0.0-rc.1
v2.0.0
```

The VSCode extension should be a thin beginner-friendly interface over the CLI / API layer. It should not duplicate RoboPilot core logic.

RoboPilot should treat v2.0.0 as a stage-completion milestone for the mature v1.x toolchain, not as an excuse for risky expansion. Unless explicitly planned otherwise, v2.0.0 is not intended to be a breaking rewrite.

Before v2.0.0, do not pursue full automatic ROS1-to-ROS2 migration, migration apply, automatic source code conversion, automatic source patching, automatic ROS/ROS2 execution, `catkin_make`, `colcon`, launch execution, generated node execution, new LLM agent behavior, or complex Webview UI. Focus on Chinese documentation, Marketplace publishing, final stability cleanup, and release readiness for the existing static migration assistant workflow.

v2.0.0 should represent:

- PyPI-distributed CLI
- Python API layer
- documented JSON contracts
- optional VSCode extension
- English and Chinese documentation
- examples, tutorials, and demo pack
- static ROS1 / ROS2 inspection
- dependency analysis
- ROS1-to-ROS2 migration planning
- migration scaffold preview / generate / validate / report workflow
- no-ROS-required safety model

If no breaking changes are introduced, v2.0.0 should be described as a stage-completion release, not a breaking rewrite.

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

Chinese documentation rules:

- Chinese Markdown must be UTF-8 without BOM.
- Do not use GBK, ANSI, or UTF-8 with BOM.
- Avoid wholesale rewrites for encoding-only changes.
- Prefer minimal patches.
- Use `python -m pytest tests/test_docs_encoding.py` to verify Chinese documentation encoding.

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
v1.17.0 VSCode Marketplace Publish
```

This milestone should finalize Marketplace readiness for the RoboPilot VSCode extension, while publishing only through an explicitly confirmed manual path.

Suggested implementation items:

```txt
vscode-extension/package.json
vscode-extension/README.md
vscode-extension/CHANGELOG.md
docs/vscode_marketplace.md
docs/zh-CN/vscode_marketplace.md
.github/workflows/vscode-publish.yml
README.md
README.zh-CN.md
```

Do not add ROS runtime behavior, ROS2 runtime behavior, catkin/colcon execution, migration apply, automatic source conversion, real tokens, new Python CLI commands, Python migration logic changes, broad VSCode product features, or new LLM behavior during this milestone. Do not publish to Marketplace unless explicitly confirmed.
