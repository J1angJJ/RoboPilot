
# AGENTS.md

## Project Goal

RoboPilot is an AI-native robotics development assistant for ROS-style workflows, ProjectSpec planning and refinement, debugging, workflow visualization, project inspection, safe repair suggestions, and static project reports.

The project explores how lightweight AI-assisted developer tools can help robotics learners and developers plan, validate, generate, inspect, and debug robotics software projects without requiring a full ROS2 runtime environment.

RoboPilot should grow as a real developer tool, not as a one-time demo script.

## Current Architecture

RoboPilot currently follows a spec-first workflow:

```txt
natural language task
        ↓
ProjectSpec
        ↓
validate spec
        ↓
generate ROS-style package
        ↓
inspect generated or existing project
```

The central design principle is:

```txt
LLM or rule-based planner should produce or refine ProjectSpec.
RoboPilot should validate ProjectSpec.
RoboPilot should deterministically generate, inspect, suggest repairs, and export reports for project files.
```

Do not bypass the `ProjectSpec` workflow when adding generation-related features.

## Current Capabilities

RoboPilot currently supports:

1. Offline ROS-style project generation.
2. Prompt-driven template selection.
3. Structured `ProjectSpec` generation.
4. Spec validation.
5. Generation from `robopilot.yaml`.
6. Robotics error log debugging.
7. Mermaid workflow graph generation.
8. Static generated examples.
9. Project inspection for generated and ROS-style projects.
10. Project repair suggestions based on inspection issues.
11. Static Markdown project reports.
12. Planner interface with offline rule-based planning and optional OpenAI-backed ProjectSpec-only LLM planning.
13. Rule-based and optional LLM-assisted ProjectSpec refinement.
14. Static ProjectSpec diff reports.
15. Read-only apply preview.
16. Read-only apply plan export.
17. Safe apply from plan with dry-run default and backups.
18. Safe rollback from RoboPilot backup directories.
19. English and Chinese documentation.
20. Pytest test coverage and GitHub Actions CI.

## Current Priority

The current priority is:

```txt
v0.15.0 Apply Rollback
```

The goal is to safely restore files from a RoboPilot backup directory with dry-run as the default.

Expected command:

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

The rollback layer should:

- dry-run by default
- require `--confirm` before restoring files
- require the project path to exist
- require the backup path to exist and be a directory
- require the backup to be inside `.robopilot_backups`
- refuse unsafe relative paths and path traversal
- restore only files contained in the selected backup
- preserve relative paths
- not delete newly created files in this version

The optional LLM planner must not run ROS2, launch files, colcon, or generated Python nodes. It must not modify files or generate arbitrary code directly.

## Important Constraints

- Do NOT require a real ROS2 installation.
- Do NOT require a GPU.
- Do NOT require Docker.
- Do NOT run heavy model training.
- Do NOT execute generated ROS nodes.
- Do NOT execute launch files.
- Do NOT run `colcon build`.
- Do NOT call OpenAI API or any LLM API unless the task explicitly asks for a future optional LLM mode.
- Do NOT add LangChain, Streamlit, Gradio, RAG, VSCode extension, or large frameworks unless explicitly requested.
- Prefer pure Python implementations.
- Keep the project lightweight and easy to clone, install, test, and understand.
- Generated code may be ROS2-style pseudocode if real ROS2 runtime support is not available.

## Development Philosophy

RoboPilot should feel like a real developer tool.

Prioritize:

- clear architecture
- stable `ProjectSpec` workflow
- deterministic behavior
- safe file operations
- testable modules
- readable generated files
- useful CLI output
- concise documentation
- minimal dependencies
- backward compatibility with existing commands

Avoid:

- overengineering
- unnecessary multi-agent architecture
- heavy framework lock-in
- unstable LLM-only behavior
- features that require unavailable hardware or runtime environments
- changing public CLI behavior without updating tests and documentation
- duplicating validation logic instead of reusing existing modules

## Recommended Tech Stack

- Python 3.10+
- Typer for CLI
- Rich for terminal output
- Pytest for tests
- pathlib for file operations
- built-in serialization helpers for RoboPilot's limited YAML schema

Optional future dependencies:

- OpenAI SDK for optional LLM-powered planning
- Streamlit or Gradio for optional lightweight UI
- Mermaid for workflow visualization
- Ruff or Black for formatting

Do not add optional dependencies unless they are required for the current task.

## Code Style

- Use type hints.
- Prefer `pathlib.Path` over `os.path`.
- Keep functions small and focused.
- Separate CLI code from business logic.
- Separate templates from file-writing logic.
- Reuse existing spec loader and validator where possible.
- Use clear function and variable names.
- Add docstrings for public functions.
- Avoid hidden side effects.
- Avoid global mutable state.
- Keep output deterministic for tests.

## Expected Core Package Structure

Current and expected package structure:

```txt
src/robopilot/
├─ __init__.py
├─ main.py
├─ generator/
│  ├─ __init__.py
│  ├─ project_generator.py
│  ├─ project_spec.py
│  ├─ task_classifier.py
│  ├─ template_registry.py
│  └─ templates.py
├─ spec/
│  ├─ __init__.py
│  ├─ io.py
│  └─ validator.py
├─ debugger/
│  ├─ __init__.py
│  └─ log_analyzer.py
├─ graph/
│  ├─ __init__.py
│  └─ mermaid_generator.py
├─ inspector/
│  ├─ __init__.py
│  └─ project_inspector.py
└─ utils/
   └─ file_ops.py
```

