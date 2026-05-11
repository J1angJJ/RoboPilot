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

## Current Architecture

RoboPilot follows a spec-first and safety-first workflow:

```txt
natural language task
  -> planner
  -> ProjectSpec
  -> refine
  -> diff
  -> validate
  -> generate / apply-preview
  -> apply-plan
  -> apply
  -> rollback
  -> history
  -> inspect / repair-suggest / report
```

The central design principle:

```txt
LLM or rule-based planner/refiner may produce or refine ProjectSpec.
RoboPilot validates ProjectSpec.
RoboPilot deterministically renders files.
RoboPilot previews changes before writing.
RoboPilot writes only through validated plans.
RoboPilot backs up before updating.
RoboPilot supports rollback from backups.
```

Do not bypass the `ProjectSpec` workflow when adding planning, refinement, generation, apply, or migration-related features.

## Current Capabilities

RoboPilot currently supports:

1. Offline ROS-style project generation.
2. Prompt-driven template selection.
3. Structured `ProjectSpec` generation.
4. Spec validation.
5. Generation from `robopilot.yaml`.
6. Spec refinement.
7. LLM-assisted spec refinement.
8. Spec diff.
9. Apply preview.
10. Apply plan export.
11. Apply plan validation.
12. Safe apply from plan.
13. Rollback from RoboPilot backups.
14. Project-local apply/rollback history.
15. Static project inspection.
16. Read-only repair suggestions.
17. Markdown project report export.
18. Robotics error log debugging.
19. Mermaid workflow graph generation.
20. Optional LLM planner and refiner.
21. English and Chinese documentation.
22. ROS project detection without requiring ROS.
23. ROS1 static inspection without requiring ROS.
24. Dependency analysis without requiring ROS.
25. ROS1-to-ROS2 static migration planning.
26. Migration plan validation and diff.
27. Migration apply preview.
28. Release-readiness documentation for testing, compatibility, limitations, stability policy, and release process.
29. Pytest test coverage and GitHub Actions CI.

## Current Priority

The current priority is:

```txt
v1.0.0-rc.1 Release Candidate Checklist
```

The goal is to prepare RoboPilot v1.0.0-rc.1 by auditing versioning, documentation, stability boundaries, limitations, compatibility, tests, and CLI help.

Expected work:

- maintain `docs/testing.md`
- maintain `docs/release_process.md`
- maintain `docs/compatibility.md`
- maintain `docs/known_limitations.md`
- maintain `docs/stability_policy.md`
- keep README links, `docs/v1_scope.md`, `CHANGELOG.md`, and `roadmap.md` current
- keep `pyproject.toml` on the valid Python package version `1.0.0rc1` for the RC

Do not implement new CLI commands, migration file generation, migration apply, ROS runtime execution, ROS2 runtime execution, catkin/colcon execution, RAG, Streamlit, Gradio, VSCode extension, robot integration, or new LLM behavior for this milestone.

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
- Prefer pure Python implementations.
- Keep the project lightweight and easy to clone, install, test, and understand.
- Static analysis must not execute user code.

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
- backward compatibility with existing commands

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

## Recommended Tech Stack

- Python 3.10+
- Typer for CLI
- Rich for terminal output
- Pytest for tests
- pathlib for file operations
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

## Safety Rules

- Never delete user files automatically.
- Never overwrite existing files unless explicitly allowed.
- Default behavior for file-writing operations should be dry-run when practical.
- Confirmed file-writing operations must require explicit flags such as `--confirm`.
- Generated projects should be written to `outputs/` by default.
- Do not commit generated temporary outputs from `outputs/`.
- Never commit API keys, tokens, private paths, local environment files, logs, backups, or local history artifacts.
- Never assume the user has ROS or ROS2 installed.
- Never require external services for default offline features.
- Apply must only write files listed in a validated apply plan.
- Rollback must only restore files from a RoboPilot backup.
- History writing must only write RoboPilot metadata under `.robopilot_history/`.

## Existing CLI Commands

The following commands should remain supported:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
robopilot validate --spec refined.yaml
robopilot generate --spec refined.yaml
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
robopilot history --project outputs/demo_detector
robopilot detect outputs/demo_detector
robopilot inspect-ros1 path/to/ros1_package
robopilot deps path/to/project
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-plan-diff --old migration_plan_v1.yaml --new migration_plan_v2.yaml
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
robopilot inspect outputs/demo_detector
robopilot repair-suggest outputs/demo_detector
robopilot report outputs/demo_detector --output report.md
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
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

Generated projects should include a `robopilot.yaml` file. `robopilot.yaml` should be usable as input for `robopilot generate --spec robopilot.yaml`.

## LLM Rules

LLM features are optional. The default workflow must remain offline.

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
  -> ProjectSpec
  -> validate
  -> diff / preview
  -> deterministic generation or apply
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
v1.0.0-rc.1 Release Candidate Checklist
```

This milestone should finalize release-candidate readiness through documentation and version consistency checks. It must not add new product capabilities, new commands, or change public CLI behavior.