Documentation and examples:

```txt
docs/
├─ architecture.md
├─ demo_script.md
└─ screenshots/

examples/
├─ prompts/
├─ error_logs/
├─ pipelines/
├─ graphs/
└─ generated_projects/

tests/
```

If a directory does not exist yet, create it only when needed by the current task.

## Safety Rules

- Never delete user files automatically.
- Never overwrite existing files unless explicitly allowed.
- When overwriting is necessary, create a backup or require an explicit overwrite flag.
- Generated projects should be written to `outputs/` by default.
- Do not commit generated temporary outputs from `outputs/`.
- Never commit API keys, tokens, private paths, local environment files, or logs.
- Never assume the user has ROS2 installed.
- Never require external services for offline MVP features.
- Static inspection must not execute user code.

## Existing CLI Commands

The following commands should remain supported:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
```

```bash
robopilot validate --spec robopilot.yaml
```

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

```bash
robopilot diff --old robopilot.yaml --new refined.yaml
```

```bash
robopilot generate --spec robopilot.yaml
```

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

```bash
robopilot debug --text "ModuleNotFoundError: No module named 'cv_bridge'"
```

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

```bash
robopilot inspect examples/generated_projects/demo_detector
```

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
```

```bash
robopilot report examples/generated_projects/demo_detector --output report.md
```

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
```

```bash
robopilot diff --old base.yaml --new refined.yaml
```

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
```

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
```

```bash
robopilot apply --plan apply_plan.yaml --confirm
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

## ProjectSpec Rules

`ProjectSpec` is the central intermediate representation.

Generation-related features should flow through `ProjectSpec`.

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

Validation logic should live in the spec validation module and should be reused by other modules such as generator and inspector.

## Testing

Before finalizing a change, run:

```bash
pytest
```

On Windows, if pytest cannot access the default temporary directory, run:

```bash
pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

For CLI-related changes, also run relevant commands manually.

For generator-related changes, test:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

For spec-related changes, test:

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output .pytest_tmp/robopilot.yaml
```

```bash
robopilot validate --spec .pytest_tmp/robopilot.yaml
```

```bash
robopilot generate --spec .pytest_tmp/robopilot.yaml --output-root .pytest_tmp/spec_generated --overwrite
```

For inspector-related changes, test:

```bash
robopilot inspect examples/generated_projects/demo_detector
```

For repair-suggest-related changes, test:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
```

For report-related changes, test:

```bash
robopilot report examples/generated_projects/demo_detector --output .pytest_tmp/demo_report.md
```

For planner-related changes, test:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
```

## Preferred Development Workflow

1. Read `README.md`, `README.zh-CN.md`, `roadmap.md`, `CHANGELOG.md`, `pyproject.toml`, and this file first.
2. Understand the existing architecture before editing.
3. Implement one small feature at a time.
4. Reuse existing modules instead of duplicating logic.
5. Add or update tests.
6. Run tests.
7. Run relevant CLI commands manually.
8. Update README and demo docs when behavior changes.
9. Update `CHANGELOG.md` under `Unreleased`.
10. Summarize changed files, design decisions, and test results.

## Current Implementation Target

Implement:

```txt
v0.15.0 Apply Rollback
```

The planner layer should continue to support:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
```

Spec refinement should be supported:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

Spec diff should be supported:

```bash
robopilot diff --old base.yaml --new refined.yaml
```

The diff implementation should include:

- validation before comparison
- changed scalar fields
- added and removed nodes
- added and removed topics
- added and removed config files, launch files, and notes
- readable terminal output and stable JSON output
- no file modification

The optional LLM refiner should include:

- provider-backed structured ProjectSpec output only
- reuse of existing provider configuration and OpenAI client logic
- reuse of existing ProjectSpec parsing and validation
- clear missing-configuration errors
- no direct file or code generation

The apply preview implementation should include:

- in-memory rendering of expected deterministic project files
- comparison against an existing project directory
- create/update/keep/conflict classification
- readable terminal output and stable JSON output
- no file modification and no `--apply`

The apply plan implementation should include:

- reuse of apply-preview classification logic
- deterministic YAML-like and JSON serialization
- validation of required apply plan fields
- no target project modification and no real apply execution

The apply implementation should include:

- dry-run default
- explicit `--confirm` for writes
- stale plan rejection
- conflict rejection
- backup creation before updating existing files
- strict create/update/keep/conflict boundaries

The rollback implementation should include:

- dry-run default
- explicit `--confirm` for restores
- project and backup path validation
- `.robopilot_backups` location checks
- unsafe relative path and path traversal protection
- restore-only behavior for files contained in the backup
- no deletion of newly created files
- readable terminal output and stable JSON output

Do not start broad LLM orchestration, direct LLM code generation, RAG, Streamlit UI, VSCode integration, real ROS2 runtime execution, `--apply`, automatic unconfirmed apply, or colcon integration until the spec-first workflow is stable.
